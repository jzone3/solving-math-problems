/* P21 v1 phase 2 (v2): packing search with progressive candidate filtering.
 * Usage: cover2 <copies_file> <k in {6,7}> [out_file] [seed]
 * Copies grouped by fixed-vertex-orbit class (7 classes); a k-packing uses k
 * distinct classes (k=7: all; 7 disjoint copies automatically cover all 1225
 * edges, i.e. a decomposition). Recursion: pick the remaining class with the
 * fewest surviving candidates, try each, filter other classes' lists.
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
static int target, skipcls;
static int chosen[8]; static int nch;
static long long nodes;
static int stride=1, offset=0;

/* lists[c] = surviving candidate indices for class c; sizes ln[c]; used[c] flag */
static int solve(int **lists, int *ln, int *used, uint64_t *uni){
    if (nch == target) return 1;
    /* pick unused, non-skipped class with fewest candidates */
    int best=-1, bestn=1<<30;
    for (int c=0;c<7;c++){
        if (used[c] || c==skipcls) continue;
        if (ln[c]==0) return 0;
        if (ln[c]<bestn){bestn=ln[c];best=c;}
    }
    int *mylist = lists[best]; int myn = ln[best];
    used[best]=1;
    int step = (nch==0)?stride:1;
    for (int i=(nch==0)?offset:0;i<myn;i+=step){
        Copy *c = &copies[mylist[i]];
        if (!disj(c->b, uni)) continue;
        nodes++;
        if ((nodes & 0xFFFFF)==0){fprintf(stderr,"nodes %lld depth %d\n",nodes,nch);fflush(stderr);}
        uint64_t nu[W]; for(int w=0;w<W;w++) nu[w]=uni[w]|c->b[w];
        /* filter remaining classes */
        int *nl[7]; int nn[7];
        int ok=1;
        for (int cc=0;cc<7;cc++){
            if (used[cc]||cc==skipcls){nl[cc]=NULL;nn[cc]=0;continue;}
            nl[cc]=malloc(ln[cc]*sizeof(int)); nn[cc]=0;
            for (int j=0;j<ln[cc];j++)
                if (disj(copies[lists[cc][j]].b, nu)) nl[cc][nn[cc]++]=lists[cc][j];
            if (nn[cc]==0 && nch+1 + 0 < target){ /* may still be ok if we don't need it (k=6 skip handled by skipcls) */ ok=0; }
        }
        chosen[nch++] = mylist[i];
        int res = 0;
        if (ok || nch==target) res = solve(nl, nn, used, nu);
        nch--;
        for (int cc=0;cc<7;cc++) free(nl[cc]);
        if (res){ used[best]=0; return 1; }
    }
    used[best]=0;
    return 0;
}

int main(int argc, char **argv){
    FILE *f = fopen(argv[1], "r");
    int k = atoi(argv[2]);
    FILE *fvf = fopen("fv_orbits.txt", "r");
    for (int i=0;i<7;i++) if(fscanf(fvf,"%d",&fv[i])!=1) return 2;
    fclose(fvf);
    size_t cap=1<<20; copies=malloc(cap*sizeof(Copy));
    char line[4096];
    while (fgets(line,sizeof line,f)){
        if (ncop==(int)cap){cap*=2;copies=realloc(copies,cap*sizeof(Copy));}
        Copy *c=&copies[ncop]; memset(c,0,sizeof *c); c->fv=-1;
        char *p=line; int o,cnt=0;
        while (sscanf(p,"%d",&o)==1){
            c->b[o>>6]|=1ULL<<(o&63); cnt++;
            for(int i=0;i<7;i++) if(o==fv[i]) c->fv=i;
            while(*p==' ')p++; while(*p&&*p!=' '&&*p!='\n')p++; while(*p==' ')p++;
            if(*p=='\n'||!*p)break;
        }
        if(cnt!=25||c->fv<0){fprintf(stderr,"bad line %d\n",ncop);return 2;}
        ncop++;
    }
    fclose(f);
    fprintf(stderr,"%d copies\n",ncop);
    unsigned seed = argc>4 ? (unsigned)atoi(argv[4]) : 1u;
    if (getenv("STRIDE")) stride = atoi(getenv("STRIDE"));
    if (getenv("OFFSET")) offset = atoi(getenv("OFFSET"));
    srand(seed);
    int *cls[7], clsn[7];
    for(int i=0;i<7;i++){cls[i]=malloc(ncop*sizeof(int));clsn[i]=0;}
    for(int i=0;i<ncop;i++) cls[copies[i].fv][clsn[copies[i].fv]++]=i;
    /* shuffle each class */
    for(int c=0;c<7;c++){
        for(int i=clsn[c]-1;i>0;i--){int j=rand()%(i+1);int t=cls[c][i];cls[c][i]=cls[c][j];cls[c][j]=t;}
        fprintf(stderr,"class %d: %d\n",c,clsn[c]);
    }
    target=k;
    uint64_t uni[W]={0,0,0};
    int used[7]={0,0,0,0,0,0,0};
    int found=0;
    if (k==7){
        skipcls=-1; nodes=0; nch=0;
        found = solve(cls,clsn,used,uni);
    } else {
        for (skipcls=6; skipcls>=0 && !found; skipcls--){
            nodes=0; nch=0; memset(used,0,sizeof used);
            fprintf(stderr,"skip class %d\n",skipcls); fflush(stderr);
            found = solve(cls,clsn,used,uni);
            if(!found) fprintf(stderr,"no %d-packing skipping class %d (nodes=%lld)\n",k,skipcls,nodes);
        }
    }
    if (found){
        printf("FOUND %d-%s\n",k,k==7?"DECOMPOSITION":"PACKING");
        if (argc>3){
            FILE *out=fopen(argv[3],"w");
            for(int i=0;i<nch;i++)
                for(int o=0;o<175;o++)
                    if(copies[chosen[i]].b[o>>6]>>(o&63)&1) fprintf(out,"%d %d\n",i,o);
            fclose(out);
        }
    } else printf("NO %d-packing among given copies\n",k);
    return 0;
}
