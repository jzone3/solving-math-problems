/* P12 V5: direct-DFS exhaustive search for mirror-symmetric T2(n), n odd (works for n=13).
 *
 * Same math as mirror.c (see NOTES.md C5): WLOG the square contains the identity row and is
 * invariant under M(r)_j = (n-1) - r_{n-1-j}. Remaining n-1 rows form M-orbits {r, M(r)}
 * (size 2, or 1 if M(r)=r). First column is a permutation; branch on the smallest free
 * first-column symbol s and grow a row r starting with s symbol-by-symbol, adding the arcs
 * of BOTH r and M(r) (arc (a,b) of r ⇒ arc (n-1-b, n-1-a) of M(r)) with tuscan-2 checks.
 * At completion: if M(r)=r it is an M-fixed row (arcs of M(r) = arcs of r; must NOT have
 * been double-added) -- handled by treating fixed rows separately: a row is M-fixed iff
 * r_j + r_{n-1-j} = n-1 for all j; we run two modes when extending class s:
 * pair mode (r != M(r), add both rows) and fixed mode (constrain r to be M-fixed, add once).
 * Deterministic branching => each mirror-symmetric square found exactly once.
 *
 * Build: gcc -O3 -march=native -fopenmp -o mirror2 mirror2.c
 * Run: ./mirror2 n
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <omp.h>

static int N;
static long long solutions = 0;
static unsigned long long nodes_total = 0;

typedef struct {
    uint16_t u1[16], u2[16];   /* used dist-1 / dist-2 arcs: u1[a] bit b */
    uint16_t firstmask, lastmask;
    uint8_t rows[16][16];
    int nrows;
    unsigned long long nodes;
} St;

static void emit(St *st) {
    #pragma omp critical
    {
        solutions++;
        printf("SOLUTION n=%d (mirror-symmetric)\n", N);
        for (int i = 0; i < st->nrows; i++) {
            for (int j = 0; j < N; j++) printf("%d ", st->rows[i][j]);
            printf("\n");
        }
        fflush(stdout);
    }
}

static inline int add1(St *st, int a, int b) {
    if (st->u1[a] & (1u << b)) return 0;
    st->u1[a] |= (uint16_t)(1u << b); return 1;
}
static inline void del1(St *st, int a, int b) { st->u1[a] &= (uint16_t)~(1u << b); }
static int K2 = 1; /* set 0 (env T1=1) to search Tuscan-1 instead (validation mode) */
static inline int add2(St *st, int a, int b) {
    if (!K2) return 1;
    if (st->u2[a] & (1u << b)) return 0;
    st->u2[a] |= (uint16_t)(1u << b); return 1;
}
static inline void del2(St *st, int a, int b) { if (K2) st->u2[a] &= (uint16_t)~(1u << b); }

static void branch_class(St *st);

/* ---- pair mode: grow row r (r != M(r)); arcs of both r and its mirror added ---- */
/* invariant: for placed prefix r[0..pos-1], arcs (r[j],r[j+1]) and mirrored (N-1-r[j+1],N-1-r[j])
   are in u1 (similarly dist-2). */
static void grow_pair(St *st, uint8_t *r, int pos, uint16_t inrow) {
    if (pos == N) {
        /* completed; must not be M-fixed (fixed rows handled in fixed mode) */
        int fixedrow = 1;
        for (int j = 0; j < N; j++) if (r[j] + r[N-1-j] != N-1) { fixedrow = 0; break; }
        if (fixedrow) return;
        /* canonical: pair counted once: mirror's first symbol must be > r[0]? No: mirror
           first = N-1-r[N-1]; branching is deterministic on smallest free class, and the
           mirror row's class is marked used, so no duplicate. */
        int mf = N - 1 - r[N-1], ml = N - 1 - r[0];
        /* lasts: r[N-1] and ml; firsts: r[0] and mf; already checked incrementally below */
        (void)mf; (void)ml;
        memcpy(st->rows[st->nrows], r, N); st->nrows++;
        for (int j = 0; j < N; j++) st->rows[st->nrows][j] = (uint8_t)(N - 1 - r[N-1-j]);
        st->nrows++;
        branch_class(st);
        st->nrows -= 2;
        return;
    }
    st->nodes++;
    int prev = r[pos-1], prev2 = (pos >= 2) ? r[pos-2] : -1;
    for (int b = 0; b < N; b++) {
        if (inrow & (1u << b)) continue;
        int rb = N - 1 - b, rp = N - 1 - prev;
        /* dist-1 arcs: (prev,b) and mirrored (rb,rp); note they can coincide only if
           b == N-1-prev i.e. arc is self-mirror; then adding twice must be rejected. */
        if (!add1(st, prev, b)) continue;
        if (!add1(st, rb, rp)) { del1(st, prev, b); continue; }
        int ok = 1, a2 = 0;
        if (prev2 >= 0) {
            int rp2 = N - 1 - prev2;
            if (!add2(st, prev2, b)) ok = 0;
            else if (!add2(st, rb, rp2)) { del2(st, prev2, b); ok = 0; }
            else a2 = 1;
        }
        if (ok) {
            /* first/last column checks when placing last symbol */
            int fl_ok = 1;
            uint16_t sf = st->firstmask, sl = st->lastmask;
            if (pos == N - 1) {
                int mf = N - 1 - b;      /* mirror row first symbol */
                int ml = N - 1 - r[0];   /* mirror row last symbol */
                if (b == ml || mf == r[0]) fl_ok = 0;               /* distinct lasts/firsts */
                if (fl_ok && ((st->lastmask >> b) & 1)) fl_ok = 0;
                if (fl_ok && ((st->lastmask >> ml) & 1)) fl_ok = 0;
                if (fl_ok && ((st->firstmask >> mf) & 1)) fl_ok = 0;
                if (fl_ok) {
                    st->lastmask |= (uint16_t)((1u << b) | (1u << ml));
                    st->firstmask |= (uint16_t)(1u << mf);
                }
            }
            if (fl_ok) {
                r[pos] = (uint8_t)b;
                grow_pair(st, r, pos + 1, (uint16_t)(inrow | (1u << b)));
            }
            st->firstmask = sf; st->lastmask = sl;
        }
        if (a2) { del2(st, prev2, b); del2(st, rb, N - 1 - prev2); }
        del1(st, rb, rp); del1(st, prev, b);
    }
}

