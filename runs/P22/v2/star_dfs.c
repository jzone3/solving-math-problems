/* Fast DFS over the 42 star-edge variables of vertex 0 with full unit
 * propagation over all 19558 triangle clauses of the G127 arrowing CNF.
 *
 * Enumerates all 2^42 star assignments implicitly; a branch is pruned when
 * unit propagation derives a conflict.  Star assignments that survive to
 * depth 42 are (optionally canonicity-filtered under Stab(0) x flip and)
 * written out as cubes for a kissat + drat-trim finishing pass.
 *
 * Input files (same dir): g127.tri_edges (0-based edge ids per triangle).
 * Edge order matches gen_cnf.py: 42 star edges (0,c) c in C sorted, then rest.
 *
 * Usage: ./star_dfs [max_report_sec] [start_prefix_bits start_prefix_len]
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

#define NV 2667
#define NT 9779
#define NSTAR 42

static int tri[NT][3];
static int *occ[NV];      /* clause indices containing edge v */
static int nocc[NV];
static int8_t val[NV];    /* -1 unknown, 0, 1 */
static int trail[NV];
static int ntrail;

static long long nodes = 0, conflicts = 0, survivors = 0;
static FILE *out;
static time_t t0;

/* group: 84 sequences perm[g][i] = position of image, neg[g] flip flag */
static int P = 127;
static int Cres[NSTAR];
static int posOf[127];
static int perm[84][NSTAR];
static int gneg[84];
static int ngroup = 0;

static void build_group(void) {
    int i, x, isC[127];
    memset(isC, 0, sizeof isC);
    for (x = 1; x < P; x++) isC[(x * x % P) * x % P] = 1;
    int k = 0;
    for (x = 1; x < P; x++) if (isC[x]) Cres[k++] = x;
    for (i = 0; i < NSTAR; i++) posOf[Cres[i]] = i;
    for (i = 0; i < NSTAR; i++) {
        int a = Cres[i], f, j;
        for (f = 0; f < 2; f++) {
            for (j = 0; j < NSTAR; j++)
                perm[ngroup][j] = posOf[(int)((long long)a * Cres[j] % P)];
            gneg[ngroup] = f;
            ngroup++;
        }
    }
}

/* return 1 if star assignment s (bits s[0..41]) is lex-min among images */
static int canonical(const int8_t *s) {
    int g, j;
    for (g = 0; g < ngroup; g++) {
        if (gneg[g] == 0 && perm[g][0] == 0) {
            /* identity check below still fine */
        }
        for (j = 0; j < NSTAR; j++) {
            int img = s[perm[g][j]] ^ gneg[g];
            if (img < s[j]) goto smaller;   /* image lex-smaller: not canonical */
            if (img > s[j]) goto next_g;
        }
        continue;      /* equal image */
smaller:
        return 0;
next_g: ;
    }
    return 1;
}

static int assign(int v, int b);

/* propagate assignment v=b; returns 0 on conflict */
static int propagate_from(int start) {
    int qi = start;
    while (qi < ntrail) {
        int v = trail[qi++];
        int b = val[v];
        for (int k = 0; k < nocc[v]; k++) {
            int c = occ[v][k];
            /* clause pair semantics: triangle edges e1,e2,e3 must not be all
             * equal.  If two are assigned equal and third assigned equal ->
             * conflict; if two equal and third unknown -> force different. */
            int *e = tri[c];
            int a0 = val[e[0]], a1 = val[e[1]], a2 = val[e[2]];
            int nu = (a0 < 0) + (a1 < 0) + (a2 < 0);
            if (nu == 0) {
                if (a0 == a1 && a1 == a2) return 0;
            } else if (nu == 1) {
                int u, w1, w2;
                if (a0 < 0) { u = e[0]; w1 = a1; w2 = a2; }
                else if (a1 < 0) { u = e[1]; w1 = a0; w2 = a2; }
                else { u = e[2]; w1 = a0; w2 = a1; }
                if (w1 == w2) { if (!assign(u, !w1)) return 0; }
            }
        }
    }
    return 1;
}

static int assign(int v, int b) {
    if (val[v] >= 0) return val[v] == b;
    val[v] = (int8_t)b;
    trail[ntrail++] = v;
    return 1;
}

static void undo_to(int mark) {
    while (ntrail > mark) val[trail[--ntrail]] = -1;
}

static void dfs(int depth) {
    nodes++;
    if ((nodes & 0xfffff) == 0) {
        fprintf(stderr, "t=%lds nodes=%lld conflicts=%lld survivors=%lld depth=%d\n",
                time(NULL) - t0, nodes, conflicts, survivors, depth);
        fflush(stderr);
    }
    /* find next unassigned star var */
    int v = -1;
    for (int i = depth; i < NSTAR; i++) if (val[i] < 0) { v = i; break; }
    if (v < 0) {
        int8_t s[NSTAR];
        for (int i = 0; i < NSTAR; i++) s[i] = val[i];
        if (canonical(s)) {
            survivors++;
            for (int i = 0; i < NSTAR; i++) fputc(s[i] ? '1' : '0', out);
            fputc('\n', out);
            if ((survivors & 0xffff) == 0) fflush(out);
        }
        return;
    }
    for (int b = 0; b < 2; b++) {
        int mark = ntrail;
        if (assign(v, b) && propagate_from(mark)) dfs(v + 1);
        else conflicts++;
        undo_to(mark);
    }
}

int main(int argc, char **argv) {
    t0 = time(NULL);
    build_group();
    FILE *f = fopen("g127.tri_edges", "r");
    if (!f) { perror("g127.tri_edges"); return 1; }
    int cnt[NV]; memset(cnt, 0, sizeof cnt);
    for (int i = 0; i < NT; i++) {
        if (fscanf(f, "%d %d %d", &tri[i][0], &tri[i][1], &tri[i][2]) != 3) return 1;
        cnt[tri[i][0]]++; cnt[tri[i][1]]++; cnt[tri[i][2]]++;
    }
    fclose(f);
    for (int v = 0; v < NV; v++) { occ[v] = malloc(cnt[v] * sizeof(int)); nocc[v] = 0; }
    for (int i = 0; i < NT; i++)
        for (int j = 0; j < 3; j++) { int v = tri[i][j]; occ[v][nocc[v]++] = i; }
    memset(val, -1, sizeof val);
    ntrail = 0;
    out = fopen("star_survivors.txt", "w");
    dfs(0);
    fprintf(stderr, "DONE t=%lds nodes=%lld conflicts=%lld survivors=%lld\n",
            time(NULL) - t0, nodes, conflicts, survivors);
    fclose(out);
    return 0;
}
