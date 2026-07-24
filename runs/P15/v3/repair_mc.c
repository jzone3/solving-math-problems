/* repair_mc: hole-driven exact repair phase INSIDE a full cover_mc assignment
 * (the holes_mc idea operating on the full-Z_N state).
 *
 * Reads a state dump from cover_mc3 (out.json.state):
 *   line 1: N m nmods best
 *   lines:  a n   (residue, modulus) for every divisor n >= m of N
 * Frees every modulus with n >= n_min (small residue classes), keeps the
 * rest frozen. The freed moduli must jointly cover
 *   H' = current holes  UNION  elements uniquely covered by freed classes
 * (staying at the old residue re-covers exactly one's own damage, so the
 * reduction is exact: covering H' <=> a full covering system).
 * Residues of a freed modulus are restricted to CANDIDATES = residues of
 * holes in H' plus the old residue (any other residue is dominated).
 * Search: weighted min-conflicts with breakout, as holes_mc.c, but over
 * sparse candidate lists so huge moduli (n up to N) cost O(#holes), never
 * O(n). Init = old residues, i.e. starting energy = #current holes.
 *
 * Usage: repair_mc state_file n_min secs seed out.json
 * On success prints SOLVED, writes the FULL witness JSON, exit 0.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
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
    if (argc < 6) { fprintf(stderr, "usage: %s state_file n_min secs seed out.json\n", argv[0]); return 2; }
    FILE *f = fopen(argv[1], "r");
    if (!f) { perror("state"); return 2; }
    long N; int m, nmods; long dumped_best;
    if (fscanf(f, "%ld %d %d %ld", &N, &m, &nmods, &dumped_best) != 4) return 2;
    long *res = malloc(sizeof(long) * nmods);
    long *mods = malloc(sizeof(long) * nmods);
    for (int i = 0; i < nmods; i++)
        if (fscanf(f, "%ld %ld", &res[i], &mods[i]) != 2) return 2;
    fclose(f);
    long n_min = atol(argv[2]);
    double budget = atof(argv[3]);
    rng_s += (unsigned long long)atoll(argv[4]) * 2654435761ULL;
    const char *outpath = argv[5];

    /* rebuild coverage counts */
    uint16_t *cnt = calloc(N, sizeof(uint16_t));
    for (int i = 0; i < nmods; i++)
        for (long t = res[i]; t < N; t += mods[i]) cnt[t]++;

    /* freed moduli and the hole set H' */
    int *freed = malloc(sizeof(int) * nmods);
    int NM = 0;
    for (int i = 0; i < nmods; i++) if (mods[i] >= n_min) freed[NM++] = i;
    long NH = 0, cap = 1 << 20;
    int64_t *H = malloc(sizeof(int64_t) * cap);
    for (long t = 0; t < N; t++) if (cnt[t] == 0) {
        if (NH == cap) { cap *= 2; H = realloc(H, sizeof(int64_t) * cap); }
        H[NH++] = t;
    }
    long base_holes = NH;
    for (int j = 0; j < NM; j++) {
        int i = freed[j]; long n = mods[i];
        for (long t = res[i]; t < N; t += n) if (cnt[t] == 1) {
            if (NH == cap) { cap *= 2; H = realloc(H, sizeof(int64_t) * cap); }
            H[NH++] = t;
        }
    }
    fprintf(stderr, "N=%ld m=%d freed=%d (n>=%ld) holes=%ld damage=%ld H'=%ld\n",
            N, m, NM, n_min, base_holes, NH - base_holes, NH);

    /* per freed modulus: hash residues of H' to candidate ids, CSR buckets */
    long **cands = malloc(sizeof(long*) * NM);   /* candidate residue values */
    long *ncand = malloc(sizeof(long) * NM);
    int32_t **cidx = malloc(sizeof(int32_t*) * NM); /* hole -> candidate id */
    long **bstart = malloc(sizeof(long*) * NM);
    int32_t **bitems = malloc(sizeof(int32_t*) * NM);
    long *cur = malloc(sizeof(long) * NM);       /* current candidate id */
    long hsz = 1; while (hsz < 4 * (NH + 1)) hsz <<= 1;
    long *hkey = malloc(sizeof(long) * hsz);
    long *hval = malloc(sizeof(long) * hsz);
    for (int j = 0; j < NM; j++) {
        int i = freed[j]; long n = mods[i];
        memset(hkey, -1, sizeof(long) * hsz);
        long nc = 0;
        cidx[j] = malloc(sizeof(int32_t) * NH);
        long *cv = malloc(sizeof(long) * (NH + 1));
        /* seed with the old residue so "stay put" is always available */
        {
            long r = res[i] % n;
            long p = (r * 2654435761UL) & (hsz - 1);
            while (hkey[p] != -1 && hkey[p] != r) p = (p + 1) & (hsz - 1);
            if (hkey[p] == -1) { hkey[p] = r; hval[p] = nc; cv[nc++] = r; }
        }
        for (long k = 0; k < NH; k++) {
            long r = H[k] % n;
            long p = (r * 2654435761UL) & (hsz - 1);
            while (hkey[p] != -1 && hkey[p] != r) p = (p + 1) & (hsz - 1);
            if (hkey[p] == -1) { hkey[p] = r; hval[p] = nc; cv[nc++] = r; }
            cidx[j][k] = (int32_t)hval[p];
        }
        ncand[j] = nc;
        cands[j] = malloc(sizeof(long) * nc);
        memcpy(cands[j], cv, sizeof(long) * nc);
        free(cv);
        /* CSR */
        long *bs = calloc(nc + 1, sizeof(long));
        for (long k = 0; k < NH; k++) bs[cidx[j][k] + 1]++;
        for (long c = 0; c < nc; c++) bs[c + 1] += bs[c];
        int32_t *bi = malloc(sizeof(int32_t) * NH);
        long *fill = calloc(nc, sizeof(long));
        for (long k = 0; k < NH; k++) { long c = cidx[j][k]; bi[bs[c] + fill[c]++] = (int32_t)k; }
        free(fill);
        bstart[j] = bs; bitems[j] = bi;
        cur[j] = 0; /* candidate 0 == old residue */
    }
    free(hkey); free(hval);

    /* coverage multiplicity per hole BY FREED MODULI ONLY (frozen mods cover
     * none of H' by construction: holes have cnt 0, damage has cnt 1 from
     * its own freed class) */
    int *cov = calloc(NH, sizeof(int));
    float *w = malloc(sizeof(float) * NH);
    for (long k = 0; k < NH; k++) w[k] = 1.0f;
    for (int j = 0; j < NM; j++)
        for (long o = bstart[j][cur[j]]; o < bstart[j][cur[j] + 1]; o++) cov[bitems[j][o]]++;
    long energy = 0;
    for (long k = 0; k < NH; k++) if (cov[k] == 0) energy++;
    fprintf(stderr, "start energy=%ld (should equal holes=%ld)\n", energy, base_holes);

    long best = energy;
    long *best_cur = malloc(sizeof(long) * NM);
    memcpy(best_cur, cur, sizeof(long) * NM);
    double *gain = NULL; long gain_sz = 0;

    double t0 = now(), tbest = t0;
    long long it = 0;
    long stall = 0, stall_lim = 8L * NM;
    while (energy && now() - t0 < budget) {
        if (now() - tbest > 120.0) {
            /* kick: restore best, reshuffle a few freed mods, reset weights */
            memcpy(cur, best_cur, sizeof(long) * NM);
            memset(cov, 0, sizeof(int) * NH);
            for (int j = 0; j < NM; j++) {
                if (frand() < 6.0 / NM) cur[j] = (long)(xrand() % ncand[j]);
                for (long o = bstart[j][cur[j]]; o < bstart[j][cur[j] + 1]; o++) cov[bitems[j][o]]++;
            }
            for (long k = 0; k < NH; k++) w[k] = 1.0f;
            energy = 0;
            for (long k = 0; k < NH; k++) if (cov[k] == 0) energy++;
            tbest = now();
            printf("kick energy=%ld t=%.1fs\n", energy, now() - t0);
            fflush(stdout);
        }
        it++;
        int j = (int)(xrand() % NM);
        long nc = ncand[j];
        if (nc > gain_sz) { gain_sz = nc; gain = realloc(gain, sizeof(double) * gain_sz); }
        memset(gain, 0, sizeof(double) * nc);
        for (long k = 0; k < NH; k++) if (cov[k] == 0) gain[cidx[j][k]] += w[k];
        long a_old = cur[j];
        double lose = 0.0;
        for (long o = bstart[j][a_old]; o < bstart[j][a_old + 1]; o++)
            if (cov[bitems[j][o]] == 1) lose += w[bitems[j][o]];
        long b;
        if (frand() < 0.01) b = (long)(xrand() % nc);
        else {
            double dmax = -1e300;
            for (long c = 0; c < nc; c++) {
                double d = (c == a_old) ? 0.0 : gain[c] - lose;
                if (d > dmax) dmax = d;
            }
            long pick = a_old, seen = 0;
            for (long c = 0; c < nc; c++) {
                double d = (c == a_old) ? 0.0 : gain[c] - lose;
                if (d >= dmax - 1e-9) { seen++; if (xrand() % seen == 0) pick = c; }
            }
            b = pick;
        }
        if (b != a_old) {
            for (long o = bstart[j][a_old]; o < bstart[j][a_old + 1]; o++) {
                long k = bitems[j][o];
                if (--cov[k] == 0) energy++;
            }
            for (long o = bstart[j][b]; o < bstart[j][b + 1]; o++) {
                long k = bitems[j][o];
                if (cov[k]++ == 0) energy--;
            }
            cur[j] = b;
        }
        if (energy < best) {
            best = energy;
            memcpy(best_cur, cur, sizeof(long) * NM);
            stall = 0;
            tbest = now();
            printf("best=%ld it=%lld t=%.1fs\n", best, it, now() - t0);
            fflush(stdout);
        } else if (++stall >= stall_lim) {
            for (long k = 0; k < NH; k++) if (cov[k] == 0) w[k] += 1.0f;
            stall = 0;
        }
    }
    if (energy == 0) {
        /* splice freed residues into the full assignment and verify over Z_N */
        for (int j = 0; j < NM; j++) res[freed[j]] = cands[j][cur[j]];
        char *covfull = calloc(N, 1);
        for (int i = 0; i < nmods; i++)
            for (long t = res[i]; t < N; t += mods[i]) covfull[t] = 1;
        for (long t = 0; t < N; t++) if (!covfull[t]) { fprintf(stderr, "BUG: t=%ld uncovered\n", t); return 1; }
        printf("SOLVED size=%d t=%.1fs it=%lld\n", nmods, now() - t0, it);
        FILE *o = fopen(outpath, "w");
        fprintf(o, "{\"m\": %d, \"N\": %ld, \"cover\": [", m, N);
        for (int i = 0; i < nmods; i++)
            fprintf(o, "%s[%ld, %ld]", i ? ", " : "", res[i], mods[i]);
        fprintf(o, "]}\n");
        fclose(o);
        return 0;
    }
    /* write best partial state (cover_mc3 state format) for warm restarts */
    {
        for (int j = 0; j < NM; j++) res[freed[j]] = cands[j][best_cur[j]];
        char sp[4200];
        snprintf(sp, sizeof sp, "%s.state", outpath);
        FILE *o = fopen(sp, "w");
        fprintf(o, "%ld %d %d %ld\n", N, m, nmods, best);
        for (int i = 0; i < nmods; i++) fprintf(o, "%ld %ld\n", res[i], mods[i]);
        fclose(o);
    }
    printf("NOSOLUTION best=%ld t=%.1fs it=%lld\n", best, now() - t0, it);
    return 1;
}
