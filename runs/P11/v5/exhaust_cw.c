/* Exhaustive search for ICW_d(m, s^2) fixed by a multiplier t on Z_m
 * (d=1 gives the plain CW case).  Exhausts all integer vectors on Z_m,
 * coefficients in [-min(d,s), min(d,s)], constant on orbits of <t>, with
 *     sum a_i = s,  sum a_i^2 = s^2,  all nontrivial autocorrelations 0.
 * Justified by AGZ Theorem 2.4 (d=1, s^2 = prime power, gcd(m,s)=1) or
 * McFarland Theorem 4.1 (contractions), plus the fixed-translate lemma
 * (needs gcd(s,m)=1).
 *
 * Pruning: moment bounds + folding constraints modulo divisors q where the
 * relevant prime is self-conjugate (Lander Thm 2.2 forces the folded image
 * to be s*delta_{j}, at a caller-chosen residue j).
 *
 * Usage: ./exhaust_cw m s d t [fold_spec...]
 *   e.g. ./exhaust_cw 120 7 1 7 8:0 5:0 10:0
 * fold_spec q:j means: folding mod q must equal s at residue j, 0 elsewhere.
 * Prints every solution found and a final count.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXN 256
#define MAXORB 128
#define MAXF 4

static int n, s, k, dmax, tmul;
static int norb;
static int orbsz[MAXORB];
static int orbelts[MAXORB][64];   /* orbit elements */
static int coef[MAXORB];

static int nf;                     /* number of fold constraints */
static int fm[MAXF];               /* modulus */
static int ftarget[MAXF][MAXN];    /* target folded vector */
static int fcur[MAXF][MAXN];       /* current partial folded sums */
static int fcap[MAXF][MAXN];       /* capacity from remaining orbits */
/* per-orbit contribution counts to each fold residue */
static int fcnt[MAXORB][MAXF][MAXN];

static long long nodes = 0, leaves = 0, found = 0;
static int split_k = 1, split_r = 0, split_depth = 4;
static long long split_ctr = 0;

static int a[MAXN];

static void build_orbits(void) {
    int seen[MAXN]; memset(seen, 0, sizeof(seen));
    norb = 0;
    for (int x = 0; x < n; x++) {
        if (seen[x]) continue;
        int y = x, sz = 0;
        while (!seen[y]) { seen[y] = 1; orbelts[norb][sz++] = y; y = (tmul*y) % n; }
        orbsz[norb] = sz;
        norb++;
    }
    /* sort orbits by size descending (index sort) */
    for (int i = 0; i < norb; i++)
        for (int j = i+1; j < norb; j++)
            if (orbsz[j] > orbsz[i]) {
                int tsz = orbsz[i]; orbsz[i] = orbsz[j]; orbsz[j] = tsz;
                int tmp[64]; memcpy(tmp, orbelts[i], sizeof(tmp));
                memcpy(orbelts[i], orbelts[j], sizeof(tmp));
                memcpy(orbelts[j], tmp, sizeof(tmp));
            }
}

static int check_full(void) {
    memset(a, 0, sizeof(a));
    for (int i = 0; i < norb; i++)
        for (int j = 0; j < orbsz[i]; j++)
            a[orbelts[i][j]] += coef[i];
    for (int g = 1; g < n; g++) {
        long long c = 0;
        for (int i = 0; i < n; i++) c += (long long)a[i] * a[(i+g) % n];
        if (c != 0) return 0;
    }
    return 1;
}

