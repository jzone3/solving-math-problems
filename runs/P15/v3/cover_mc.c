/* Weighted min-conflicts (breakout) search for covering systems, C engine.
 * State: one residue per divisor n>=m of N. Energy: #uncovered t in Z_N.
 * Move: reassign random modulus to max-weighted-gain residue; on stall,
 * bump weights of current holes (breakout). Greedy init.
 *
 * Usage: cover_mc N m seconds seed out.json
 * Prints "SOLVED size=..." and writes JSON witness on success.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

static long N;
static int m;
static int *cnt;      /* coverage multiplicity, size N */
static double *w;     /* hole weights, size N */
static long *mods;    /* divisors >= m */
static int nmods;
static long *res;     /* residue per modulus */
static double *gain;  /* scratch, size max modulus */

static unsigned long long rng_s = 88172645463325252ULL;
static inline unsigned long long xrand(void) {
    rng_s ^= rng_s << 13; rng_s ^= rng_s >> 7; rng_s ^= rng_s << 17;
    return rng_s;
}
static inline double frand(void) { return (xrand() >> 11) * (1.0 / 9007199254740992.0); }

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
    for (long d = 2; d <= N; d++) if (N % d == 0 && d >= m) divs[nmods++] = d;
    mods = divs;
    cnt = calloc(N, sizeof(int));
    w = malloc(sizeof(double) * N);
    for (long t = 0; t < N; t++) w[t] = 1.0;
    res = malloc(sizeof(long) * nmods);
    long maxmod = mods[nmods - 1];
    gain = malloc(sizeof(double) * maxmod);

    /* greedy init: smallest mods first */
    for (int i = 0; i < nmods; i++) {
        long n = mods[i];
        memset(gain, 0, sizeof(double) * n);
        for (long t = 0; t < N; t++) if (cnt[t] == 0) gain[t % n] += 1.0;
        long bb = 0;
        for (long b = 1; b < n; b++) if (gain[b] > gain[bb]) bb = b;
        res[i] = bb;
        for (long t = bb; t < N; t += n) cnt[t]++;
    }
    long energy = 0;
    for (long t = 0; t < N; t++) if (cnt[t] == 0) energy++;
    long best = energy;
    long *best_state = malloc(sizeof(long) * nmods);
    memcpy(best_state, res, sizeof(long) * nmods);

    /* hole list with positions for O(1) add/remove */
    long *hl = malloc(sizeof(long) * N);   /* hole list */
    long *hpos = malloc(sizeof(long) * N); /* position in hl, or -1 */
    long nh = 0;
    for (long t = 0; t < N; t++) { hpos[t] = -1; if (cnt[t] == 0) { hl[nh] = t; hpos[t] = nh; nh++; } }

    double t0 = now(), tbest = t0;
    long long it = 0;
    long stall = 0, stall_lim = 4L * nmods;
    double kick_after = 300.0;
    while (energy && now() - t0 < budget) {
        if (now() - tbest > kick_after) {
            /* kick: restart from best, reset weights, shake 10% of moduli */
            memcpy(res, best_state, sizeof(long) * nmods);
            memset(cnt, 0, sizeof(int) * N);
            for (int i2 = 0; i2 < nmods; i2++) {
                if (frand() < 0.10) res[i2] = (long)(xrand() % mods[i2]);
                for (long t = res[i2]; t < N; t += mods[i2]) cnt[t]++;
            }
            for (long t = 0; t < N; t++) w[t] = 1.0;
            nh = 0;
            for (long t = 0; t < N; t++) { hpos[t] = -1; if (cnt[t] == 0) { hl[nh] = t; hpos[t] = nh; nh++; } }
            energy = nh;
            tbest = now();
            printf("kick energy=%ld t=%.1fs\n", energy, now() - t0);
            fflush(stdout);
        }
        it++;
        int i = (int)(xrand() % nmods);
        long n = mods[i];
        long a_old = res[i];
        memset(gain, 0, sizeof(double) * n);
        for (long k = 0; k < nh; k++) { long h = hl[k]; gain[h % n] += w[h]; }
        double lose = 0.0;
        for (long t = a_old; t < N; t += n) if (cnt[t] == 1) lose += w[t];
        long b;
        if (frand() < 0.01) b = (long)(xrand() % n);
        else {
            double dmax = -1e300;
            for (long bb2 = 0; bb2 < n; bb2++) {
                double d = (bb2 == a_old) ? 0.0 : gain[bb2] - lose;
                if (d > dmax) dmax = d;
            }
            /* second pass: reservoir-pick among ties */
            long pick = a_old; long seen = 0;
            for (long bb2 = 0; bb2 < n; bb2++) {
                double d = (bb2 == a_old) ? 0.0 : gain[bb2] - lose;
                if (d >= dmax - 1e-9) { seen++; if (xrand() % seen == 0) pick = bb2; }
            }
            b = pick;
        }
        if (b != a_old) {
            for (long t = a_old; t < N; t += n) {
                if (--cnt[t] == 0) { hl[nh] = t; hpos[t] = nh; nh++; }
            }
            for (long t = b; t < N; t += n) {
                if (cnt[t]++ == 0) {
                    long p = hpos[t], last = hl[--nh];
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
            for (long k = 0; k < nh; k++) w[hl[k]] += 1.0;
            stall = 0;
        }
    }
    if (energy == 0) {
        /* verify */
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
