/* P21 v1 phase 2: exact-cover / packing search over enumerated C7-invariant
 * HoSi copies (each = 25 of 175 edge orbits, bitmask of 3 x u64).
 * Usage: cover <copies_file> <k> [out_file]
 *   k=7: exact cover of all 175 orbits by 7 disjoint copies (Algorithm X style,
 *        branch on uncovered orbit with fewest candidates).
 *   k=6: find 6 pairwise disjoint copies (classes = fixed-vertex orbit; each
 *        copy contains exactly one orbit through vertex 49; choose 6 classes).
 * Fixed-vertex orbits are the 7 orbits containing vertex 49, passed via env
 * FV_ORBITS="a b c d e f g" (or auto-read orbits file). Here we just take them
 * as the 7 orbit indices that appear in copies as their unique fv orbit; we
 * receive them on the command line after out_file if needed. For simplicity:
 * we detect classes by intersecting each copy with the fv orbit set read from
 * file "fv_orbits.txt" (7 ints).
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define W 3
typedef struct { uint64_t b[W]; int fv; } Copy;

static Copy *copies; static int ncop;
static int fv[7];

static inline int disj(const uint64_t *a, const uint64_t *b){
    return !((a[0]&b[0])|(a[1]&b[1])|(a[2]&b[2]));
}

static int chosen[8]; static int nch;
static uint64_t uni[W];
/* per-orbit candidate lists */
static int **byorb; static int *byorbn;

static long long nodes = 0;

static int solve7(void){
    /* find uncovered orbit with fewest disjoint candidates */
    if (nch == 7) return 1;
    int best = -1, bestn = 1<<30;
    for (int o = 0; o < 175; o++){
        if (uni[o>>6]>>(o&63)&1) continue;
        int cnt = 0;
        for (int i = 0; i < byorbn[o]; i++){
            Copy *c = &copies[byorb[o][i]];
            if (disj(c->b, uni)) cnt++;
        }
        if (cnt == 0) return 0;
        if (cnt < bestn){ bestn = cnt; best = o; if (cnt==1) break; }
    }
    for (int i = 0; i < byorbn[best]; i++){
        int ci = byorb[best][i];
        Copy *c = &copies[ci];
        if (!disj(c->b, uni)) continue;
        nodes++;
        if ((nodes & 0xFFFFF) == 0){ fprintf(stderr, "nodes %lld depth %d\n", nodes, nch); }
        for (int w=0;w<W;w++) uni[w] |= c->b[w];
        chosen[nch++] = ci;
        if (solve7()) return 1;
        nch--;
        for (int w=0;w<W;w++) uni[w] &= ~c->b[w];
    }
    return 0;
}

/* k=6: pick copies from 6 of the 7 fv classes, pairwise disjoint */
static int *cls[7]; static int clsn[7];
static int skipcls; static int target;
static int solve6(int ci){
    if (nch == target) return 1;
    if (ci == skipcls) ci++;
    if (ci > 6) return 0;
    for (int i = 0; i < clsn[ci]; i++){
        int idx = cls[ci][i];
        Copy *c = &copies[idx];
        if (!disj(c->b, uni)) continue;
        nodes++;
        if ((nodes & 0xFFFFFF) == 0) fprintf(stderr, "nodes %lld depth %d cls %d\n", nodes, nch, ci);
        for (int w=0;w<W;w++) uni[w] |= c->b[w];
        chosen[nch++] = idx;
        if (solve6(ci+1)) return 1;
        nch--;
        for (int w=0;w<W;w++) uni[w] &= ~c->b[w];
    }
    return 0;
}

int main(int argc, char **argv){
    FILE *f = fopen(argv[1], "r");
    int k = atoi(argv[2]);
    FILE *fvf = fopen("fv_orbits.txt", "r");
    for (int i=0;i<7;i++) if(fscanf(fvf, "%d", &fv[i])!=1){fprintf(stderr,"bad fv\n");return 2;}
    fclose(fvf);
    size_t cap = 1<<20; copies = malloc(cap*sizeof(Copy));
    char line[4096];
    while (fgets(line, sizeof line, f)){
        if (ncop == (int)cap){ cap*=2; copies = realloc(copies, cap*sizeof(Copy)); }
        Copy *c = &copies[ncop]; memset(c, 0, sizeof *c); c->fv = -1;
        char *p = line; int o, cnt=0;
        while (sscanf(p, "%d", &o) == 1){
            c->b[o>>6] |= 1ULL<<(o&63); cnt++;
            for (int i=0;i<7;i++) if (o==fv[i]) c->fv = i;
            while (*p==' '||*p=='\t') p++;
            while (*p && *p!=' ' && *p!='\t' && *p!='\n') p++;
            while (*p==' ') p++;
            if (*p=='\n'||!*p) break;
        }
        if (cnt != 25 || c->fv < 0){ fprintf(stderr, "bad line %d cnt=%d fv=%d\n", ncop, cnt, c->fv); return 2; }
        ncop++;
    }
    fclose(f);
    fprintf(stderr, "%d copies\n", ncop);
    if (k == 7){
        for (int i=0;i<7;i++){ cls[i]=malloc(ncop*sizeof(int)); clsn[i]=0; }
        for (int i=0;i<ncop;i++) cls[copies[i].fv][clsn[copies[i].fv]++]=i;
        for (int i=0;i<7;i++) fprintf(stderr, "class %d: %d\n", i, clsn[i]);
        target = 7; skipcls = -1;
        memset(uni,0,sizeof uni); nch=0; nodes=0;
        if (solve6(0)){
            printf("FOUND 7-DECOMPOSITION\n");
            for (int i=0;i<7;i++) printf("copy %d\n", chosen[i]);
        } else printf("NO 7-decomposition among given copies (nodes=%lld)\n", nodes);
    } else {
        target = 6;
        for (int i=0;i<7;i++){ cls[i]=malloc(ncop*sizeof(int)); clsn[i]=0; }
        for (int i=0;i<ncop;i++) cls[copies[i].fv][clsn[copies[i].fv]++]=i;
        for (int i=0;i<7;i++) fprintf(stderr, "class %d: %d\n", i, clsn[i]);
        for (skipcls = 6; skipcls >= 0; skipcls--){
            memset(uni,0,sizeof uni); nch=0; nodes=0;
            if (solve6(0)){
                printf("FOUND 6-PACKING (skipping class %d)\n", skipcls);
                for (int i=0;i<6;i++) printf("copy %d\n", chosen[i]);
                goto done;
            }
            fprintf(stderr, "no 6-packing skipping class %d (nodes=%lld)\n", skipcls, nodes);
        }
        printf("NO 6-packing among given copies\n");
    }
done:
    if (argc > 3 && nch > 0){
        FILE *out = fopen(argv[3], "w");
        for (int i=0;i<nch;i++){
            for (int o=0;o<175;o++) if (copies[chosen[i]].b[o>>6]>>(o&63)&1)
                fprintf(out, "%d %d\n", i, o);
        }
        fclose(out);
    }
    return 0;
}