static void rec(int i, int rsum, int rsq, int remcap) {
    nodes++;
    if ((nodes & ((1LL<<31)-1)) == 0) {
        fprintf(stderr, "progress: nodes=%lld leaves=%lld found=%lld\n",
                nodes, leaves, found);
    }
    if (i == split_depth && split_k > 1) {
        if ((split_ctr++ % split_k) != split_r) return;
    }
    if (rsq > k) return;
    int need = s - rsum;
    if (need > remcap || -need > remcap) return;
    /* fold feasibility */
    for (int f = 0; f < nf; f++)
        for (int r = 0; r < fm[f]; r++) {
            int diff = ftarget[f][r] - fcur[f][r];
            if (diff > fcap[f][r] || -diff > fcap[f][r]) return;
        }
    if (i == norb) {
        leaves++;
        if (rsum == s && rsq == k && check_full()) {
            found++;
            printf("SOLUTION:");
            for (int j = 0; j < norb; j++)
                if (coef[j]) {
                    printf(" %+d*<%d>%d", coef[j], orbelts[j][0], orbsz[j]);
                }
            printf("\n"); fflush(stdout);
        }
        return;
    }
    int sz = orbsz[i];
    /* remove this orbit's capacity */
    for (int f = 0; f < nf; f++)
        for (int r = 0; r < fm[f]; r++) fcap[f][r] -= dmax * fcnt[i][f][r];
    for (int c = -dmax; c <= dmax; c++) {
        coef[i] = c;
        if (c) for (int f = 0; f < nf; f++)
            for (int r = 0; r < fm[f]; r++) fcur[f][r] += c * fcnt[i][f][r];
        rec(i+1, rsum + c*sz, rsq + c*c*sz, remcap - dmax*sz);
        if (c) for (int f = 0; f < nf; f++)
            for (int r = 0; r < fm[f]; r++) fcur[f][r] -= c * fcnt[i][f][r];
    }
    coef[i] = 0;
    for (int f = 0; f < nf; f++)
        for (int r = 0; r < fm[f]; r++) fcap[f][r] += dmax * fcnt[i][f][r];
}

int main(int argc, char **argv) {
    if (argc < 5) { fprintf(stderr, "usage: %s m s d t [q:j ...]\n", argv[0]); return 2; }
    n = atoi(argv[1]);
    s = atoi(argv[2]);
    k = s * s;
    dmax = atoi(argv[3]);
    if (dmax > s) dmax = s;
    tmul = atoi(argv[4]);
    {
        const char *e;
        if ((e = getenv("SPLIT_K"))) split_k = atoi(e);
        if ((e = getenv("SPLIT_R"))) split_r = atoi(e);
        if ((e = getenv("SPLIT_DEPTH"))) split_depth = atoi(e);
    }
    build_orbits();
    nf = 0;
    for (int i = 5; i < argc; i++) {
        int m, j;
        if (sscanf(argv[i], "%d:%d", &m, &j) != 2 || n % m) { fprintf(stderr, "bad fold %s\n", argv[i]); return 2; }
        fm[nf] = m;
        memset(ftarget[nf], 0, sizeof(ftarget[nf]));
        ftarget[nf][j] = s;
        nf++;
    }
    for (int i = 0; i < norb; i++)
        for (int f = 0; f < nf; f++) {
            memset(fcnt[i][f], 0, sizeof(fcnt[i][f]));
            for (int j = 0; j < orbsz[i]; j++)
                fcnt[i][f][orbelts[i][j] % fm[f]]++;
        }
    int total = 0;
    for (int f = 0; f < nf; f++)
        for (int r = 0; r < fm[f]; r++) {
            fcur[f][r] = 0; fcap[f][r] = 0;
        }
    for (int i = 0; i < norb; i++) {
        total += orbsz[i];
        for (int f = 0; f < nf; f++)
            for (int r = 0; r < fm[f]; r++) fcap[f][r] += dmax * fcnt[i][f][r];
    }
    total *= dmax;
    fprintf(stderr, "m=%d s=%d d=%d t=%d orbits=%d folds=%d split=%d/%d@%d\n",
            n, s, dmax, tmul, norb, nf, split_r, split_k, split_depth);
    rec(0, 0, 0, total);
    printf("m=%d s=%d d=%d t=%d folds=%d split=%d/%d@%d done: solutions=%lld nodes=%lld leaves=%lld\n",
           n, s, dmax, tmul, nf, split_r, split_k, split_depth, found, nodes, leaves);
    return 0;
}
