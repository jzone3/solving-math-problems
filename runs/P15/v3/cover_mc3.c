/* cover_mc3: sampled-candidate weighted min-conflicts (breakout) engine.
 * Same search state/energy as cover_mc.c, engineered for N ~ 2e8:
 *   - candidate residues proposed from a SAMPLE of the hole list (exact when
 *     nh <= sample size, i.e. the whole endgame), so a move never scans all
 *     holes nor all residues of a modulus;
 *   - chosen candidate then evaluated EXACTLY by one strided class scan
 *     (gain: sum of hole weights in the class; lose: sum of weights of
 *     uniquely covered elements of the vacated class), both OpenMP-parallel;
 *   - cnt as uint16 (half the memory traffic of int), w/gain as float;
 *   - greedy init without divisions (rolling residue counter), parallel.
 *
 * Usage: cover_mc3 N m secs seed out.json [sample]
 * Prints "SOLVED size=..." and writes JSON witness on success.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#include <omp.h>

static long N;
static int m;
static uint16_t *cnt;    /* coverage multiplicity, size N */
static float *w;         /* hole weights, size N */
static long *mods;       /* divisors >= m */
static int nmods;
static long *res;        /* residue per modulus */
static float *gain;      /* sparse scratch, size max modulus (touched only) */
static int32_t *touched; /* residues touched this move */
static int32_t *rbuf;    /* scratch: hole residues this move */

static unsigned long long rng_s = 88172645463325252ULL;
static inline unsigned long long xrand(void) {
    rng_s ^= rng_s << 13; rng_s ^= rng_s >> 7; rng_s ^= rng_s << 17;
    return rng_s;
}
static inline double frand(void) { return (xrand() >> 11) * (1.0 / 9007199254740992.0); }

static int cmp_long(const void *a, const void *b) {
    long x = *(const long *)a, y = *(const long *)b;
    return x < y ? -1 : x > y;
}

static double now(void) {
    struct timespec ts; clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + 1e-9 * ts.tv_nsec;
}