/* ---- fixed mode: grow M-fixed row: r[N-1-j] = N-1-r[j]; choose first half ---- */
static void grow_fixed(St *st, uint8_t *r, int pos, uint16_t inrow) {
    /* rows with r[j]+r[N-1-j]=N-1: middle symbol r[(N-1)/2] = (N-1)/2. Determine r by
       positions 0..(N-3)/2; each choice b at pos also fixes N-1-b at N-1-pos.
       Simpler: grow positions left to right but when pos > (N-1)/2 the symbol is forced. */
    if (pos == N) {
        memcpy(st->rows[st->nrows], r, N); st->nrows++;
        branch_class(st);
        st->nrows--;
        return;
    }
    st->nodes++;
    int half = (N - 1) / 2;
    int prev = r[pos-1], prev2 = (pos >= 2) ? r[pos-2] : -1;
    int lo = 0, hi = N - 1, forced = -1;
    if (pos > half) { forced = N - 1 - r[N - 1 - pos]; lo = hi = forced; }
    else if (pos == half) { lo = hi = (N - 1) / 2; } /* middle symbol forced */
    for (int b = lo; b <= hi; b++) {
        if (inrow & (1u << b)) continue;
        if (pos <= half && b == N - 1 - b && pos != half) continue;
        if (pos < half && ((inrow >> (N - 1 - b)) & 0)) {;}
        if (!add1(st, prev, b)) continue;
        int a2 = 0, ok = 1;
        if (prev2 >= 0) { if (!add2(st, prev2, b)) ok = 0; else a2 = 1; }
        if (ok) {
            int fl_ok = 1;
            uint16_t sl = st->lastmask;
            if (pos == N - 1) {
                if ((st->lastmask >> b) & 1) fl_ok = 0;
                else st->lastmask |= (uint16_t)(1u << b);
            }
            if (fl_ok) {
                r[pos] = (uint8_t)b;
                grow_fixed(st, r, pos + 1, (uint16_t)(inrow | (1u << b)));
            }
            st->lastmask = sl;
        }
        if (a2) del2(st, prev2, b);
        del1(st, prev, b);
    }
}

