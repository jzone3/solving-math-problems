/* P04 V2 frontier push: verify Hajos' conjecture for order-13 graphs.
 *
 * Input: graph6 lines on stdin, each a graph H on NH=12 vertices (from
 *   geng -c -d5 12). We reconstruct candidate order-13 graphs G = H + w,
 *   where w is a new vertex joined to all odd-degree vertices of H.
 *
 * Rationale (see NOTES.md): a minimum counterexample G of order 13 is
 * 2-connected, has all degrees even, and at most one vertex of degree < 6
 * (that vertex having degree 4; degree-2 vertices are impossible by vertex
 * suppression + the verified n<=12 case). Deleting the degree-4 vertex (or
 * any vertex, if delta(G)>=6) yields a connected graph H on 12 vertices
 * with delta(H) >= 5, and G is recovered from H by joining a new vertex to
 * the odd-degree vertices of H. Hence enumerating all connected H with
 * delta >= 5 and extending covers every candidate G (with duplicates,
 * which is harmless).
 *
 * For each candidate G we search for a decomposition into <= 6 edge-disjoint
 * cycles (floor((13-1)/2) = 6) using randomized long-cycle peeling.  Every
 * found decomposition is re-verified exactly (partition of E(G) into cycles)
 * before the graph is counted as OK.  Graphs where the heuristic fails
 * within the attempt budget are printed to stdout (graph6 of G, n=13) for
 * exact treatment by ILP.
 *
 * Compile: gcc -O3 -march=native -o hajos_check hajos_check.c
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define NH 12
#define NG 13
#define MAXE 78
#define BOUND 6            /* floor((13-1)/2) */
#define ATTEMPTS 300

typedef uint16_t bs;       /* bitset over <=13 vertices */

static uint64_t rng_state = 0x9e3779b97f4a7c15ULL;
static inline uint64_t rng(void){
    uint64_t x = rng_state; x ^= x<<13; x ^= x>>7; x ^= x<<17;
    return rng_state = x;
}
static inline int rnd(int m){ return (int)(rng() % (uint64_t)m); }

/* ---- graph6 decode for n=12 ---- */
static int decode_g6(const char *s, bs adj[NH]){
    if (s[0]-63 != NH) return -1;
    memset(adj,0,sizeof(bs)*NH);
    int need = (NH*(NH-1)/2 + 5)/6;   /* 11 chars */
    int bitpos = 0;
    for (int k = 0; k < need; k++){
        int c = s[1+k];
        if (c < 63 || c > 126) return -1;
        c -= 63;
        for (int b = 5; b >= 0; b--){
            if (bitpos >= NH*(NH-1)/2) break;
            if ((c>>b)&1){
                /* column-major upper triangle: edge (i,j), j>i */
                int p = bitpos, j = 1;
                while (p >= j) { p -= j; j++; }
                int i = p;
                adj[i] |= (bs)1<<j; adj[j] |= (bs)1<<i;
            }
            bitpos++;
        }
    }
    return 0;
}

/* ---- graph6 encode for n=13 ---- */
static void encode_g6(bs adj[NG], char *out){
    int need = (NG*(NG-1)/2 + 5)/6; /* 13 */
    out[0] = 63 + NG;
    int bitpos = 0;
    for (int k = 0; k < need; k++){
        int c = 0;
        for (int b = 5; b >= 0; b--){
            if (bitpos < NG*(NG-1)/2){
                int p = bitpos, j = 1;
                while (p >= j){ p -= j; j++; }
                int i = p;
                if (adj[i] & ((bs)1<<j)) c |= 1<<b;
            }
            bitpos++;
        }
        out[1+k] = 63 + c;
    }
    out[1+need] = 0;
}

static inline int popc(bs x){ return __builtin_popcount((unsigned)x); }

/* connectivity of G (13 vertices, all present) */
static int connected(bs adj[NG]){
    bs seen = 1, frontier = 1;
    while (frontier){
        bs nxt = 0;
        while (frontier){
            int v = __builtin_ctz((unsigned)frontier);
            frontier &= frontier-1;
            nxt |= adj[v];
        }
        frontier = nxt & ~seen;
        seen |= nxt;
    }
    return seen == ((bs)1<<NG)-1;
}

/* 2-connectivity: connected and no cutvertex (brute: remove each v) */
static int biconnected(bs adj[NG]){
    if (!connected(adj)) return 0;
    for (int v = 0; v < NG; v++){
        bs mask = (((bs)1<<NG)-1) & ~((bs)1<<v);
        int s = __builtin_ctz((unsigned)mask);
        bs seen = (bs)1<<s, frontier = seen;
        while (frontier){
            bs nxt = 0;
            while (frontier){
                int u = __builtin_ctz((unsigned)frontier);
                frontier &= frontier-1;
                nxt |= adj[u];
            }
            nxt &= mask;
            frontier = nxt & ~seen;
            seen |= nxt;
        }
        if (seen != mask) return 0;
    }
    return 1;
}

/* ---- randomized long-cycle peeling ----
 * work[]: current residual adjacency. Random walk; keep "on path" positions;
 * when an edge closes a cycle, record the longest closable cycle; prefer to
 * continue walking. Returns cycle as vertex list in cyc[], length ret.
 */
