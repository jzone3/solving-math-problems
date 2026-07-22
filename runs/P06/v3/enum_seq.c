/* Exhaustively verify the unified GM reduction (*) over ALL graphical degree
 * sequences of length n:
 *   (*)  n^2 m^2 >= (nA - 4m^2) * exp( (1/m) * sum_v d_v ln d_v )
 * with A = sum d(d+1), 2m = sum d.  Since R >= m*exp(-(1/2m) sum d ln d)
 * (AM-GM over Randic edge weights), (*) for all sequences of length n implies
 * WoW conjecture 129 for ALL graphs on n vertices.
 *
 * Enumerates nonincreasing sequences (n-1 >= d1 >= ... >= dn >= 0), even sum,
 * Erdos-Gallai at leaves. Reports any sequence with g > EPS, tracks max g
 * (excluding exact-equality clique+padding cases up to fp noise).
 * usage: ./enum_seq n [d1_lo d1_hi]   (optional: restrict first degree value
 *        to [d1_lo, d1_hi] for parallel partitioning; results are additive)
 */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

static int n;
static int d[64];
static long long cnt_graphical = 0;
static double maxg = -1e18;
static int maxseq[64];
static double lg[64]; /* lg[x] = x*ln(x) */

static int erdos_gallai(void) {
    /* d nonincreasing */
    long long sum = 0;
    for (int i = 0; i < n; i++) sum += d[i];
    if (sum & 1) return 0;
    long long pref = 0;
    for (int k = 1; k <= n; k++) {
        pref += d[k - 1];
        long long tail = 0;
        for (int i = k; i < n; i++) tail += d[i] < k ? d[i] : k;
        if (pref > (long long)k * (k - 1) + tail) return 0;
        if (d[k-1] < k) break; /* Erdos-Gallai: enough to check k up to Durfee */
    }
    return 1;
}

static void leaf(void) {
    if (!erdos_gallai()) return;
    long long m2 = 0, A = 0;
    double H = 0;
    for (int i = 0; i < n; i++) {
        m2 += d[i];
        A += (long long)d[i] * (d[i] + 1);
        H += lg[d[i]];
    }
    if (!m2) return;
    cnt_graphical++;
    double m = m2 / 2.0;
    double rhs = (double)n * A - (double)m2 * m2;
    if (rhs <= 0) return;
    double g = log(rhs) + H / m - log((double)n * n * m * m);
    if (g > maxg) {
        maxg = g;
        for (int i = 0; i < n; i++) maxseq[i] = d[i];
    }
    if (g > 1e-9) {
        printf("VIOLATION g=%.12f seq:", g);
        for (int i = 0; i < n; i++) printf(" %d", d[i]);
        printf("\n");
    }
}

static void rec(int i, int hi, long long sum) {
    if (i == n) { leaf(); return; }
    for (int v = hi; v >= 0; v--) {
        d[i] = v;
        rec(i + 1, v, sum + v);
    }
}

int main(int argc, char **argv) {
    n = atoi(argv[1]);
    int lo = argc > 3 ? atoi(argv[2]) : 0;
    int hi = argc > 3 ? atoi(argv[3]) : n - 1;
    for (int x = 0; x < 64; x++) lg[x] = x ? x * log((double)x) : 0.0;
    for (int v = hi; v >= lo; v--) { d[0] = v; rec(1, v, v); }
    printf("n=%d graphical sequences=%lld max g=%.12g seq:", n, cnt_graphical, maxg);
    for (int i = 0; i < n; i++) printf(" %d", maxseq[i]);
    printf("\n");
    return 0;
}
