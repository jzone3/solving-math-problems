/* Exhaustive Z3-orbit scan of the minimal ACZ shape (12 deg-4 sources x 16 deg-3
 * sinks, 48 arcs) for tau=3 Woodall counterexamples.
 *
 * Automorphism sigma of order 3 acting freely on sources: 4 source orbits {3a+i}.
 * Sinks: k orbits of size 3 ({3b+o}, 3k+f=16) plus f fixed sinks (a fixed sink has
 * in-degree 3 = one full source orbit -> "owner" orbit, consuming 1 rep out-slot).
 * Graph determined by: owners (non-decreasing canonical), contingency matrix c[a][b]
 * (row sums 4-m_a, col sums 3), and offset sets S_ab in Z3 with |S_ab|=c[a][b]
 * (rotation-minimal per column: exact dedup of the 3^k sink-rotation subgroup).
 *
 * Per candidate: bitmask dicut sweep over all X subsets of sources (tau filter),
 * WalkSAT 3-coloring on tight cuts with full-verification CEGAR loop; candidates not
 * packed within budget are printed for exact SAT verification in Python.
 * Usage: zscan f shard nshards [debug_print_first_N]
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

static int K, F;                 /* k sink orbits, f fixed sinks */
static int owners[13], m[4];     /* owner orbit per fixed sink; m[a]=#owned */
static int cmat[4][8];           /* contingency matrix */
static int Sab[4][8];            /* offset bitmask (3 bits) per (a,b) */
static const int SUBS[4][3] = {{0,-1,-1},{1,2,4},{3,5,6},{7,-1,-1}};
static const int NSUB[4] = {1,3,3,1};

static long long cand_total, tau_reject, packed_ok, dumped, dbg_left;
static unsigned rng_state = 12345u;
static unsigned rnd(void){ rng_state ^= rng_state<<13; rng_state ^= rng_state>>17;
    rng_state ^= rng_state<<5; return rng_state; }

static int rot3(int s, int r){ return ((s<<r)|(s>>(3-r)))&7; }

/* per-candidate arrays */
static int innb[16];             /* source bitmask per sink */
static int inarc_src[16][3], inarc_id[16][3], inarc_n[16];
static int arc_color[48];
static uint64_t tight[600]; static int ntight;

static void build_arcs(void){
    int aid = 0;
    for (int t = 0; t < 16; t++) { innb[t] = 0; inarc_n[t] = 0; }
    for (int a = 0; a < 4; a++) for (int i = 0; i < 3; i++) {
        int s = 3*a + i;
        for (int b = 0; b < K; b++) for (int o = 0; o < 3; o++)
            if (Sab[a][b] & (1<<o)) {
                int t = 3*b + (o + i) % 3;
                innb[t] |= 1<<s;
                inarc_src[t][inarc_n[t]] = s; inarc_id[t][inarc_n[t]++] = aid;
                aid++;
            }
        for (int j = 0; j < F; j++) if (owners[j] == a) {
                int t = 3*K + j;
                innb[t] |= 1<<s;
                inarc_src[t][inarc_n[t]] = s; inarc_id[t][inarc_n[t]++] = aid;
                aid++;
            }
    }
    /* aid must be 48; in-degrees must be 3 */
}

/* sweep: tau filter + collect tight (size-3) cut masks; returns 0 if tau<3 */
static int sweep_tau_tight(void){
    ntight = 0;
    for (int t = 0; t < 16; t++) {          /* in-arc dicuts, always size 3 */
        uint64_t msk = 0;
        for (int j = 0; j < 3; j++) msk |= 1ULL << inarc_id[t][j];
        if (ntight < 600) tight[ntight++] = msk;
    }
    for (int X = 1; X < 4095; X++) {
        int sz = 0; uint64_t msk = 0;
        for (int t = 0; t < 16; t++) {
            if ((innb[t] & ~X) == 0) continue;   /* t in Ymax */
            for (int j = 0; j < 3; j++)
                if ((X >> inarc_src[t][j]) & 1) {
                    sz++; msk |= 1ULL << inarc_id[t][j];
                    if (sz > 3) goto next_t_done; /* only need <=3 exact */
                }
            next_t_done:;
            if (sz > 3) break;
        }
        if (sz == 0) continue;
        if (sz < 3) return 0;
        if (sz == 3 && ntight < 600) tight[ntight++] = msk;
    }
    return 1;
}

/* full verification of current coloring; if violated cut found, store to *out */
static int verify_all(uint64_t colmask[3], uint64_t *out){
    for (int X = 1; X < 4095; X++) {
        int seen = 0, any = 0; uint64_t msk = 0;
        for (int t = 0; t < 16; t++) {
            if ((innb[t] & ~X) == 0) continue;
            for (int j = 0; j < 3; j++)
                if ((X >> inarc_src[t][j]) & 1) {
                    any = 1; msk |= 1ULL << inarc_id[t][j];
                    seen |= 1 << arc_color[inarc_id[t][j]];
                }
        }
        if (any && seen != 7) { *out = msk; return 0; }
    }
    return 1;
}