static int random_long_cycle(bs work[NG], int cyc[NG+1]){
    int path[MAXE+2]; int plen = 0;
    int pos[NG]; for (int i = 0; i < NG; i++) pos[i] = -1;
    /* start vertex: random among those with positive degree */
    int cand[NG], nc = 0;
    for (int v = 0; v < NG; v++) if (work[v]) cand[nc++] = v;
    if (!nc) return 0;
    int v = cand[rnd(nc)];
    path[plen] = v; pos[v] = plen; plen++;
    bs used_at[NG]; memset(used_at,0,sizeof used_at); /* edges used from each vertex on this walk */
    int bestlen = 0, beststart = -1;
    for (;;){
        bs nb = work[v] & ~used_at[v];
        /* neighbours that do NOT close a cycle (not on path except allow closing) */
        bs closing = 0, open = 0;
        bs t = nb;
        while (t){
            int u = __builtin_ctz((unsigned)t); t &= t-1;
            if (pos[u] >= 0 && plen - pos[u] >= 3) closing |= (bs)1<<u;
            else if (pos[u] < 0) open |= (bs)1<<u;
        }
        /* record best closing cycle available right now */
        t = closing;
        while (t){
            int u = __builtin_ctz((unsigned)t); t &= t-1;
            int len = plen - pos[u];
            if (len > bestlen){ bestlen = len; beststart = pos[u]; }
        }
        if (open){
            /* continue walk on a random open neighbour */
            int cntb = popc(open);
            int pick = rnd(cntb);
            t = open; int u = -1;
            while (pick-- >= 0){ u = __builtin_ctz((unsigned)t); t &= t-1; }
            used_at[v] |= (bs)1<<u; used_at[u] |= (bs)1<<v;
            path[plen] = u; pos[u] = plen; plen++;
            v = u;
        } else {
            break; /* stuck: take best cycle seen (may be via current closing) */
        }
    }
    if (bestlen < 3) return 0;
    for (int i = 0; i < bestlen; i++) cyc[i] = path[beststart + i];
    return bestlen;
}

/* try to decompose G into <= BOUND cycles; on success fills sol (list of
 * cycles) and returns number of cycles, else 0. */
static int try_decompose(bs adj[NG], int m,
                         int sol[BOUND][NG+1], int sollen[BOUND]){
    bs work[NG]; memcpy(work,adj,sizeof work);
    int rem = m, ncyc = 0;
    int cyc[NG+1];
    while (rem > 0){
        if (ncyc >= BOUND) return 0;
        /* remaining edges must fit in remaining cycles (max NG per cycle) */
        if (rem > (BOUND-ncyc)*NG) return 0;
        int len = random_long_cycle(work, cyc);
        if (len < 3) return 0;
        for (int i = 0; i < len; i++){
            int a = cyc[i], b = cyc[(i+1)%len];
            work[a] &= ~((bs)1<<b); work[b] &= ~((bs)1<<a);
        }
        memcpy(sol[ncyc], cyc, sizeof(int)*len);
        sollen[ncyc] = len;
        ncyc++;
        rem -= len;
    }
    return ncyc;
}

/* exact re-verification of a claimed decomposition */
static int verify_decomposition(bs adj[NG], int m,
                                int sol[BOUND][NG+1], int sollen[BOUND],
                                int ncyc){
    bs left[NG]; memcpy(left,adj,sizeof left);
    int tot = 0;
    for (int c = 0; c < ncyc; c++){
        int len = sollen[c];
        if (len < 3) return 0;
        bs seenv = 0;
        for (int i = 0; i < len; i++){
            int a = sol[c][i], b = sol[c][(i+1)%len];
            if (a < 0 || a >= NG) return 0;
            if (seenv & ((bs)1<<a)) return 0;   /* vertex repeat -> not a cycle */
            seenv |= (bs)1<<a;
            if (!(left[a] & ((bs)1<<b))) return 0; /* edge absent or reused */
            left[a] &= ~((bs)1<<b); left[b] &= ~((bs)1<<a);
            tot++;
        }
    }
    if (tot != m) return 0;
    for (int v = 0; v < NG; v++) if (left[v]) return 0;
    return 1;
}

int main(int argc, char **argv){
    if (argc > 1) rng_state ^= strtoull(argv[1],NULL,10)*0x2545F4914F6CDD1DULL;
    char line[128];
    unsigned long long nread=0, ncand=0, nok=0, nhard=0, nbicon_skip=0;
    bs adjH[NH], adj[NG];
    int sol[BOUND][NG+1], sollen[BOUND];
    while (fgets(line,sizeof line,stdin)){
        nread++;
        if (decode_g6(line, adjH)) continue;
        /* degrees & parity of H */
        bs odd = 0; int ok = 1;
        for (int v = 0; v < NH; v++){
            int d = popc(adjH[v]);
            if (d & 1) odd |= (bs)1<<v;
        }
        int nodd = popc(odd);
        if (nodd < 4) continue;      /* new vertex degree <4: deg 0 disconnected, deg 2 impossible (see NOTES) */
        (void)ok;
        /* build G */
        for (int v = 0; v < NH; v++){
            adj[v] = adjH[v];
            if (odd & ((bs)1<<v)) adj[v] |= (bs)1<<(NG-1);
        }
        adj[NG-1] = odd;
        if (!biconnected(adj)){ nbicon_skip++; continue; }
        ncand++;
        int m = 0;
        for (int v = 0; v < NG; v++) m += popc(adj[v]);
        m /= 2;
        int done = 0;
        for (int t = 0; t < ATTEMPTS && !done; t++){
            int nc = try_decompose(adj, m, sol, sollen);
            if (nc){
                if (!verify_decomposition(adj, m, sol, sollen, nc)){
                    fprintf(stderr,"BUG: invalid decomposition claimed\n");
                    exit(2);
                }
                done = 1;
            }
        }
        if (done) nok++;
        else {
            nhard++;
            char out[32]; encode_g6(adj,out);
            printf("%s\n",out);
            fflush(stdout);
        }
    }
    fprintf(stderr,"read=%llu candidates=%llu ok=%llu hard=%llu bicon_skip=%llu\n",
            nread,ncand,nok,nhard,nbicon_skip);
    return 0;
}
