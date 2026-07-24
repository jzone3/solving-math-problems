/* Massive annealed sampling of the full (asymmetric) ACZ-complete minimal-shape
 * region for tau=3 Woodall counterexamples.
 *
 * Shapes: nS sources (n4 of degree 4, n3 of degree 3), nT = (4*n4+3*n3)/3 sinks of
 * in-degree 3, nS <= 16, arcs <= 64. Search: random config-model start, degree-
 * preserving double-swap mutations, hill-climb on tight-dicut count with random
 * restarts. Every tau=3 candidate gets a CERTIFIED packing decision: WalkSAT
 * 3-coloring + full-verification CEGAR (as in zscan.c); unresolved candidates are
 * printed for exact SAT verification in Python (averify.py handles "ACAND" lines).
 *
 * Usage: ascan n4 n3 seed minutes [debug_print_first_N]
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

static int N4, N3, NS, NT, NA;
static int nbr[16][4], deg[16];       /* source -> targets */
static unsigned rng_state;
static unsigned rnd(void){ rng_state ^= rng_state<<13; rng_state ^= rng_state>>17;
    rng_state ^= rng_state<<5; return rng_state; }

static int innb_[24];                  /* sink -> source bitmask */
static int inarc_src[24][3], inarc_id[24][3], inarc_n[24];
static int arc_color[64];
static uint64_t tight[900]; static int ntight;

static long long iters, tau3_cnt, packed_cnt, dumped;
static long long debug_n;

static int build_arcs(void){          /* returns 0 if some sink indeg != 3 */
    int aid = 0;
    for (int t = 0; t < NT; t++) { innb_[t] = 0; inarc_n[t] = 0; }
    for (int s = 0; s < NS; s++)
        for (int j = 0; j < deg[s]; j++) {
            int t = nbr[s][j];
            if (inarc_n[t] >= 3) return 0;
            innb_[t] |= 1 << s;
            inarc_src[t][inarc_n[t]] = s; inarc_id[t][inarc_n[t]++] = aid++;
        }
    for (int t = 0; t < NT; t++) if (inarc_n[t] != 3) return 0;
    return 1;
}

/* sweep over all X: returns -1 if tau<3, else number of tight cuts (collected) */
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
                if ((X >> inarc_src[t][j]) & 1) {
                    sz++; msk |= 1ULL << inarc_id[t][j];
                }
            if (sz > 3) break;
        }
        if (sz == 0) continue;
        if (sz < 3) return -1;
        if (sz == 3 && ntight < 900) tight[ntight++] = msk;
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
    uint64_t work[1000]; int nwork = ntight < 900 ? ntight : 900;
    memcpy(work, tight, nwork * sizeof(uint64_t));
    for (int restart = 0; restart < 5; restart++) {
        for (int i = 0; i < NA; i++)
            arc_color[i] = (restart == 0) ? i % 3 : (int)(rnd() % 3);
        for (int cegar = 0; cegar < 10; cegar++) {
            uint64_t colmask[3];
            for (int step = 0; step < 3000; step++) {
                colmask[0] = colmask[1] = colmask[2] = 0;
                for (int i = 0; i < NA; i++) colmask[arc_color[i]] |= 1ULL << i;
                int vio = -1, misscol = -1;
                for (int c = 0; c < nwork && vio < 0; c++)
                    for (int kk = 0; kk < 3; kk++)
                        if ((work[c] & colmask[kk]) == 0) { vio = c; misscol = kk; break; }
                if (vio < 0) break;
                int ids[64], nid = 0;
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
            if (nwork < 1000) work[nwork++] = bad;
        }
    }
    return 0;
}

static void dump_candidate(void){
    printf("ACAND n4=%d n3=%d nbrs=", N4, N3);
    for (int s = 0; s < NS; s++) {
        for (int j = 0; j < deg[s]; j++) printf("%d%c", nbr[s][j],
            j+1 < deg[s] ? ',' : (s+1 < NS ? ';' : '\n'));
    }
    fflush(stdout);
}