int main(int argc, char **argv) {
    if (argc < 6) { fprintf(stderr, "usage: %s N m secs seed out.json\n", argv[0]); return 2; }
    N = atol(argv[1]); m = atoi(argv[2]);
    double budget = atof(argv[3]);
    rng_s += (unsigned long long)atoll(argv[4]) * 2654435761ULL;
    const char *outpath = argv[5];
    long SAMPLE = argc > 6 ? atol(argv[6]) : 16384;
    const char *warmpath = argc > 8 ? argv[8] : NULL;

    long *divs = malloc(sizeof(long) * 20000);
    nmods = 0;
    for (long d = 2; d * d <= N; d++) if (N % d == 0) {
        if (d >= m) divs[nmods++] = d;
        if (N / d != d && N / d >= m) divs[nmods++] = N / d;
    }
    divs[nmods++] = N; /* d=1 pair */
    qsort(divs, nmods, sizeof(long), cmp_long);
    /* dedupe */
    int nm2 = 0;
    for (int i = 0; i < nmods; i++) if (nm2 == 0 || divs[nm2-1] != divs[i]) divs[nm2++] = divs[i];
    nmods = nm2;
    mods = divs;
    long maxmod = mods[nmods - 1];

    cnt = calloc(N, sizeof(uint16_t));
    w = malloc(sizeof(float) * N);
    for (long t = 0; t < N; t++) w[t] = 1.0f;
    res = malloc(sizeof(long) * nmods);
    gain = calloc(maxmod, sizeof(float));
    touched = malloc(sizeof(int32_t) * (N + 1));
    rbuf = malloc(sizeof(int32_t) * N);

    int nthreads = omp_get_max_threads();
    fprintf(stderr, "nmods=%d maxmod=%ld threads=%d\n", nmods, maxmod, nthreads);

    /* hole list with positions for O(1) add/remove (maintained from init on) */
    int32_t *hl = malloc(sizeof(int32_t) * N);
    int32_t *hpos = malloc(sizeof(int32_t) * N);
    long nh = 0;

    /* greedy init, smallest mods first. Two regimes:
     *  n <= HCAP: rolling-residue histogram scan of Z_N (no divisions);
     *  n >  HCAP: histogram over the current hole list only (small by then). */
    double tg0 = now();
    if (warmpath) {
        /* warm start: load residues from a state dump instead of greedy */
        FILE *sf = fopen(warmpath, "r");
        if (!sf) { perror("warm state"); return 2; }
        long wN; int wm, wnm; long wbest;
        if (fscanf(sf, "%ld %d %d %ld", &wN, &wm, &wnm, &wbest) != 4 ||
            wN != N || wnm != nmods) { fprintf(stderr, "warm state mismatch\n"); return 2; }
        for (int i = 0; i < nmods; i++) {
            long a, n;
            if (fscanf(sf, "%ld %ld", &a, &n) != 2 || n != mods[i]) { fprintf(stderr, "warm state mods mismatch\n"); return 2; }
            res[i] = a;
        }
        fclose(sf);
        for (int i = 0; i < nmods; i++) {
            long n2 = mods[i], r2 = res[i];
            #pragma omp parallel for schedule(static)
            for (long t = r2; t < N; t += n2) cnt[t]++;
        }
        nh = 0;
        for (long t = 0; t < N; t++) { hpos[t] = -1; if (cnt[t] == 0) { hl[nh] = (int32_t)t; hpos[t] = (int32_t)nh; nh++; } }
        fprintf(stderr, "warm start from %s: holes=%ld\n", warmpath, nh);
    } else {
        const long HCAP = 1L << 21;
        long hist_n = maxmod < HCAP ? maxmod : HCAP;
        long *hist = malloc(sizeof(long) * hist_n);
        long *lhist = malloc(sizeof(long) * hist_n * nthreads);
        int holes_built = 0;
        for (int i = 0; i < nmods; i++) {
            long n = mods[i];
            long bb = 0;
            if (n <= HCAP) {
                #pragma omp parallel
                {
                    int tid = omp_get_thread_num(), nt = omp_get_num_threads();
                    long lo = N * tid / nt, hi = N * (tid + 1) / nt;
                    long *lh = lhist + (long)tid * hist_n;
                    memset(lh, 0, sizeof(long) * n);
                    long r = lo % n;
                    for (long t = lo; t < hi; t++) {
                        if (cnt[t] == 0) lh[r]++;
                        if (++r == n) r = 0;
                    }
                }
                for (long b = 0; b < n; b++) {
                    long s = 0;
                    for (int tid = 0; tid < nthreads; tid++) s += lhist[(long)tid * hist_n + b];
                    hist[b] = s;
                }
                for (long b = 1; b < n; b++) if (hist[b] > hist[bb]) bb = b;
                res[i] = bb;
                #pragma omp parallel for schedule(static)
                for (long t = bb; t < N; t += n) cnt[t]++;
            } else {
                if (!holes_built) {
                    nh = 0;
                    for (long t = 0; t < N; t++) { hpos[t] = -1; if (cnt[t] == 0) { hl[nh] = (int32_t)t; hpos[t] = (int32_t)nh; nh++; } }
                    holes_built = 1;
                    fprintf(stderr, "greedy switch to hole-list at n=%ld, holes=%ld t=%.1fs\n", n, nh, now() - tg0);
                }
                long ntouch = 0;
                #pragma omp parallel for schedule(static)
                for (long k = 0; k < nh; k++) rbuf[k] = (int32_t)(hl[k] % n);
                for (long k = 0; k < nh; k++) {
                    int32_t r = rbuf[k];
                    if (gain[r] == 0.0f) touched[ntouch++] = r;
                    gain[r] += 1.0f;
                }
                float gbest = -1.0f;
                for (long k = 0; k < ntouch; k++)
                    if (gain[touched[k]] > gbest) { gbest = gain[touched[k]]; bb = touched[k]; }
                for (long k = 0; k < ntouch; k++) gain[touched[k]] = 0.0f;
                if (gbest < 0.0f) bb = 0; /* no holes hit: park at 0 */
                res[i] = bb;
                for (long t = bb; t < N; t += n) {
                    if (cnt[t]++ == 0) {
                        int32_t p = hpos[t], last = hl[--nh];
                        hl[p] = last; hpos[last] = p; hpos[t] = -1;
                    }
                }
            }
        }
        free(hist); free(lhist);
        if (!holes_built) {
            nh = 0;
            for (long t = 0; t < N; t++) { hpos[t] = -1; if (cnt[t] == 0) { hl[nh] = (int32_t)t; hpos[t] = (int32_t)nh; nh++; } }
        }
    }
    long energy = nh;
    fprintf(stderr, "greedy init done: holes=%ld t=%.1fs\n", energy, now() - tg0);

    long best = energy;
    long *best_state = malloc(sizeof(long) * nmods);
    memcpy(best_state, res, sizeof(long) * nmods);

    char statepath[4096];
    snprintf(statepath, sizeof statepath, "%s.state", outpath);
    double tdump = 0.0;

    double t0 = now(), tbest = t0;
    long long it = 0;
    long stall = 0, stall_lim = 4L * nmods;
    double kick_after = argc > 7 ? atof(argv[7]) : 300.0;
    double tlog = t0;
    long long it_log = 0;
    while (energy && now() - t0 < budget) {
        double tn = now();
        if (tn - tlog > 30.0) {
            printf("rate=%.1f it/s energy=%ld t=%.1fs\n", (it - it_log) / (tn - tlog), energy, tn - t0);
            fflush(stdout);
            tlog = tn; it_log = it;
        }
        if (tn - tbest > kick_after) {
            memcpy(res, best_state, sizeof(long) * nmods);
            memset(cnt, 0, sizeof(uint16_t) * N);
            for (int i2 = 0; i2 < nmods; i2++) {
                if (frand() < 8.0 / nmods) res[i2] = (long)(xrand() % mods[i2]);
                long n2 = mods[i2], r2 = res[i2];
                #pragma omp parallel for schedule(static)
                for (long t = r2; t < N; t += n2) cnt[t]++;
            }
            #pragma omp parallel for schedule(static)
            for (long t = 0; t < N; t++) w[t] = 1.0f;
            nh = 0;
            for (long t = 0; t < N; t++) { hpos[t] = -1; if (cnt[t] == 0) { hl[nh] = (int32_t)t; hpos[t] = (int32_t)nh; nh++; } }
            energy = nh;
            tbest = now();
            printf("kick energy=%ld t=%.1fs\n", energy, now() - t0);
            fflush(stdout);
        }
        it++;
        int i = (int)(xrand() % nmods);
        long n = mods[i];
        long a_old = res[i];

        /* propose candidate residues from a hole sample (exact if nh<=SAMPLE) */
        long ntouch = 0;
        long ns = nh <= SAMPLE ? nh : SAMPLE;
        int exact_sample = (ns == nh);
        for (long k = 0; k < ns; k++) {
            long h = exact_sample ? (long)hl[k] : (long)hl[xrand() % nh];
            int32_t r = (int32_t)(h % n);
            if (gain[r] == 0.0f) touched[ntouch++] = r;
            gain[r] += w[h];
        }
        /* pick best sampled candidate (reservoir over ties) */
        long b = a_old;
        {
            double gmax = -1.0; long seen = 0;
            for (long k = 0; k < ntouch; k++) {
                long r = touched[k];
                if (r == a_old) continue;
                double g = gain[r];
                if (g > gmax + 1e-9) { gmax = g; seen = 1; b = r; }
                else if (g >= gmax - 1e-9) { seen++; if (xrand() % seen == 0) b = r; }
            }
        }
        for (long k = 0; k < ntouch; k++) gain[touched[k]] = 0.0f;
        /* random-walk noise only on small classes: an unconditional random
         * reassignment of a small-n modulus (class size N/n ~ 1e7) can blow
         * millions of holes at once, which the 50 it/s original never felt */
        int noise = (N / n <= 65536) && frand() < 0.01;
        if (noise) b = (long)(xrand() % n);

        if (b != a_old && !noise) {
            /* exact evaluation of the chosen move: one class scan each side */
            double lose = 0.0, egain = 0.0;
            #pragma omp parallel for reduction(+:lose) schedule(static) if(N / n > 16384)
            for (long t = a_old; t < N; t += n) if (cnt[t] == 1) lose += w[t];
            #pragma omp parallel for reduction(+:egain) schedule(static) if(N / n > 16384)
            for (long t = b; t < N; t += n) if (cnt[t] == 0) egain += w[t];
            double d = egain - lose;
            int flat = (egain == 0.0 && lose == 0.0);
            /* accept improving moves; zero-delta sideways moves allowed on a
             * flat landscape (mirrors cover_mc.c's random tie behavior) */
            if (!(d > 1e-9 || flat)) b = a_old;
        }

        if (b != a_old) {
            for (long t = a_old; t < N; t += n) {
                if (--cnt[t] == 0) { hl[nh] = (int32_t)t; hpos[t] = (int32_t)nh; nh++; }
            }
            for (long t = b; t < N; t += n) {
                if (cnt[t]++ == 0) {
                    int32_t p = hpos[t], last = hl[--nh];
                    hl[p] = last; hpos[last] = p; hpos[t] = -1;
                }
            }
            res[i] = b;
            energy = nh;
        }
        if (energy < best) {
            best = energy;
            memcpy(best_state, res, sizeof(long) * nmods);
            stall = 0;
            tbest = now();
            printf("best=%ld it=%lld t=%.1fs\n", best, it, now() - t0);
            fflush(stdout);
            if (now() - tdump > 60.0) {
                /* periodic best-state dump for external repair drivers */
                char tmp[4200];
                snprintf(tmp, sizeof tmp, "%s.tmp", statepath);
                FILE *sf = fopen(tmp, "w");
                if (sf) {
                    fprintf(sf, "%ld %d %d %ld\n", N, m, nmods, best);
                    for (int i2 = 0; i2 < nmods; i2++)
                        fprintf(sf, "%ld %ld\n", best_state[i2], mods[i2]);
                    fclose(sf);
                    rename(tmp, statepath);
                }
                tdump = now();
            }
        } else if (++stall >= stall_lim) {
            for (long k = 0; k < nh; k++) w[hl[k]] += 1.0f;
            stall = 0;
        }
    }
    if (energy == 0) {
        char *cov = calloc(N, 1);
        for (int i = 0; i < nmods; i++)
            for (long t = res[i]; t < N; t += mods[i]) cov[t] = 1;
        for (long t = 0; t < N; t++) if (!cov[t]) { fprintf(stderr, "BUG\n"); return 1; }
        printf("SOLVED size=%d t=%.1fs it=%lld\n", nmods, now() - t0, it);
        FILE *f = fopen(outpath, "w");
        fprintf(f, "{\"m\": %d, \"N\": %ld, \"cover\": [", m, N);
        for (int i = 0; i < nmods; i++)
            fprintf(f, "%s[%ld, %ld]", i ? ", " : "", res[i], mods[i]);
        fprintf(f, "]}\n");
        fclose(f);
        return 0;
    }
    printf("NOSOLUTION best=%ld t=%.1fs it=%lld\n", best, now() - t0, it);
    return 1;
}
