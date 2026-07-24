/* Exhaustive scan: minimal ACZ shape (12 deg-4 sources x 16 deg-3 sinks, 48 arcs)
 * admitting an order-3 automorphism sigma acting NON-freely on sources.
 * (The free case p=4,q=0 was closed by zscan.c; here q = #fixed sources > 0.)
 *
 * Structure forced by sigma (order 3):
 *  - sources: p orbits of size 3 + q fixed, 3p+q=12, q in {3,6,9,12} (p=3..0)
 *  - sinks:   k orbits of size 3 + f fixed, 3k+f=16, f in {1,4,7,10,13,16}
 *  - fixed source (deg 4): sigma-invariant 4-neighborhood =
 *      (one full sink orbit [3 arcs] + one fixed sink) OR (4 distinct fixed sinks)
 *  - orbit source representative (deg 4): for each sink orbit b an offset subset
 *      S(a,b) subseteq Z3 (|S(a,b)| arcs), plus possibly "owning" fixed sinks
 *      (each owned fixed sink receives 1 arc from EACH orbit member; costs 1 deg)
 *  - fixed sink (indeg 3): owned by exactly one source orbit (3 arcs) XOR hit by
 *      exactly 3 distinct fixed sources
 *  - orbit sink representative (indeg 3): sum_a |S(a,b)| + #fixed sources hitting
 *      orbit b (each such source sends one arc to every orbit member) = 3
 *
 * Enumeration is exhaustive up to (super)set of isomorphism; overcounting is fine.
 * Every candidate: bitmask tau sweep; certified WalkSAT+CEGAR packing (verified
 * against ALL dicuts); unresolved candidates printed as "NCAND" for exact SAT.
 *
 * Usage: z3nf p f mode [shard nshards]
 *   mode 0=count only, 1=full scan, 2=scan + debug-print first 300 (NDBG lines)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

static int P, Q, K, F, MODE, SHARD, NSHARDS;

/* current assignment */
static int cmat[4][6];        /* |S(a,b)| for orbit source a, sink orbit b */
static int own[16];           /* fixed sink t: owner orbit 0..P-1, or P=3fixed-src */
static int Sab[4][6];         /* offset subsets (bitmask in Z3) */
static int fsrc_orb[12];      /* fixed source: chosen sink orbit b, or -1 (4 fixed) */
static int fsrc_f[12][4];     /* fixed source: fixed-sink targets (1 or 4), -1 pad */
static int e_b[6];            /* # fixed sources choosing sink orbit b */

static long long cand, tau_reject, packed, dumped, sat_needed;

/* ---- graph build + tau/pack machinery (12 sources, 16 sinks, 48 arcs) ---- */
static int NS = 12, NT = 16, NA = 48;
static int innb_[16], inarc_src[16][3], inarc_id[16][3], inarc_n[16];
static int nbrow[12][4], nbdeg[12];
static int arc_color[48];
static uint64_t tight[600]; static int ntight;
static unsigned rng_state = 88172645u;
static unsigned rnd(void){ rng_state ^= rng_state<<13; rng_state ^= rng_state>>17;
    rng_state ^= rng_state<<5; return rng_state; }

/* vertex numbering: sources: orbit a member m -> 3a+m (a<P), fixed j -> 3P+j.
 * sinks: orbit b member m -> 3b+m (b<K), fixed t -> 3K+t. */
static int build_graph(void){
    for (int s = 0; s < NS; s++) nbdeg[s] = 0;
    for (int a = 0; a < P; a++)
        for (int m = 0; m < 3; m++) {
            int s = 3*a + m;
            for (int b = 0; b < K; b++)
                for (int o = 0; o < 3; o++)
                    if (Sab[a][b] & (1 << o))
                        nbrow[s][nbdeg[s]++] = 3*b + (m + o) % 3;
            for (int t = 0; t < F; t++)
                if (own[t] == a) nbrow[s][nbdeg[s]++] = 3*K + t;
        }
    for (int j = 0; j < Q; j++) {
        int s = 3*P + j;
        if (fsrc_orb[j] >= 0) {
            for (int m = 0; m < 3; m++) nbrow[s][nbdeg[s]++] = 3*fsrc_orb[j] + m;
            nbrow[s][nbdeg[s]++] = 3*K + fsrc_f[j][0];
        } else {
            for (int i = 0; i < 4; i++) nbrow[s][nbdeg[s]++] = 3*K + fsrc_f[j][i];
        }
    }
    int aid = 0;
    for (int t = 0; t < NT; t++) { innb_[t] = 0; inarc_n[t] = 0; }
    for (int s = 0; s < NS; s++) {
        if (nbdeg[s] != 4) return 0;
        for (int j = 0; j < 4; j++) {
            int t = nbrow[s][j];
            if (inarc_n[t] >= 3) return 0;
            innb_[t] |= 1 << s;
            inarc_src[t][inarc_n[t]] = s; inarc_id[t][inarc_n[t]++] = aid++;
        }
    }
    for (int t = 0; t < NT; t++) if (inarc_n[t] != 3) return 0;
    return 1;
}

