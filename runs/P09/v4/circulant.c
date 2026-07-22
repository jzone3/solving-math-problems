/* P09 Bollobas-Nikiforov circulant exhaust (variant V4, part 2).
 *
 * For each n (argv range), enumerates ALL circulant graphs C_n(S),
 * S subseteq {1..floor(n/2)}, S nonempty, excluding the complete graph.
 * Eigenvalues are lambda_j = sum_{s in S, s<n/2} 2cos(2*pi*j*s/n)
 *                            + [n/2 in S] cos(pi*j),  j = 0..n-1.
 * Subsets are visited in Gray-code order so the eigenvalue vector is
 * updated incrementally in O(n) per subset.
 *
 * Violation test: s2 = l1^2 + l2^2 > 2m(1 - 1/w) + eps, with exact clique
 * number w by bitmask branch-and-bound (only when s2 > m, since w >= 2).
 *
 * Usage: ./circulant nmin nmax
 * Build: gcc -O3 -march=native -o circulant circulant.c -lm
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdint.h>

#define NMAX 64
static uint64_t adj[NMAX];
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
static int max_clique(int n) {
    best_clique = 1;
    expand((n == 64) ? ~0ull : ((1ull << n) - 1), 0);
    return best_clique;
}

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: %s nmin nmax\n", argv[0]); return 1; }
    int nmin = atoi(argv[1]), nmax = atoi(argv[2]);
    for (int n = nmin; n <= nmax && n <= NMAX; n++) {
        int h = n / 2;                 /* generators 1..h */
        int half = (n % 2 == 0);       /* generator h is an involution if n even */
        /* delta[s][j] = contribution of generator s to lambda_j */
        static double delta[NMAX / 2 + 1][NMAX];
        for (int s = 1; s <= h; s++)
            for (int j = 0; j < n; j++)
                delta[s][j] = (half && s == h) ? cos(M_PI * j)
                                               : 2.0 * cos(2.0 * M_PI * j * s / n);
        double lam[NMAX];
        memset(lam, 0, sizeof lam);
        uint64_t nsub = 1ull << h;
        uint64_t cur = 0;
        long long evaluated = 0, violations = 0;
        double best_gap = -1e18; uint64_t best_S = 0; int best_w = 0, best_m = 0;
        double best_s2 = 0;
        for (uint64_t i = 1; i < nsub; i++) {
            uint64_t gray = i ^ (i >> 1);
            int bit = __builtin_ctzll(i);      /* generator index bit -> s = bit+1 */
            int s = bit + 1;
            double sign = (gray >> bit) & 1 ? 1.0 : -1.0;
            for (int j = 0; j < n; j++) lam[j] += sign * delta[s][j];
            cur = gray;
            if (cur == nsub - 1) continue;     /* complete graph */
            /* degree = lam[0]; m = n*deg/2 */
            double deg = lam[0];
            double m = n * deg / 2.0;
            double l1 = -1e18, l2 = -1e18;
            for (int j = 0; j < n; j++) {
                if (lam[j] > l1) { l2 = l1; l1 = lam[j]; }
                else if (lam[j] > l2) l2 = lam[j];
            }
            double s2 = l1 * l1 + l2 * l2;
            if (s2 <= m - 1e-6) continue;
            /* build adjacency and clique number */
            memset(adj, 0, sizeof adj);
            for (int b = 0; b < h; b++) {
                if (!((cur >> b) & 1)) continue;
                int g = b + 1;
                for (int v = 0; v < n; v++) {
                    int u = (v + g) % n;
                    adj[v] |= 1ull << u;
                    adj[u] |= 1ull << v;
                }
            }
            int w = max_clique(n);
            evaluated++;
            double rhs = 2.0 * m * (1.0 - 1.0 / w);
            double gap = s2 - rhs;
            if (gap > best_gap) {
                best_gap = gap; best_S = cur; best_w = w; best_m = (int)(m + 0.5);
                best_s2 = s2;
            }
            if (gap > 1e-7) {
                violations++;
                printf("VIOLATION n=%d S=0x%llx m=%.1f w=%d l1=%.10f l2=%.10f s2=%.10f rhs=%.10f gap=%.3e\n",
                       n, (unsigned long long)cur, m, w, l1, l2, s2, rhs, gap);
                fflush(stdout);
            }
        }
        fprintf(stderr,
            "n=%d subsets=%llu evaluated=%lld violations=%lld best_gap=%.6e best_S=0x%llx best_m=%d best_w=%d best_s2=%.10f\n",
            n, (unsigned long long)(nsub - 1), evaluated, violations, best_gap,
            (unsigned long long)best_S, best_m, best_w, best_s2);
        fflush(stderr);
    }
    return 0;
}
