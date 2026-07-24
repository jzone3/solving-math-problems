/* cover_mc2: optimized weighted min-conflicts (breakout) for covering systems.
 * Same search as cover_mc.c, engineered for N ~ 2e8:
 *   - gain evaluated ONLY at residues actually hit by holes (touched list),
 *     never O(n) scans/memsets over all residues of a modulus;
 *   - hole->residue reduction (h % n) parallelized with OpenMP into a
 *     scratch buffer, then a cheap serial accumulate;
 *   - lose scan over the vacated class parallelized (strided, reduction);
 *   - cnt as uint16 (half the memory traffic of int), w/gain as float;
 *   - greedy init without divisions (rolling residue counter), parallel;
 *   - optional hole-driven repair: with prob P a move targets the residue
 *     class of a random current hole instead of a uniform random modulus
 *     (biases work onto moduli that can actually cover holes).
 *
 * Usage: cover_mc2 N m secs seed out.json [holeprob]
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
    {
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

    double t0 = now(), tbest = t0;
    long long it = 0;
    long stall = 0, stall_lim = 4L * nmods;
    double kick_after = 300.0;
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

        /* gain over holes only: parallel residue reduction, serial accumulate */
        long ntouch = 0;
        {
            long nh_l = nh;
            #pragma omp parallel for schedule(static) if(nh_l > 8192)
            for (long k = 0; k < nh_l; k++) rbuf[k] = (int32_t)(hl[k] % n);
            for (long k = 0; k < nh_l; k++) {
                int32_t r = rbuf[k];
                if (gain[r] == 0.0f) touched[ntouch++] = r;
                gain[r] += w[hl[k]];
            }
        }
        double lose = 0.0;
        #pragma omp parallel for reduction(+:lose) schedule(static) if(N / n > 8192)
        for (long t = a_old; t < N; t += n) if (cnt[t] == 1) lose += w[t];

        long b;
        if (frand() < 0.01) b = (long)(xrand() % n);
        else {
            /* candidates: touched residues plus a_old (delta 0) */
            double dmax = 0.0; /* staying put */
            for (long k = 0; k < ntouch; k++) {
                long r = touched[k];
                if (r == a_old) continue;
                double d = (double)gain[r] - lose;
                if (d > dmax) dmax = d;
            }
            if (dmax <= 0.0 && lose == 0.0) {
                /* flat landscape: every residue ties at delta 0 (as in the
                 * full-residue reservoir of cover_mc.c) — random walk */
                b = (long)(xrand() % n);
            } else {
                long pick = a_old, seen = 1; /* a_old at delta 0 counts if dmax==0 */
                if (dmax > 0.0) { seen = 0; }
                for (long k = 0; k < ntouch; k++) {
                    long r = touched[k];
                    if (r == a_old) continue;
                    double d = (double)gain[r] - lose;
                    if (d >= dmax - 1e-9) { seen++; if (xrand() % seen == 0) pick = r; }
                }
                b = pick;
            }
        }
        /* reset gain sparsely */
        for (long k = 0; k < ntouch; k++) gain[touched[k]] = 0.0f;

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
