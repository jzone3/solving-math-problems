/* P09 Bollobas-Nikiforov: abelian Cayley graphs of order 48..64 (round 12).
 *
 * For an abelian group G = Z_{d1} x ... x Z_{dk} (mixed-radix element
 * encoding) and an inverse-closed connection set S (0 not in S), the Cayley
 * graph eigenvalues are exact character sums
 *     lambda_chi = sum_{s in S} cos(2*pi * sum_i c_i s_i / d_i),
 * (real, since S = -S).  We take lambda_1 = |S| (trivial character; graph
 * regular) and lambda_2 = max over nontrivial characters.  omega is exact
 * via bitmask branch-and-bound (n <= 64).  gap = l1^2+l2^2 - 2m(1-1/w);
 * any gap > 1e-7 is a candidate (re-verify with verify.py).
 *
 * Connection sets are sampled uniformly over inverse-closed subsets by
 * including each {s,-s} orbit independently with random probability p per
 * sample.  Involutions (s = -s) are single-element orbits.
 *
 * Usage: ./abelian d1 [d2 ...] -- samples seed
 * Build: gcc -O3 -march=native -o abelian abelian.c -lm
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdint.h>

#define MAXN 64
#define MAXK 6
static int K, D[MAXK], N;
static uint64_t adj[MAXN];

static int best_clique;
static void expand(uint64_t cand, int size) {
    if (!cand) { if (size > best_clique) best_clique = size; return; }
    while (cand) {
        if (size + __builtin_popcountll(cand) <= best_clique) return;
        int v = __builtin_ctzll(cand);
        cand &= cand - 1;
        expand(cand & adj[v], size + 1);
    }
}
static int max_clique(void) {
    best_clique = 1;
    expand((N == 64) ? ~0ull : ((1ull << N) - 1), 0);
    return best_clique;
}

static unsigned long long rs;
static double rnd(void) {
    rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17;
    return (double)(rs >> 11) / 9007199254740992.0;
}

static void decode(int x, int *t) {
    for (int i = 0; i < K; i++) { t[i] = x % D[i]; x /= D[i]; }
}
static int neg(int x) {
    int t[MAXK], y = 0, mul = 1;
    decode(x, t);
    for (int i = 0; i < K; i++) { y += ((D[i] - t[i]) % D[i]) * mul; mul *= D[i]; }
    return y;
}
static int add(int a, int b) {
    int ta[MAXK], tb[MAXK], y = 0, mul = 1;
    decode(a, ta); decode(b, tb);
    for (int i = 0; i < K; i++) { y += ((ta[i] + tb[i]) % D[i]) * mul; mul *= D[i]; }
    return y;
}

int main(int argc, char **argv) {
    int ai = 1;
    K = 0;
    while (ai < argc && strcmp(argv[ai], "--")) {
        D[K++] = atoi(argv[ai++]);
    }
    if (ai >= argc - 2 || K == 0) { fprintf(stderr, "usage: %s d1 [d2 ...] -- samples seed\n", argv[0]); return 1; }
    long samples = atol(argv[ai + 1]);
    rs = strtoull(argv[ai + 2], 0, 10) * 2654435761ull + 88172645463325252ull;
    N = 1;
    for (int i = 0; i < K; i++) N *= D[i];
    if (N > MAXN) { fprintf(stderr, "order %d > %d\n", N, MAXN); return 1; }

    /* orbit representatives {s,-s} */
    int reps[MAXN], nreps = 0, seen[MAXN] = {0};
    for (int x = 1; x < N; x++) {
        if (seen[x]) continue;
        seen[x] = seen[neg(x)] = 1;
        reps[nreps++] = x;
    }
    /* precompute character table cos values: chi[c][x] */
    static double chi[MAXN][MAXN];
    for (int c = 0; c < N; c++) {
        int tc[MAXK];
        decode(c, tc);
        for (int x = 0; x < N; x++) {
            int tx[MAXK];
            decode(x, tx);
            double ph = 0;
            for (int i = 0; i < K; i++) ph += (double)tc[i] * tx[i] / D[i];
            chi[c][x] = cos(2.0 * M_PI * ph);
        }
    }

    long total = 0, evaluated = 0, violations = 0;
    double best_gap = -1e18;
    for (long it = 0; it < samples; it++) {
        double p = 0.15 + 0.7 * rnd();
        int inS[MAXN] = {0};
        int deg = 0;
        for (int i = 0; i < nreps; i++)
            if (rnd() < p) {
                int s = reps[i], ns = neg(s);
                inS[s] = inS[ns] = 1;
            }
        for (int x = 1; x < N; x++) deg += inS[x];
        if (deg < 2 || deg >= N - 1) continue;
        total++;
        /* eigenvalues */
        double l1 = deg, l2 = -1e18;
        for (int c = 1; c < N; c++) {
            double ev = 0;
            for (int x = 1; x < N; x++)
                if (inS[x]) ev += chi[c][x];
            if (ev > l2) l2 = ev;
        }
        long m = (long)N * deg / 2;
        double s2 = l1 * l1 + l2 * l2;
        if (s2 <= (double)m - 1e-6) continue; /* rhs >= m whenever w >= 2 */
        evaluated++;
        /* build adjacency, exact omega */
        memset(adj, 0, sizeof adj);
        for (int a = 0; a < N; a++)
            for (int x = 1; x < N; x++)
                if (inS[x]) {
                    int b = add(a, x);
                    adj[a] |= 1ull << b;
                }
        int w = max_clique();
        double rhs = 2.0 * m * (1.0 - 1.0 / w);
        double gap = s2 - rhs;
        if (gap > best_gap) best_gap = gap;
        if (gap > 1e-7) {
            violations++;
            printf("CANDIDATE N=%d deg=%d w=%d l1=%.6f l2=%.10f gap=%.6e S=", N, deg, w, l1, l2, gap);
            for (int x = 1; x < N; x++) if (inS[x]) printf("%d,", x);
            printf("\n");
            fflush(stdout);
        }
    }
    printf("SUMMARY group=");
    for (int i = 0; i < K; i++) printf("%d%s", D[i], i + 1 < K ? "x" : "");
    printf(" N=%d total=%ld evaluated=%ld violations=%ld best_gap=%.6e\n",
           N, total, evaluated, violations, best_gap);
    return 0;
}
