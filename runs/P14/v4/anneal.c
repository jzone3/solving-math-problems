/* P14 V4: annealing++ local search for balanced ternary designs.
 *
 * State: M[V][B] over {0,1,2}; every row permanently has exactly rho1 ones and
 * rho2 twos (moves swap two entries within a row), so row constraints hold by
 * construction. Energy = w_col * sum_j (colsum_j - K)^2
 *                      + w_pair * sum_{i<k} (P_ik - Lambda)^2
 * with adaptively re-weighted constraint classes (breakout-style: the class
 * that stays violated gets its weight bumped). Moves accepted by Metropolis
 * with geometric cooling + reheats; many restarts (random or supplied seeds
 * from LP-relaxation roundings read from a file).
 *
 * Usage: anneal V B rho1 rho2 K Lambda seed max_iters [startfile]
 * On success writes witness to stdout after the line "SOLVED" and exits 0.
 * Otherwise prints best energy found and exits 1.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

static int V, B, R1, R2, K, LAM;
static int M[32][64];        /* current matrix */
static int best[32][64];
static int cs[64];           /* column sums */
static int P[32][32];        /* pairwise inner products */
static unsigned long long rngs;

static unsigned long long xrand(void) { /* xorshift64* */
    rngs ^= rngs >> 12; rngs ^= rngs << 25; rngs ^= rngs >> 27;
    return rngs * 2685821657736338717ULL;
}
static int rnd(int n) { return (int)(xrand() % (unsigned)n); }
static double rndu(void) { return (xrand() >> 11) * (1.0 / 9007199254740992.0); }

static long long energy(double wc, double wp, long long *ec, long long *ep) {
    long long Ec = 0, Ep = 0;
    for (int j = 0; j < B; j++) { long long d = cs[j] - K; Ec += d * d; }
    for (int i = 0; i < V; i++)
        for (int k = i + 1; k < V; k++) { long long d = P[i][k] - LAM; Ep += d * d; }
    *ec = Ec; *ep = Ep;
    return 0;
}

static void recompute(void) {
    memset(cs, 0, sizeof cs);
    memset(P, 0, sizeof P);
    for (int j = 0; j < B; j++)
        for (int i = 0; i < V; i++) cs[j] += M[i][j];
    for (int i = 0; i < V; i++)
        for (int k = i + 1; k < V; k++) {
            int s = 0;
            for (int j = 0; j < B; j++) s += M[i][j] * M[k][j];
            P[i][k] = P[k][i] = s;
        }
}

static void random_start(void) {
    for (int i = 0; i < V; i++) {
        int vals[64];
        for (int j = 0; j < B; j++) vals[j] = j < R1 ? 1 : (j < R1 + R2 ? 2 : 0);
        for (int j = B - 1; j > 0; j--) { int t = rnd(j + 1); int tmp = vals[j]; vals[j] = vals[t]; vals[t] = tmp; }
        for (int j = 0; j < B; j++) M[i][j] = vals[j];
    }
    recompute();
}

int main(int argc, char **argv) {
    if (argc < 9) { fprintf(stderr, "usage: %s V B rho1 rho2 K Lam seed iters [startfile]\n", argv[0]); return 2; }
    V = atoi(argv[1]); B = atoi(argv[2]); R1 = atoi(argv[3]); R2 = atoi(argv[4]);
    K = atoi(argv[5]); LAM = atoi(argv[6]);
    rngs = strtoull(argv[7], 0, 10) * 6364136223846793005ULL + 1442695040888963407ULL;
    long long iters = atoll(argv[8]);

    if (argc > 9) { /* start matrix file: V lines of B digits */
        FILE *f = fopen(argv[9], "r");
        if (!f) { perror("startfile"); return 2; }
        for (int i = 0; i < V; i++)
            for (int j = 0; j < B; j++) { int c = fgetc(f); while (c=='\n'||c==' '||c=='\r') c = fgetc(f); M[i][j] = c - '0'; }
        fclose(f);
        recompute();
    } else random_start();

    double wc = 1.0, wp = 1.0;
    long long Ec, Ep; energy(wc, wp, &Ec, &Ep);
    double E = wc * Ec + wp * Ep;
    double bestE = 1e18;
    double T = 3.0;
    const double cool = 0.999995;
    long long since_improve = 0;

    for (long long it = 0; it < iters; it++) {
        /* pick row and two columns with different values */
        int i = rnd(V), j1 = rnd(B), j2 = rnd(B);
        int a = M[i][j1], b = M[i][j2];
        if (a == b) { continue; }
        int d = b - a; /* j1 gains d, j2 loses d */
        /* delta for column part */
        long long dc1 = cs[j1] - K, dc2 = cs[j2] - K;
        long long dEc = ((dc1 + d) * (dc1 + d) - dc1 * dc1) + ((dc2 - d) * (dc2 - d) - dc2 * dc2);
        /* delta for pair part: P[i][k] changes by d*(M[k][j1]-M[k][j2]) */
        long long dEp = 0;
        for (int k = 0; k < V; k++) {
            if (k == i) continue;
            int dk = d * (M[k][j1] - M[k][j2]);
            if (!dk) continue;
            long long p = P[i][k] - LAM;
            dEp += (p + dk) * (p + dk) - p * p;
        }
        double dE = wc * dEc + wp * dEp;
        if (dE <= 0 || rndu() < exp(-dE / T)) {
            M[i][j1] = b; M[i][j2] = a;
            cs[j1] += d; cs[j2] -= d;
            for (int k = 0; k < V; k++) {
                if (k == i) continue;
                int dk = d * (M[k][j1] + (j1==j1?0:0) - M[k][j2]);
                /* careful: M[k][*] unchanged by this move (different row) */
                dk = d * (M[k][j1] - M[k][j2]);
                if (dk) { P[i][k] += dk; P[k][i] += dk; }
            }
            Ec += dEc; Ep += dEp;
            E = wc * Ec + wp * Ep;
            if (Ec + Ep == 0) {
                printf("SOLVED\n");
                for (int r = 0; r < V; r++) { for (int c = 0; c < B; c++) putchar('0' + M[r][c]); putchar('\n'); }
                return 0;
            }
            if (Ec * 1.0 * wc + Ep * 1.0 * wp < bestE) {
                bestE = wc * Ec + wp * Ep; since_improve = 0;
                memcpy(best, M, sizeof M);
            }
        }
        since_improve++;
        T *= cool;
        if (T < 0.05) T = 0.05;
        /* adaptive reweighting + reheat when stuck */
        if (since_improve > 2000000) {
            if (Ec > 0 && Ep == 0) wc *= 1.3; else if (Ep > 0 && Ec == 0) wp *= 1.3;
            else { wc = 1.0; wp = 1.0; }
            if (wc > 100 || wp > 100) { wc = wp = 1.0; }
            T = 2.0; since_improve = 0;
            energy(wc, wp, &Ec, &Ep);
        }
    }
    long long fEc, fEp; 
    /* report best raw violation counts */
    memcpy(M, best, sizeof M); recompute(); energy(1,1,&fEc,&fEp);
    printf("BEST col_sq=%lld pair_sq=%lld total=%lld\n", fEc, fEp, fEc + fEp);
    for (int r = 0; r < V; r++) { for (int c = 0; c < B; c++) putchar('0' + M[r][c]); putchar('\n'); }
    return 1;
}
