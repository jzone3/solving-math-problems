/* Fast graph6 scanner for WoW 129 (and padded criterion).
 * stdin: graph6 lines (n <= 62). Reports any graph with
 *   dev - R > -EPS   (direct near-violation/violation)
 * or A/(4m) - R > EPS_PAD (padded violation, strict positive only),
 * plus running max of both scores.
 * dev^2 = (S + 2m)/n - (2m/n)^2, S = sum d^2  (trace identity).
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define MAXN 64

int main(int argc, char **argv) {
    double eps_direct = argc > 1 ? atof(argv[1]) : 1e-9;
    char line[4096];
    double best_d = -1e18, best_p = -1e18;
    char best_d_g[4096] = "", best_p_g[4096] = "";
    long long cnt = 0;
    double invsqrt[MAXN * MAXN];
    for (int i = 1; i < MAXN * MAXN; i++) invsqrt[i] = 1.0 / sqrt((double)i);
    while (fgets(line, sizeof line, stdin)) {
        int len = strlen(line);
        while (len && (line[len-1] == '\n' || line[len-1] == '\r')) line[--len] = 0;
        if (!len) continue;
        cnt++;
        int n = line[0] - 63;
        int d[MAXN]; memset(d, 0, sizeof d);
        unsigned char eu[2048], ev[2048]; int ne = 0;
        int k = 0; /* bit index */
        const char *p = line + 1;
        int bitbuf = 0, bitcnt = 0;
        for (int j = 1; j < n; j++) {
            for (int i = 0; i < j; i++) {
                if (bitcnt == 0) { bitbuf = (*p++) - 63; bitcnt = 6; }
                if (bitbuf & (1 << (bitcnt - 1))) { eu[ne] = i; ev[ne] = j; ne++; d[i]++; d[j]++; }
                bitcnt--;
            }
        }
        if (!ne) continue;
        long long S = 0, m2 = 2LL * ne;
        for (int i = 0; i < n; i++) S += (long long)d[i] * d[i];
        double R = 0;
        for (int e = 0; e < ne; e++) R += invsqrt[d[eu[e]] * d[ev[e]]];
        double mean = (double)m2 / n;
        double dev = sqrt(((double)S + m2) / n - mean * mean);
        double sd = dev - R;
        /* phi: max over integer n' >= n of dev^2(n') - R^2 (isolated-vertex padding) */
        double A = (double)S + m2;
        double nstar = 2.0 * m2 * m2 / A;  /* 8m^2/A */
        double phi = -1e18;
        double cands[3] = {(double)n, floor(nstar), ceil(nstar)};
        for (int c = 0; c < 3; c++) {
            double nn = cands[c];
            if (nn < n) continue;
            double v = A / nn - ((double)m2 / nn) * ((double)m2 / nn) - R * R;
            if (v > phi) phi = v;
        }
        if (sd > best_d) { best_d = sd; strcpy(best_d_g, line); }
        if (phi > best_p) { best_p = phi; strcpy(best_p_g, line); }
        if (sd > eps_direct) printf("DIRECT %.12f %s\n", sd, line);
        if (phi > 1e-9) printf("PHI %.12f %s\n", phi, line);
    }
    fprintf(stderr, "scanned %lld | best direct %.12f (%s) | best padded %.12f (%s)\n",
            cnt, best_d, best_d_g, best_p, best_p_g);
    return 0;
}
