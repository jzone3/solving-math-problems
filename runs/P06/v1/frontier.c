/* P06/V1: exhaustive scan of all graphical degree sequences of length n,
 * scoring s(d) = dev(d) - R_lb(d)  (see frontier.py for definitions & rigor).
 * Prints any sequence with s > -1e-6 (near-zeros; re-checked exactly in Python)
 * and the global float max. Usage: ./frontier n
 */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

static int n;
static int d[64];            /* non-increasing sequence being built */
static long long cnt = 0;
static double best = -1e18;
static int bestseq[64];

static double wsorted[64];   /* workspace */

static int erdos_gallai(void) {
    /* d non-increasing; sum even checked by caller */
    long long pref = 0;
    for (int k = 1; k <= n; k++) {
        pref += d[k - 1];
        long long rhs = (long long)k * (k - 1);
        for (int i = k; i < n; i++) rhs += d[i] < k ? d[i] : k;
        if (pref > rhs) return 0;
    }
    return 1;
}

static double score(void) {
    double s1 = 0, s2 = 0;
    int npos = 0;
    for (int i = 0; i < n; i++) {
        s1 += d[i];
        s2 += (double)d[i] * d[i];
        if (d[i] > 0) npos++;
    }
    double dev2 = (s1 + s2) / n - (s1 / n) * (s1 / n);
    double dev = dev2 > 0 ? sqrt(dev2) : 0;
    if (npos == 0) return dev; /* empty graph: score 0 */
    /* weights ascending = 1/sqrt(deg) for degrees descending; d is
     * non-increasing so w[i] = 1/sqrt(d[i]) is non-decreasing over positives */
    for (int i = 0; i < npos; i++) wsorted[i] = 1.0 / sqrt((double)d[i]);
    double pref[65];
    pref[0] = 0;
    for (int i = 0; i < npos; i++) pref[i + 1] = pref[i] + wsorted[i];
    double total = 0;
    for (int u = 0; u < npos; u++) {
        int k = d[u];
        double wu = wsorted[u];
        double s = pref[k];
        if (wu <= wsorted[k - 1]) s += wsorted[k] - wu; /* k < npos guaranteed */
        total += wu * s;
    }
    return dev - total / 2.0;
}

static void rec(int i, int maxd, long long sum) {
    if (i == n) {
        if (sum % 2) return;
        if (!erdos_gallai()) return;
        cnt++;
        double s = score();
        if (s > best) {
            best = s;
            for (int j = 0; j < n; j++) bestseq[j] = d[j];
        }
        if (s > -1e-6) {
            printf("NEARZERO %.17g :", s);
            for (int j = 0; j < n; j++) printf(" %d", d[j]);
            printf("\n");
        }
        return;
    }
    int hi = maxd < n - 1 ? maxd : n - 1;
    for (int v = hi; v >= 0; v--) {
        d[i] = v;
        rec(i + 1, v, sum + v);
    }
}

int main(int argc, char **argv) {
    n = atoi(argv[1]);
    rec(0, n - 1, 0);
    printf("DONE n=%d graphical=%lld floatmax=%.17g at:", n, cnt, best);
    for (int j = 0; j < n; j++) printf(" %d", bestseq[j]);
    printf("\n");
    return 0;
}
