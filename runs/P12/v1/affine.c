/* affine.c — affine-twisted multiplicative circular Tuscan-2 arrays.
 *
 * Rows: row_u = u*b + v_u (mod n) for u in Zn*, where b is a circular
 * arrangement of Zn (b[0] = 0 wlog) and v in Zn^{n-1} is a twist vector.
 * d1 pair (x, x+delta) occurs at position c of row_u iff u*d_c = delta and
 * x = u*b_c + v_u (d_c = b_{c+1}-b_c).  Exactly-once coverage for every
 * delta <=> for each delta the map c -> (delta/d_c)*b_c + v_{delta/d_c} is a
 * bijection; ditto distance 2 with e_c = b_{c+2}-b_c.  Cells with equal u
 * never collide, so the conditions reduce to binary difference constraints
 * v_u - v_{u'} != K, precomputable from b.  Trivial twists v_u = a + m*u give
 * equivalent arrays; normalized away by fixing v_1 = v_2 = 0 (2 primitive).
 *
 * For random b we solve the v-CSP by DFS; every solution is an (n-1) x n
 * circular Tuscan-2 array (independently re-checked), printed to stdout in
 * cutconv format.  Usage: ./affine n seed [max_arrays] [basefile]
 * With basefile: enumerate ALL v-solutions for each base line (n numbers).
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define NMAX 16
static int N;
static int inv_[NMAX];
static uint16_t forb[NMAX][NMAX];   /* forb[u][u'] bitmask of forbidden (v_u - v_u') mod n */
static int b_[NMAX], d_[NMAX], e_[NMAX];
static int v_[NMAX];                /* v_[u] for u = 1..n-1; -1 = unassigned */
static long long arrays_out = 0, bases_tried = 0, csp_sat = 0;
static long long max_arrays = -1;

static uint64_t rng;
static uint64_t xrnd(void) { rng ^= rng << 13; rng ^= rng >> 7; rng ^= rng << 17; return rng; }

static int check_and_print(void) {
    static uint8_t rows[NMAX][NMAX];
    static uint8_t seen1[NMAX][NMAX], seen2[NMAX][NMAX];
    memset(seen1, 0, sizeof seen1);
    memset(seen2, 0, sizeof seen2);
    int m = N - 1;
    for (int u = 1; u < N; u++)
        for (int c = 0; c < N; c++)
            rows[u - 1][c] = (u * b_[c] + v_[u]) % N;
    for (int r = 0; r < m; r++)
        for (int c = 0; c < N; c++) {
            int x = rows[r][c], y1 = rows[r][(c + 1) % N], y2 = rows[r][(c + 2) % N];
            if (seen1[x][y1]++ || seen2[x][y2]++) return 0;   /* construction bug guard */
        }
    for (int r = 0; r < m; r++) {
        for (int c = 0; c < N; c++) printf("%d ", rows[r][c]);
        printf("\n");
    }
    printf("\n");
    arrays_out++;
    return 1;
}

static int order_[NMAX], no_;

static void dfs(int idx) {
    if (max_arrays >= 0 && arrays_out >= max_arrays) return;
    if (idx == no_) { csp_sat++; check_and_print(); return; }
    int u = order_[idx];
    for (int val = 0; val < N; val++) {
        int ok = 1;
        for (int j = 0; j < idx && ok; j++) {
            int u2 = order_[j];
            if (forb[u][u2] >> ((val - v_[u2] + N) % N) & 1) ok = 0;
        }
        /* fixed vars v_1 = v_2 = 0 */
        if (ok && (forb[u][1] >> val & 1)) ok = 0;
        if (ok && (forb[u][2] >> val & 1)) ok = 0;
        if (!ok) continue;
        v_[u] = val;
        dfs(idx + 1);
    }
    v_[u] = -1;
}

static void add_constraints(const int *diff) {
    /* cells for delta: u_c = delta/diff[c]; collision between c,c' with
     * different u:  v_{u_c} - v_{u_c'} != u_c'*b_{c'} - u_c*b_c.
     * Multiply delta out: u_c = delta*inv(diff[c]).  For the constraint set
     * (over all delta) between a PAIR (u, u') with u'/u = diff[c]/diff[c']:
     * iterate delta directly (n small). */
    for (int delta = 1; delta < N; delta++)
        for (int c = 0; c < N; c++)
            for (int c2 = c + 1; c2 < N; c2++) {
                int u = delta * inv_[diff[c]] % N;
                int u2 = delta * inv_[diff[c2]] % N;
                if (u == u2) continue;   /* same row: b_c != b_c2 suffices */
                int k = ((u2 * b_[c2] - u * b_[c]) % N + N) % N;
                forb[u][u2] |= 1u << k;
                forb[u2][u] |= 1u << ((N - k) % N);
            }
}

int main(int argc, char **argv) {
    N = atoi(argv[1]);
    rng = argc > 2 ? strtoull(argv[2], 0, 10) : 12345;
    if (!rng) rng = 1;
    max_arrays = argc > 3 ? atoll(argv[3]) : -1;
    FILE *bf = argc > 4 ? fopen(argv[4], "r") : NULL;
    for (int x = 1; x < N; x++)
        for (int y = 1; y < N; y++) if (x * y % N == 1) inv_[x] = y;
    b_[0] = 0;
    int pool[NMAX];
    for (;;) {
        if (bf) {
            int okread = 1;
            for (int c = 0; c < N; c++)
                if (fscanf(bf, "%d", &b_[c]) != 1) { okread = 0; break; }
            if (!okread) break;
        } else {
            /* random circular arrangement */
            for (int i = 0; i < N - 1; i++) pool[i] = i + 1;
            for (int i = N - 2; i > 0; i--) { int j = xrnd() % (i + 1); int t = pool[i]; pool[i] = pool[j]; pool[j] = t; }
            for (int i = 0; i < N - 1; i++) b_[i + 1] = pool[i];
        }
        int ok = 1;
        for (int c = 0; c < N; c++) {
            d_[c] = ((b_[(c + 1) % N] - b_[c]) % N + N) % N;
            e_[c] = ((b_[(c + 2) % N] - b_[c]) % N + N) % N;
            if (!d_[c] || !e_[c]) ok = 0;   /* d_c always nonzero; e_c too (b distinct) */
        }
        if (!ok) continue;
        memset(forb, 0, sizeof forb);
        add_constraints(d_);
        add_constraints(e_);
        /* quick infeasibility: any fully forbidden pair with fixed vars */
        for (int u = 1; u < N; u++) v_[u] = -1;
        v_[1] = 0; v_[2] = 0;
        if ((forb[2][1] >> 0 & 1)) { bases_tried++; continue; }   /* v_2 - v_1 = 0 forbidden */
        no_ = 0;
        for (int u = 3; u < N; u++) order_[no_++] = u;
        dfs(0);
        bases_tried++;
        if (bases_tried % 1000000 == 0)
            fprintf(stderr, "affine: %lld bases, %lld CSP-sat, %lld arrays out\n",
                    bases_tried, csp_sat, arrays_out);
        if (max_arrays >= 0 && arrays_out >= max_arrays) break;
    }
    fprintf(stderr, "affine done: %lld bases, %lld arrays\n", bases_tried, arrays_out);
    return 0;
}