static int try_pack(void){
    uint64_t work[700]; int nwork = ntight;
    memcpy(work, tight, ntight * sizeof(uint64_t));
    for (int restart = 0; restart < 4; restart++) {
        for (int i = 0; i < 48; i++)
            arc_color[i] = (restart == 0) ? i % 3 : (int)(rnd() % 3);
        for (int cegar = 0; cegar < 8; cegar++) {
            uint64_t colmask[3];
            for (int step = 0; step < 2000; step++) {
                colmask[0] = colmask[1] = colmask[2] = 0;
                for (int i = 0; i < 48; i++) colmask[arc_color[i]] |= 1ULL << i;
                int vio = -1, misscol = -1;
                for (int c = 0; c < nwork; c++)
                    for (int kk = 0; kk < 3; kk++)
                        if ((work[c] & colmask[kk]) == 0) { vio = c; misscol = kk; break; }
                if (vio < 0) break;
                /* recolor a random arc of the violated cut to the missing color,
                   preferring one whose color appears twice+ in the cut */
                int ids[48], nid = 0;
                for (int i = 0; i < 48; i++)
                    if (work[vio] & (1ULL << i)) ids[nid++] = i;
                arc_color[ids[rnd() % nid]] = misscol;
            }
            colmask[0] = colmask[1] = colmask[2] = 0;
            for (int i = 0; i < 48; i++) colmask[arc_color[i]] |= 1ULL << i;
            int ok = 1;
            for (int c = 0; c < nwork; c++)
                for (int kk = 0; kk < 3; kk++)
                    if ((work[c] & colmask[kk]) == 0) { ok = 0; break; }
            if (!ok) break;                      /* walksat failed -> restart */
            uint64_t bad;
            if (verify_all(colmask, &bad)) return 1;
            if (nwork < 700) work[nwork++] = bad; /* CEGAR: add violated cut */
        }
    }
    return 0;
}

static void dump_candidate(void){
    printf("CAND f=%d owners=", F);
    for (int j = 0; j < F; j++) printf("%d", owners[j]);
    printf(" S=");
    for (int a = 0; a < 4; a++) for (int b = 0; b < K; b++) printf("%d", Sab[a][b]);
    printf("\n"); fflush(stdout);
}

static void check_candidate(void){
    cand_total++;
    build_arcs();
    if (dbg_left > 0) {
        dbg_left--;
        int t3 = sweep_tau_tight();
        int pk = t3 ? try_pack() : 0;
        printf("DBG tau3=%d packed=%d ", t3, pk);
        dump_candidate();
        return;
    }
    if (!sweep_tau_tight()) { tau_reject++; return; }
    if (try_pack()) { packed_ok++; return; }
    dumped++; dump_candidate();
}

/* enumerate offset choices column by column, rotation-minimal columns only */
static void rec_offsets(int b){
    if (b == K) { check_candidate(); return; }
    int idx[4];
    for (idx[0]=0; idx[0]<NSUB[cmat[0][b]]; idx[0]++)
    for (idx[1]=0; idx[1]<NSUB[cmat[1][b]]; idx[1]++)
    for (idx[2]=0; idx[2]<NSUB[cmat[2][b]]; idx[2]++)
    for (idx[3]=0; idx[3]<NSUB[cmat[3][b]]; idx[3]++) {
        int col[4], key = 0;
        for (int a = 0; a < 4; a++) { col[a] = SUBS[cmat[a][b]][idx[a]]; key = key*8 + col[a]; }
        int minimal = 1;
        for (int r = 1; r < 3 && minimal; r++) {
            int k2 = 0;
            for (int a = 0; a < 4; a++) k2 = k2*8 + rot3(col[a], r);
            if (k2 < key) minimal = 0;
        }
        if (!minimal) continue;
        for (int a = 0; a < 4; a++) Sab[a][b] = col[a];
        rec_offsets(b + 1);
    }
}

static long long mat_count;      /* for sharding on matrices */
static int shard, nshards;

static void rec_matrix(int a, int b, int rowleft, int colleft[8]){
    if (a == 4) {
        int ok = 1;
        for (int j = 0; j < K; j++) if (colleft[j] != 0) ok = 0;
        if (!ok) return;
        if (mat_count++ % nshards != shard) return;
        rec_offsets(0);
        return;
    }
    if (b == K) {
        if (rowleft == 0) rec_matrix(a+1, 0, a+1 < 4 ? 4 - m[a+1] : 0, colleft);
        return;
    }
    int mx = rowleft < 3 ? rowleft : 3;
    if (colleft[b] < mx) mx = colleft[b];
    for (int v = 0; v <= mx; v++) {
        cmat[a][b] = v; colleft[b] -= v;
        rec_matrix(a, b+1, rowleft - v, colleft);
        colleft[b] += v;
    }
}

static void rec_owners(int j, int lo){
    if (j == F) {
        for (int a = 0; a < 4; a++) m[a] = 0;
        for (int i = 0; i < F; i++) m[owners[i]]++;
        int bad = 0;
        for (int a = 0; a < 4; a++) if (m[a] > 4) bad = 1;
        if (bad) return;
        int colleft[8];
        for (int b = 0; b < K; b++) colleft[b] = 3;
        rec_matrix(0, 0, 4 - m[0], colleft);
        return;
    }
    for (int a = lo; a < 4; a++) { owners[j] = a; rec_owners(j+1, a); }
}

int main(int argc, char **argv){
    F = atoi(argv[1]); K = (16 - F) / 3;
    shard = atoi(argv[2]); nshards = atoi(argv[3]);
    dbg_left = argc > 4 ? atoll(argv[4]) : 0;
    rng_state ^= (unsigned)(shard * 2654435761u + 1);
    if (F == 0) K = 5; /* f must be 1,4,7,10,13 for 3k+f=16; f=16 handled elsewhere */
    rec_owners(0, 0);
    fprintf(stderr, "DONE f=%d shard=%d/%d cand=%lld tau_reject=%lld packed=%lld dumped=%lld\n",
            F, shard, nshards, cand_total, tau_reject, packed_ok, dumped);
    return 0;
}