static void branch_class(St *st) {
    uint16_t all = (uint16_t)((1u << N) - 1);
    if (st->firstmask == all) { emit(st); return; }
    int s = __builtin_ctz((unsigned)(~st->firstmask & all));
    uint8_t r[16];
    r[0] = (uint8_t)s;
    st->firstmask |= (uint16_t)(1u << s);
    /* pair mode */
    grow_pair(st, r, 1, (uint16_t)(1u << s));
    /* fixed mode: fixed row starting with s has last symbol N-1-s; needs both free */
    if (!((st->lastmask >> (N - 1 - s)) & 1) && s != N - 1 - s) {
        uint16_t sl = st->lastmask;
        /* last symbol set at pos N-1 in grow_fixed */
        grow_fixed(st, r, 1, (uint16_t)(1u << s));
        st->lastmask = sl;
    }
    st->firstmask &= (uint16_t)~(1u << s);
}

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: %s n\n", argv[0]); return 1; }
    N = atoi(argv[1]);
    if (getenv("T1")) K2 = 0;

    /* parallelize over the first two symbols after s=1's start: enumerate (b1,b2) pairs */
    double t0 = omp_get_wtime();
    int P = N * N;
    #pragma omp parallel
    {
        St st0;
        #pragma omp for schedule(dynamic, 1)
        for (int t = 0; t < P; t++) {
            int b1 = t / N, b2 = t % N;
            St *st = &st0;
            memset(st, 0, sizeof(St));
            /* identity row */
            for (int j = 0; j < N; j++) st->rows[0][j] = (uint8_t)j;
            st->nrows = 1;
            for (int j = 0; j + 1 < N; j++) st->u1[j] |= (uint16_t)(1u << (j+1));
            for (int j = 0; j + 2 < N; j++) st->u2[j] |= (uint16_t)(1u << (j+2));
            st->firstmask = 1u; st->lastmask = (uint16_t)(1u << (N-1));
            /* class 1: rows starting 1,b1,b2... (both pair and fixed handled via wrapper) */
            if (b1 == 1 || b2 == 1 || b1 == b2) continue;
            /* we emulate branch_class(s=1) but restricted to prefix 1,b1,b2 */
            uint8_t r[16]; r[0] = 1;
            st->firstmask |= 2u;
            /* pair mode with forced prefix */
            {
                uint16_t inrow = 1u << 1;
                int okpref = 1;
                /* place b1 */
                if (st->u1[1] & (1u << b1)) okpref = 0;
                if (okpref) {
                    st->u1[1] |= (uint16_t)(1u << b1);
                    int rb = N-1-b1, rp = N-1-1;
                    if (st->u1[rb] & (1u << rp)) { st->u1[1] &= (uint16_t)~(1u << b1); okpref = 0; }
                    else {
                        st->u1[rb] |= (uint16_t)(1u << rp);
                        r[1] = (uint8_t)b1; inrow |= (uint16_t)(1u << b1);
                        /* place b2 via grow_pair at pos 2 with candidate loop restricted:
                           simplest: call grow_pair and let it try all b, but we only want b2;
                           instead directly attempt b2 */
                        int prev = b1, prev2 = 1;
                        if (!(inrow & (1u << b2)) && !(st->u1[prev] & (1u << b2))) {
                            int rb2 = N-1-b2, rp2 = N-1-prev;
                            if (!(st->u1[rb2] & (1u << rp2))) {
                                st->u1[prev] |= (uint16_t)(1u << b2);
                                st->u1[rb2] |= (uint16_t)(1u << rp2);
                                if (add2(st, prev2, b2)) {
                                    int rpp = N-1-prev2;
                                    if (add2(st, rb2, rpp)) {
                                        r[2] = (uint8_t)b2;
                                        grow_pair(st, r, 3, (uint16_t)(inrow | (1u << b2)));
                                        del2(st, rb2, rpp);
                                    }
                                    del2(st, prev2, b2);
                                }
                                st->u1[rb2] &= (uint16_t)~(1u << rp2);
                                st->u1[prev] &= (uint16_t)~(1u << b2);
                            }
                        }
                        st->u1[rb] &= (uint16_t)~(1u << rp);
                        st->u1[1] &= (uint16_t)~(1u << b1);
                    }
                }
            }
            /* fixed mode with forced prefix */
            if (!((st->lastmask >> (N - 2)) & 1)) {
                uint16_t inrow = 1u << 1;
                int half = (N - 1) / 2;
                int ok = 1;
                /* pos1 = b1 (must respect fixed-row structure: b1 != N-1-1? b1 can be anything
                   except conflicts; forced-symbol logic only kicks in at pos >= half) */
                if (1 <= half && b1 == N - 1 - b1) ok = 0;
                if (ok && !(st->u1[1] & (1u << b1))) {
                    st->u1[1] |= (uint16_t)(1u << b1);
                    r[1] = (uint8_t)b1; inrow |= (uint16_t)(1u << b1);
                    int prev = b1, prev2 = 1;
                    int b2ok = 1;
                    if (2 <= half && b2 == N - 1 - b2 && 2 != half) b2ok = 0;
                    if (2 == half && b2 != (N-1)/2) b2ok = 0;
                    if (2 > half) b2ok = (b2 == N - 1 - r[N-3]); /* n>=7 => half>=3, unreachable */
                    if (b2ok && !(inrow & (1u << b2)) && !(st->u1[prev] & (1u << b2))) {
                        st->u1[prev] |= (uint16_t)(1u << b2);
                        if (add2(st, prev2, b2)) {
                            r[2] = (uint8_t)b2;
                            grow_fixed(st, r, 3, (uint16_t)(inrow | (1u << b2)));
                            del2(st, prev2, b2);
                        }
                        st->u1[prev] &= (uint16_t)~(1u << b2);
                    }
                    st->u1[1] &= (uint16_t)~(1u << b1);
                }
            }
            st->firstmask &= (uint16_t)~2u;
            #pragma omp atomic
            nodes_total += st->nodes;
            st->nodes = 0;
        }
    }
    printf("MIRROR2 DONE n=%d solutions=%lld nodes=%llu time=%.1fs\n",
           N, solutions, nodes_total, omp_get_wtime()-t0);
    return 0;
}