static int sweep(void){
    ntight = 0;
    for (int t = 0; t < NT; t++) {
        uint64_t msk = 0;
        for (int j = 0; j < 3; j++) msk |= 1ULL << inarc_id[t][j];
        tight[ntight++] = msk;
    }
    int full = (1 << NS) - 1;
    for (int X = 1; X < full; X++) {
        int sz = 0; uint64_t msk = 0;
        for (int t = 0; t < NT; t++) {
            if ((innb_[t] & ~X) == 0) continue;
            for (int j = 0; j < 3; j++)
                if ((X >> inarc_src[t][j]) & 1) { sz++; msk |= 1ULL << inarc_id[t][j]; }
            if (sz > 3) break;
        }
        if (sz == 0) continue;
        if (sz < 3) return -1;
        if (sz == 3 && ntight < 600) tight[ntight++] = msk;
    }
    return ntight;
}

static int verify_all(uint64_t *out){
    int full = (1 << NS) - 1;
    for (int X = 1; X < full; X++) {
        int seen = 0, any = 0; uint64_t msk = 0;
        for (int t = 0; t < NT; t++) {
            if ((innb_[t] & ~X) == 0) continue;
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
    uint64_t work[700]; int nwork = ntight < 600 ? ntight : 600;
    memcpy(work, tight, nwork * sizeof(uint64_t));
    for (int restart = 0; restart < 6; restart++) {
        for (int i = 0; i < NA; i++)
            arc_color[i] = (restart == 0) ? i % 3 : (int)(rnd() % 3);
        for (int cegar = 0; cegar < 12; cegar++) {
            uint64_t colmask[3];
            for (int step = 0; step < 4000; step++) {
                colmask[0] = colmask[1] = colmask[2] = 0;
                for (int i = 0; i < NA; i++) colmask[arc_color[i]] |= 1ULL << i;
                int vio = -1, misscol = -1;
                for (int c = 0; c < nwork && vio < 0; c++)
                    for (int kk = 0; kk < 3; kk++)
                        if ((work[c] & colmask[kk]) == 0) { vio = c; misscol = kk; break; }
                if (vio < 0) break;
                int ids[48], nid = 0;
                for (int i = 0; i < NA; i++)
                    if (work[vio] & (1ULL << i)) ids[nid++] = i;
                arc_color[ids[rnd() % nid]] = misscol;
            }
            uint64_t colmask2[3] = {0,0,0};
            for (int i = 0; i < NA; i++) colmask2[arc_color[i]] |= 1ULL << i;
            int ok = 1;
            for (int c = 0; c < nwork && ok; c++)
                for (int kk = 0; kk < 3; kk++)
                    if ((work[c] & colmask2[kk]) == 0) { ok = 0; break; }
            if (!ok) break;
            uint64_t bad;
            if (verify_all(&bad)) return 1;
            if (nwork < 700) work[nwork++] = bad;
        }
    }
    return 0;
}

static void dump_candidate(void){
    printf("NCAND p=%d f=%d nbrs=", P, F);
    for (int s = 0; s < NS; s++)
        for (int j = 0; j < 4; j++)
            printf("%d%c", nbrow[s][j], j < 3 ? ',' : (s+1 < NS ? ';' : '\n'));
    fflush(stdout);
}

static long long debug_n = 0;

static void process(void){
    cand++;
    if (MODE == 0) return;
    if (!build_graph()) { fprintf(stderr, "BUG: build failed\n"); exit(1); }
    int st = sweep();
    int t3 = (st >= 0), pk = 0;
    if (!t3) tau_reject++;
    else {
        sat_needed++;
        if (try_pack()) { packed++; pk = 1; }
        else { dumped++; dump_candidate(); }
    }
    if (debug_n > 0) {
        debug_n--;
        printf("NDBG tau3=%d packed=%d nbrs=", t3, pk);
        for (int s = 0; s < NS; s++)
            for (int j = 0; j < 4; j++)
                printf("%d%c", nbrow[s][j], j < 3 ? ',' : (s+1 < NS ? ';' : '\n'));
    }
}

/* ---- enumeration ---- */
/* offsets for cmat entries: rotation dedup on each sink-orbit column b:
 * require first nonzero-|S| row's subset to be rotation-minimal. */
static const int subs_by_size[4][3] = { {0,0,0}, {1,2,4}, {3,5,6}, {7,7,7} };
static const int nsubs_by_size[4] = {1, 3, 3, 1};
static int rotmin(int s){ /* is subset s minimal among its Z3 rotations */
    int r1 = ((s << 1) | (s >> 2)) & 7, r2 = ((s << 2) | (s >> 1)) & 7;
    return s <= r1 && s <= r2;
}

static void rec_offsets(int idx, int pairs[][2], int npairs, int firstrow[6]){
    if (idx == npairs) { process(); return; }
    int a = pairs[idx][0], b = pairs[idx][1], c = cmat[a][b];
    for (int i = 0; i < nsubs_by_size[c]; i++) {
        int s = subs_by_size[c][i];
        if (a == firstrow[b] && !rotmin(s)) continue;
        Sab[a][b] = s;
        rec_offsets(idx + 1, pairs, npairs, firstrow);
    }
}

static void enum_offsets(void){
    int pairs[24][2], npairs = 0, firstrow[6];
    for (int b = 0; b < K; b++) firstrow[b] = -1;
    for (int a = 0; a < P; a++)
        for (int b = 0; b < K; b++) {
            Sab[a][b] = 0;
            if (cmat[a][b] > 0) {
                if (firstrow[b] < 0 && cmat[a][b] < 3) firstrow[b] = a;
                pairs[npairs][0] = a; pairs[npairs][1] = b; npairs++;
            }
        }
    rec_offsets(0, pairs, npairs, firstrow);
}

/* fixed sources: assign each its target choice; canonical: non-decreasing encoded
 * choice id across fixed sources (they are interchangeable). */
static int nchoice; static int ch_orb[4096], ch_f[4096][4];
static void gen_choices(void){
    nchoice = 0;
    /* (sink orbit b, fixed sink t with own[t]==P) */
    for (int b = 0; b < K; b++)
        for (int t = 0; t < F; t++)
            if (own[t] == P) { ch_orb[nchoice] = b; ch_f[nchoice][0] = t; nchoice++; }
    /* 4 distinct fixed sinks all with own==P */
    int ts[16], nts = 0;
    for (int t = 0; t < F; t++) if (own[t] == P) ts[nts++] = t;
    for (int i = 0; i < nts; i++) for (int j = i+1; j < nts; j++)
        for (int l = j+1; l < nts; l++) for (int m = l+1; m < nts; m++) {
            ch_orb[nchoice] = -1;
            ch_f[nchoice][0] = ts[i]; ch_f[nchoice][1] = ts[j];
            ch_f[nchoice][2] = ts[l]; ch_f[nchoice][3] = ts[m];
            nchoice++;
        }
}

static int findeg[16]; /* arcs to fixed sink t from fixed sources */

static long long fsrc_ctr;
static int FSHARD_DEPTH = 3;

static void rec_fsrc(int j, int lo){
    if (j == FSHARD_DEPTH && j < Q && NSHARDS > 1 && (fsrc_ctr++ % NSHARDS) != SHARD)
        return;
    if (j == Q) {
        /* every 3fixed-src sink must have exactly 3 arcs */
        for (int t = 0; t < F; t++)
            if (own[t] == P && findeg[t] != 3) return;
        /* column sums: e_b already checked incrementally == final; verify */
        for (int b = 0; b < K; b++) {
            int s = e_b[b];
            for (int a = 0; a < P; a++) s += cmat[a][b];
            if (s != 3) return;
        }
        enum_offsets();
        return;
    }
    for (int c = lo; c < nchoice; c++) {
        int b = ch_orb[c];
        if (b >= 0) {
            int s = e_b[b];
            for (int a = 0; a < P; a++) s += cmat[a][b];
            if (s + 1 > 3) continue;
            if (findeg[ch_f[c][0]] + 1 > 3) continue;
            e_b[b]++; findeg[ch_f[c][0]]++;
            fsrc_orb[j] = b; fsrc_f[j][0] = ch_f[c][0];
            rec_fsrc(j + 1, c);
            e_b[b]--; findeg[ch_f[c][0]]--;
        } else {
            int ok = 1;
            for (int i = 0; i < 4; i++) if (findeg[ch_f[c][i]] + 1 > 3) ok = 0;
            if (!ok) continue;
            for (int i = 0; i < 4; i++) findeg[ch_f[c][i]]++;
            fsrc_orb[j] = -1; memcpy(fsrc_f[j], ch_f[c], sizeof(fsrc_f[j]));
            rec_fsrc(j + 1, c);
            for (int i = 0; i < 4; i++) findeg[ch_f[c][i]]--;
        }
    }
}

/* cmat rows: row sum r_a = 4 - (#fixed sinks owned by orbit a) */
static int rowsum[4];
static long long shard_ctr;

static void rec_cmat(int a, int b, int left){
    if (a == P) {
        /* shard at cmat level only when fsrc-level sharding is unavailable */
        if (Q <= FSHARD_DEPTH && NSHARDS > 1 && (shard_ctr++ % NSHARDS) != SHARD)
            return;
        for (int bb = 0; bb < K; bb++) { e_b[bb] = 0; }
        memset(findeg, 0, sizeof(findeg));
        gen_choices();
        if (Q > 0 && nchoice == 0) {
            /* fixed sources need targets; also all-orbit-owned fixed sinks with
             * Q>0 impossible only if no choices — but a fixed source could still
             * pick (orbit, fixed sink) only if some own[t]==P. So skip. */
            return;
        }
        rec_fsrc(0, 0);
        return;
    }
    if (b == K) {
        if (left == 0) rec_cmat(a + 1, 0, a + 1 < P ? rowsum[a + 1] : 0);
        return;
    }
    int colused = 0;
    for (int aa = 0; aa < a; aa++) colused += cmat[aa][b];
    int maxc = 3 - colused; if (maxc > left) maxc = left; if (maxc > 3) maxc = 3;
    for (int c = 0; c <= maxc; c++) {
        cmat[a][b] = c;
        rec_cmat(a, b + 1, left - c);
    }
    cmat[a][b] = 0;
}

/* owners of fixed sinks: own[t] in {0..P-1} (orbit-owned) or P (3 fixed sources).
 * canonical: non-decreasing own[] (fixed sinks interchangeable). */
static void rec_owners(int t, int lo){
    if (t == F) {
        /* row sums for orbit sources */
        for (int a = 0; a < P; a++) {
            int o = 0;
            for (int tt = 0; tt < F; tt++) if (own[tt] == a) o++;
            rowsum[a] = 4 - o;
            if (rowsum[a] < 0) return;
        }
        /* count arcs sanity: 3*sum rowsum + 3*#orbitowned + 4Q = 48 auto */
        /* #3fixed sinks * 3 must be supplied by fixed sources:
         * fixed sources supply Q*1 (orb-type, to one fixed sink) .. Q*4 arcs */
        int n3f = 0;
        for (int tt = 0; tt < F; tt++) if (own[tt] == P) n3f++;
        if (3 * n3f > 4 * Q) return;
        /* each fixed source needs >=1 fixed-sink arc, all to own==P sinks */
        if (Q > 0 && n3f == 0) return;
        rec_cmat(0, 0, P > 0 ? rowsum[0] : 0);
        return;
    }
    for (int o = lo; o <= P; o++) {
        own[t] = o;
        rec_owners(t + 1, o);
    }
}

int main(int argc, char **argv){
    P = atoi(argv[1]); F = atoi(argv[2]); MODE = atoi(argv[3]);
    SHARD = argc > 4 ? atoi(argv[4]) : 0;
    NSHARDS = argc > 5 ? atoi(argv[5]) : 1;
    if (MODE == 2) debug_n = 300;
    Q = 12 - 3 * P; K = (16 - F) / 3;
    if (Q <= 0 || F < 1 || (16 - F) % 3) { fprintf(stderr, "bad p/f\n"); return 1; }
    rec_owners(0, 0);
    fprintf(stderr,
        "DONE p=%d q=%d k=%d f=%d mode=%d shard=%d/%d cand=%lld tau_reject=%lld "
        "sat=%lld packed=%lld dumped=%lld\n",
        P, Q, K, F, MODE, SHARD, NSHARDS, cand, tau_reject, sat_needed, packed, dumped);
    return 0;
}
