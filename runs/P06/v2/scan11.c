/* P06 V2 frontier scanner: reads graph6 (n <= 15) on stdin.
 * For each graph H (treated as the non-isolated "core"; geng -d1 recommended):
 *   - computes m, S = sum d^2, R (Randic) exactly enough in double
 *   - envelope check: if (S+2m)/(4m) <= R the graph is SAFE for every number
 *     of added isolated vertices (dev <= envelope for all n).
 *   - otherwise evaluates f(n) = sqrt((S+2m)/n - (2m/n)^2) - R for all total
 *     sizes n = nh .. NMAX and reports any f > -1e-7 (near-miss / positive),
 *     except exact equality members K_q with padding q-2.
 * Compile: gcc -O2 -o scan11 scan11.c -lm
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define NMAX_PAD 400

int main(void) {
    char line[64];
    double invsqrt[16 * 16];
    for (int a = 1; a < 16; a++)
        for (int b = 1; b < 16; b++)
            invsqrt[a * 16 + b] = 1.0 / sqrt((double)(a * b));

    long long count = 0, env_fail = 0;
    double worst = -1e18; /* max near-miss f over padded evals (excl. equality) */
    long long near = 0;

    while (fgets(line, sizeof line, stdin)) {
        int n = line[0] - 63;
        int deg[16] = {0};
        unsigned adj[16] = {0};
        int idx = 0, pos = 1, bit = 5;
        int val = line[pos] - 63;
        for (int j = 1; j < n; j++) {
            for (int i = 0; i < j; i++) {
                int b = (val >> bit) & 1;
                if (bit == 0) { pos++; val = line[pos] - 63; bit = 5; }
                else bit--;
                if (b) { adj[i] |= 1u << j; adj[j] |= 1u << i; deg[i]++; deg[j]++; }
            }
        }
        count++;
        int m = 0, S = 0;
        for (int i = 0; i < n; i++) { m += deg[i]; S += deg[i] * deg[i]; }
        m /= 2;
        if (m == 0) continue;
        double R = 0.0;
        for (int i = 0; i < n; i++)
            for (int j = i + 1; j < n; j++)
                if (adj[i] & (1u << j)) R += invsqrt[deg[i] * 16 + deg[j]];

        double env = (double)(S + 2 * m) / (4.0 * m);
        if (env <= R - 1e-9) continue; /* safe for every padding (with margin) */
        env_fail++;

        int is_clique = (m == n * (n - 1) / 2);
        double a = (double)(S + 2 * m), mm = 2.0 * m;
        for (int nt = n; nt <= NMAX_PAD; nt++) {
            double var = a / nt - (mm / nt) * (mm / nt);
            if (var < 0) var = 0;
            double f = sqrt(var) - R;
            if (f > -1e-7) {
                if (is_clique && nt == 2 * n - 2) continue; /* known equality */
                near++;
                if (f > worst) worst = f;
                printf("NEAR f=%.12f pad_n=%d g6=%s", f, nt, line);
            }
        }
    }
    fprintf(stderr, "scanned %lld cores, envelope-failing %lld, near-hits %lld, worst %g\n",
            count, env_fail, near, worst);
    return 0;
}
