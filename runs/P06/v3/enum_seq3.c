/* Faster exhaustive verifier of the GM reduction (*) over all graphical degree
 * sequences of length n (see enum_seq.c for the math). Improvements:
 *   - incremental m2 / A / H along the recursion (leaf work O(EG) only)
 *   - parity pruning at the last position (sum must be even)
 *   - logs every sequence with g > -TOL_NEAR (near-misses) for the exact-R
 *     LP fallback (lp_fallback.py); prints VIOLATION for g > 1e-9
 *   - optional partition args: d1 fixed value, d2 range
 * usage: ./enum_seq3 n [d1 d2_lo d2_hi]
 */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define TOL_NEAR 1e-6

static int n;
static int d[64];
static long long cnt_graphical = 0;
static double maxg = -1e18;
static int maxseq[64];
static double lg[64];

static int erdos_gallai(void) {
    long long pref = 0;
    for (int k = 1; k <= n; k++) {
        pref += d[k - 1];
        long long tail = 0;
        for (int i = k; i < n; i++) tail += d[i] < k ? d[i] : k;
        if (pref > (long long)k * (k - 1) + tail) return 0;
        if (d[k - 1] < k) break;
    }
    return 1;
}

static void leaf(long long m2, long long A, double H) {
    if (!m2) return;
    if (!erdos_gallai()) return;
    cnt_graphical++;
    double m = m2 / 2.0;
    double rhs = (double)n * A - (double)m2 * m2;
    if (rhs <= 0) return;
    double g = log(rhs) + H / m - log((double)n * n * m * m);
    if (g > maxg) {
        maxg = g;
        for (int i = 0; i < n; i++) maxseq[i] = d[i];
    }
    if (g > -TOL_NEAR) {
        printf("%s g=%.15f seq:", g > 1e-9 ? "VIOLATION" : "NEAR", g);
        for (int i = 0; i < n; i++) printf(" %d", d[i]);
        printf("\n");
    }
}

static void rec(int i, int hi, long long m2, long long A, double H) {
    if (i == n - 1) {
        int par = (int)(m2 & 1);
        for (int v = (hi & 1) == par ? hi : hi - 1; v >= 0; v -= 2) {
            d[i] = v;
            leaf(m2 + v, A + (long long)v * (v + 1), H + lg[v]);
        }
        return;
    }
    for (int v = hi; v >= 0; v--) {
        d[i] = v;
        rec(i + 1, v, m2 + v, A + (long long)v * (v + 1), H + lg[v]);
    }
}

int main(int argc, char **argv) {
    n = atoi(argv[1]);
    for (int x = 0; x < 64; x++) lg[x] = x ? x * log((double)x) : 0.0;
    if (argc >= 5) {
        int d1 = atoi(argv[2]), lo = atoi(argv[3]), hi = atoi(argv[4]);
        d[0] = d1;
        if (hi > d1) hi = d1;
        for (int v = hi; v >= lo; v--) {
            d[1] = v;
            rec(2, v, (long long)d1 + v,
                (long long)d1 * (d1 + 1) + (long long)v * (v + 1), lg[d1] + lg[v]);
        }
        printf("n=%d d1=%d d2=[%d,%d] graphical=%lld max g=%.12g seq:",
               n, d1, lo, hi, cnt_graphical, maxg);
    } else if (argc >= 3) {
        int d1 = atoi(argv[2]);
        d[0] = d1;
        rec(1, d1, d1, (long long)d1 * (d1 + 1), lg[d1]);
        printf("n=%d d1=%d graphical=%lld max g=%.12g seq:", n, d1, cnt_graphical, maxg);
    } else {
        rec(0, n - 1, 0, 0, 0.0);
        printf("n=%d graphical=%lld max g=%.12g seq:", n, cnt_graphical, maxg);
    }
    for (int i = 0; i < n; i++) printf(" %d", maxseq[i]);
    printf("\n");
    return 0;
}
