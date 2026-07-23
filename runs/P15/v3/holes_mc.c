/* Weighted min-conflicts over an explicit HOLE SET (layered attack inner engine).
 * Input (text file): line1 "NH NM", line2 NH hole values (mod N implicit),
 * line3 NM modulus values. Assign residue r_n to every modulus; energy =
 * #holes not covered by any (h % n == r_n). Same breakout scheme as cover_mc.
 * Output: on success prints SOLVED and writes "a n" lines to out file; on
 * failure prints NOSOLUTION best=..., and writes best partial assignment.
 *
 * Usage: holes_mc problem.txt seconds seed out.txt [giveup_secs]
 * giveup_secs: also stop if no new best for that long (default: seconds).
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

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
    if (argc < 5) { fprintf(stderr, "usage: %s problem.txt secs seed out.txt\n", argv[0]); return 2; }
    FILE *f = fopen(argv[1], "r");
    long NH, NM;
    if (fscanf(f, "%ld %ld", &NH, &NM) != 2) return 2;
    long long *H = malloc(sizeof(long long) * NH);
    for (long i = 0; i < NH; i++) fscanf(f, "%lld", &H[i]);
    long *M = malloc(sizeof(long) * NM);
    for (long i = 0; i < NM; i++) fscanf(f, "%ld", &M[i]);
    fclose(f);
    double budget = atof(argv[2]);
    rng_s += (unsigned long long)atoll(argv[3]) * 2654435761ULL;
    double giveup = argc > 5 ? atof(argv[5]) : budget;

    /* CSR buckets: for each mod i, holes grouped by residue h%n */
    long **bstart = malloc(sizeof(long*) * NM);   /* bstart[i][r] offset */
    long **bitems = malloc(sizeof(long*) * NM);   /* hole indices */
    int **hres = malloc(sizeof(int*) * NM);       /* hres[i][k] = H[k] % n */
    for (long i = 0; i < NM; i++) {
        long n = M[i];
        long *cnt = calloc(n + 1, sizeof(long));
        hres[i] = malloc(sizeof(int) * NH);
        for (long k = 0; k < NH; k++) { int r = (int)(H[k] % n); hres[i][k] = r; cnt[r + 1]++; }
        for (long r = 0; r < n; r++) cnt[r + 1] += cnt[r];
        bstart[i] = cnt;
        bitems[i] = malloc(sizeof(long) * NH);
        long *fill = calloc(n, sizeof(long));
        for (long k = 0; k < NH; k++) { int r = hres[i][k]; bitems[i][cnt[r] + fill[r]++] = k; }
        free(fill);
    }
    int *cov = calloc(NH, sizeof(int));  /* coverage multiplicity per hole */
    double *w = malloc(sizeof(double) * NH);
    for (long k = 0; k < NH; k++) w[k] = 1.0;
    long *res = malloc(sizeof(long) * NM);
    long maxmod = 0;
    for (long i = 0; i < NM; i++) if (M[i] > maxmod) maxmod = M[i];
    double *gain = malloc(sizeof(double) * maxmod);

    /* greedy init */
    for (long i = 0; i < NM; i++) {
        long n = M[i];
        memset(gain, 0, sizeof(double) * n);
        for (long k = 0; k < NH; k++) if (cov[k] == 0) gain[hres[i][k]] += 1.0;
        long bb = 0;
        for (long r = 1; r < n; r++) if (gain[r] > gain[bb]) bb = r;
        res[i] = bb;
        for (long o = bstart[i][bb]; o < bstart[i][bb + 1]; o++) cov[bitems[i][o]]++;
    }
    long energy = 0;
    for (long k = 0; k < NH; k++) if (cov[k] == 0) energy++;
    long best = energy;
    long *best_state = malloc(sizeof(long) * NM);
    memcpy(best_state, res, sizeof(long) * NM);

    double t0 = now(), tbest = t0;
    long long it = 0;
    long stall = 0, stall_lim = 4 * NM;
    while (energy && now() - t0 < budget && now() - tbest < giveup) {
        it++;
        long i = (long)(xrand() % NM);
        long n = M[i];
        long a_old = res[i];
        memset(gain, 0, sizeof(double) * n);
        for (long k = 0; k < NH; k++) if (cov[k] == 0) gain[hres[i][k]] += w[k];
        double lose = 0.0;
        for (long o = bstart[i][a_old]; o < bstart[i][a_old + 1]; o++)
            if (cov[bitems[i][o]] == 1) lose += w[bitems[i][o]];
        long b;
        if (frand() < 0.01) b = (long)(xrand() % n);
        else {
            double dmax = -1e300;
            for (long r = 0; r < n; r++) {
                double d = (r == a_old) ? 0.0 : gain[r] - lose;
                if (d > dmax) dmax = d;
            }
            long pick = a_old, seen = 0;
            for (long r = 0; r < n; r++) {
                double d = (r == a_old) ? 0.0 : gain[r] - lose;
                if (d >= dmax - 1e-9) { seen++; if (xrand() % seen == 0) pick = r; }
            }
            b = pick;
        }
        if (b != a_old) {
            for (long o = bstart[i][a_old]; o < bstart[i][a_old + 1]; o++) {
                long k = bitems[i][o];
                if (--cov[k] == 0) energy++;
            }
            for (long o = bstart[i][b]; o < bstart[i][b + 1]; o++) {
                long k = bitems[i][o];
                if (cov[k]++ == 0) energy--;
            }
            res[i] = b;
        }
        if (energy < best) {
            best = energy;
            memcpy(best_state, res, sizeof(long) * NM);
            stall = 0;
            tbest = now();
            printf("best=%ld it=%lld t=%.1fs\n", best, it, now() - t0);
            fflush(stdout);
        } else if (++stall >= stall_lim) {
            for (long k = 0; k < NH; k++) if (cov[k] == 0) w[k] += 1.0;
            stall = 0;
        }
    }
    FILE *o = fopen(argv[4], "w");
    long *st = energy == 0 ? res : best_state;
    for (long i = 0; i < NM; i++) fprintf(o, "%ld %ld\n", st[i], M[i]);
    fclose(o);
    if (energy == 0) { printf("SOLVED it=%lld t=%.1fs\n", it, now() - t0); return 0; }
    printf("NOSOLUTION best=%ld t=%.1fs it=%lld\n", best, now() - t0, it);
    return 1;
}
