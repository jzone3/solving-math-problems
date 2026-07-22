/* Exhaust all threshold graphs up to N vertices for WoW 129 (direct + padded Phi).
 * Threshold graph = creation sequence b_2..b_n (b_i = 1: dominating/join vertex,
 * 0: isolated-at-the-time vertex). Covers all cliques, stars, complete splits, etc.
 * Extremal graphs for degree-based-vs-Randic objectives are expected here
 * (assortative realizations minimize R for their degree sequence).
 * Enumerates 2^(n-1) sequences per n; computes degrees and R directly.
 */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define MAXN 34

int deg[MAXN];
int seq[MAXN];

int main(int argc, char **argv) {
    int NMAX = argc > 1 ? atoi(argv[1]) : 26;
    double lg[MAXN];
    for (int x = 0; x < MAXN; x++) lg[x] = x ? x * log((double)x) : 0.0;
    double bestd_all = -1e18, bestp_all = -1e18, bestg_all = -1e18;
    for (int n = 2; n <= NMAX; n++) {
        double bestd = -1e18, bestp = -1e18, bestg = -1e18;
        long long bd_code = -1, bp_code = -1, bg_code = -1;
        long long tot = 1LL << (n - 1);
        for (long long code = 0; code < tot; code++) {
            /* build degrees: vertex 0 first; then i=1..n-1 with bit b */
            for (int i = 0; i < n; i++) deg[i] = 0;
            for (int i = 1; i < n; i++) {
                seq[i] = (code >> (i - 1)) & 1;
                if (seq[i]) {
                    deg[i] += i;
                    for (int j = 0; j < i; j++) deg[j]++;
                }
            }
            long long S = 0, m2 = 0;
            for (int i = 0; i < n; i++) { S += (long long)deg[i] * deg[i]; m2 += deg[i]; }
            if (!m2) continue;
            /* R: edge (j,i) exists iff exists k >= max(i,j)... in threshold creation:
               vertex i (join) connects to all j < i. Edge set = {(j,i): i>j, seq[i]=1}
               plus edges added by later joins? No: later join k>i adds (i,k) which is
               covered by seq[k]=1. So edges exactly {(j,i): seq[i]=1, j<i}. */
            double R = 0;
            for (int i = 1; i < n; i++) if (seq[i])
                for (int j = 0; j < i; j++)
                    R += 1.0 / sqrt((double)deg[i] * deg[j]);
            double A = (double)S + m2;
            double mean = (double)m2 / n;
            double dev = sqrt(A / n - mean * mean);
            double sd = dev - R;
            double nstar = 2.0 * m2 * m2 / A;
            double phi = -1e18;
            double cands[3] = {(double)n, floor(nstar), ceil(nstar)};
            for (int c = 0; c < 3; c++) {
                double nn = cands[c];
                if (nn < n) continue;
                double v = A / nn - ((double)m2 / nn) * ((double)m2 / nn) - R * R;
                if (v > phi) phi = v;
            }
            /* (*) GM reduction value g */
            double H = 0;
            for (int i = 0; i < n; i++) H += lg[deg[i]];
            double rhs = (double)n * A - (double)m2 * m2;
            double m = m2 / 2.0;
            double g = rhs > 0 ? log(rhs) + H / m - log((double)n * n * m * m) : -1e18;
            if (g > bestg) { bestg = g; bg_code = code; }
            if (sd > bestd) { bestd = sd; bd_code = code; }
            if (phi > bestp) { bestp = phi; bp_code = code; }
            if (sd > 1e-9 || phi > 1e-9 || g > 1e-9)
                printf("VIOLATION n=%d code=%lld dev-R=%.12f phi=%.12f g=%.12f\n", n, code, sd, phi, g);
        }
        printf("n=%2d: best dev-R %.9f (code %lld) | best phi %.9f (code %lld) | best g %.9f (code %lld)\n",
               n, bestd, bd_code, bestp, bp_code, bestg, bg_code);
        fflush(stdout);
        if (bestd > bestd_all) bestd_all = bestd;
        if (bestp > bestp_all) bestp_all = bestp;
        if (bestg > bestg_all) bestg_all = bestg;
    }
    printf("OVERALL: best dev-R %.9f | best phi %.9f | best g %.9f\n", bestd_all, bestp_all, bestg_all);
    return 0;
}