static int has_target(int s, int t){
    for (int j = 0; j < deg[s]; j++) if (nbr[s][j] == t) return 1;
    return 0;
}

static void random_start(void){
    /* config model: shuffle sink stubs (3 per sink), retry until simple */
    int stubs[64];
    for (;;) {
        int n = 0;
        for (int t = 0; t < NT; t++) for (int j = 0; j < 3; j++) stubs[n++] = t;
        for (int i = n-1; i > 0; i--) {
            int j = rnd() % (i+1); int tmp = stubs[i]; stubs[i] = stubs[j]; stubs[j] = tmp;
        }
        int k = 0, ok = 1;
        for (int s = 0; s < NS && ok; s++) {
            for (int j = 0; j < deg[s]; j++) {
                nbr[s][j] = stubs[k++];
                for (int j2 = 0; j2 < j; j2++) if (nbr[s][j2] == nbr[s][j]) ok = 0;
            }
        }
        if (ok) return;
    }
}

static int score_and_check(void){     /* returns score, does certified check */
    if (!build_arcs()) return -1000000;
    int st = sweep();
    iters++;
    int t3 = (st >= 0), pk = 0;
    if (t3) {
        tau3_cnt++;
        if (try_pack()) { packed_cnt++; pk = 1; }
        else { dumped++; dump_candidate(); }
    }
    if (debug_n > 0) {
        debug_n--;
        printf("ADBG tau3=%d packed=%d n4=%d n3=%d nbrs=", t3, pk, N4, N3);
        for (int s = 0; s < NS; s++)
            for (int j = 0; j < deg[s]; j++) printf("%d%c", nbr[s][j],
                j+1 < deg[s] ? ',' : (s+1 < NS ? ';' : '\n'));
    }
    if (!t3) return -1;
    return st;                        /* tight-cut count as score */
}

int main(int argc, char **argv){
    N4 = atoi(argv[1]); N3 = atoi(argv[2]);
    rng_state = (unsigned)atoi(argv[3]) * 2654435761u + 12345u;
    double minutes = atof(argv[4]);
    debug_n = argc > 5 ? atoll(argv[5]) : 0;
    NS = N4 + N3; NA = 4*N4 + 3*N3; NT = NA / 3;
    if (NA % 3 || NS > 16 || NT > 24) { fprintf(stderr, "bad shape\n"); return 1; }
    for (int s = 0; s < NS; s++) deg[s] = s < N4 ? 4 : 3;
    time_t t0 = time(NULL);
    long long restarts = 0;
    while (time(NULL) - t0 < (time_t)(minutes * 60)) {
        restarts++;
        random_start();
        int cur = score_and_check();
        for (int stale = 0; stale < 400; stale++) {
            if (time(NULL) - t0 >= (time_t)(minutes * 60)) break;
            /* double swap: arcs (s1,t1),(s2,t2) -> (s1,t2),(s2,t1) */
            int s1 = rnd() % NS, s2 = rnd() % NS;
            if (s1 == s2) continue;
            int j1 = rnd() % deg[s1], j2 = rnd() % deg[s2];
            int t1 = nbr[s1][j1], t2 = nbr[s2][j2];
            if (t1 == t2 || has_target(s1, t2) || has_target(s2, t1)) continue;
            nbr[s1][j1] = t2; nbr[s2][j2] = t1;
            int sc = score_and_check();
            if (sc >= cur) { if (sc > cur) stale = 0; cur = sc; }
            else { nbr[s1][j1] = t1; nbr[s2][j2] = t2; }
        }
    }
    fprintf(stderr, "DONE n4=%d n3=%d restarts=%lld iters=%lld tau3=%lld packed=%lld dumped=%lld\n",
            N4, N3, restarts, iters, tau3_cnt, packed_cnt, dumped);
    return 0;
}
