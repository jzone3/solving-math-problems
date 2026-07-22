/* pmd_dlx.c — Perfect Mendelsohn Design search with prescribed cyclic automorphisms.
 *
 * A (v,k)-PMD: blocks are cyclically ordered k-tuples of distinct points such that
 * every ordered pair (x,y), x!=y, appears at cyclic distance i in exactly one block,
 * for every i = 1..k-1.  b = v(v-1)/k blocks.
 *
 * V2 method (difference method / Kramer-Mesner): prescribe an automorphism sigma
 * consisting of c cycles of length n plus f fixed points (v = c*n + f).  Candidate
 * rows of the exact-cover matrix are sigma-orbits of blocks; columns are the
 * (distance, ordered pair) requirements.  DLX (Algorithm X, dancing links) then
 * searches for an exact cover.  With n=1 (trivial group) this is a plain full
 * exhaustive exact-cover search.
 *
 * Usage: ./pmd_dlx v k n c f [maxsol] [fixfirst]
 *   sigma = (0 1 ... n-1)(n ... 2n-1)...(...)  plus fixed points c*n .. v-1
 *   maxsol: stop after this many solutions (0 = count all / prove exhaustion). Default 1.
 *   fixfirst: if 1, force the block (0,1,...,k-1) into the solution (valid symmetry
 *             breaking for the trivial group n=1,c=v case: any PMD can be relabelled
 *             so its block covering (0,1) at distance 1 is (0,1,...,k-1)).
 * Prints solutions as b lines of k numbers between SOLUTION BEGIN/END markers.
 * Exit: prints "SOLUTIONS <count>" and "NODES <count>" at end.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

static int V, K, N, C, F, B;
static long long maxsol = 1, nsol = 0;
static unsigned long long nodes = 0;
static int fixfirst = 0;

/* ---- block encoding: canonical rotation, 6 elems * 6 bits ---- */
static inline uint64_t enc(const int *t, int k){
    uint64_t x = 0; for(int i=0;i<k;i++) x = (x<<6) | (uint64_t)t[i]; return x;
}
static void canon(const int *t, int k, int *out){
    int best = 0;
    for(int r=1;r<k;r++){
        for(int i=0;i<k;i++){
            int a = t[(best+i)%k], b2 = t[(r+i)%k];
            if(b2 < a){ best = r; break; }
            if(b2 > a) break;
        }
    }
    for(int i=0;i<k;i++) out[i] = t[(best+i)%k];
}
static inline int sigma(int p){ return p >= N*C ? p : (p%N==N-1 ? p-(N-1) : p+1); }

/* ---- hash set for visited canonical blocks ---- */
static uint64_t *hs; static long hs_size;
static int hs_insert(uint64_t key){ /* returns 1 if newly inserted */
    long h = (long)((key*0x9E3779B97F4A7C15ULL) % (uint64_t)hs_size);
    while(hs[h] != UINT64_MAX){ if(hs[h]==key) return 0; h = (h+1)%hs_size; }
    hs[h] = key; return 1;
}

/* ---- DLX structures (arrays) ---- */
static int ncols;
static int *Lc,*Rc,*collen;       /* column headers: 0..ncols (0=root) */
static int *U,*D,*Cl,*Rw;         /* nodes */
static long nnodes_alloc, nn;
static int *rowlen_of, *roworbit; /* per row id */
static long nrows;
/* row storage for printing solutions */
static int (*orbit_blocks)[/*maxorb*k*/1];  /* unused; store separately */
static int *orbstore; static long *orboff; static int *orblen; /* blocks per orbit row */

static int colid(int d,int x,int y){ /* d in 1..K-1, ordered pair x!=y */
    int p = x*(V-1) + (y - (y>x?1:0));
    return (d-1)*V*(V-1) + p + 1; /* 1-based, 0 is root */
}

static void cover(int c){
    Rc[Lc[c]] = Rc[c]; Lc[Rc[c]] = Lc[c];
    for(int i=D[c]; i!=c; i=D[i])
        for(int j=Rw[i]; ; ){
            /* iterate right within row: nodes of a row stored contiguously; use next-array */
            break;
        }
}
/* We instead store per-node L/R links for row traversal */
static int *NL,*NR;
static void cover2(int c){
    Rc[Lc[c]] = Rc[c]; Lc[Rc[c]] = Lc[c];
    for(int i=D[c]; i!=c; i=D[i])
        for(int j=NR[i]; j!=i; j=NR[j]){
            U[D[j]] = U[j]; D[U[j]] = D[j]; collen[Cl[j]]--;
        }
}
static void uncover2(int c){
    for(int i=U[c]; i!=c; i=U[i])
        for(int j=NL[i]; j!=i; j=NL[j]){
            collen[Cl[j]]++; U[D[j]] = j; D[U[j]] = j;
        }
    Lc[Rc[c]] = c; Rc[Lc[c]] = c;
}

static int solrows[4096]; static int depth_ = 0;

static void print_solution(void){
    printf("SOLUTION BEGIN\n");
    for(int s=0;s<depth_;s++){
        int r = solrows[s];
        long off = orboff[r];
        for(int bblk=0;bblk<orblen[r];bblk++){
            for(int i=0;i<K;i++) printf("%d ", orbstore[off + (long)bblk*K + i]);
            printf("\n");
        }
    }
    printf("SOLUTION END\n"); fflush(stdout);
}

static void search(void){
    if(Rc[0]==0){ nsol++; print_solution(); return; }
    /* min-length column */
    int c = -1, best = 1<<30;
    for(int j=Rc[0]; j!=0; j=Rc[j]) if(collen[j] < best){ best = collen[j]; c = j; if(best<=1) break; }
    if(best==0) return;
    cover2(c);
    for(int i=D[c]; i!=c; i=D[i]){
        nodes++;
        solrows[depth_++] = Rw[i];
        for(int j=NR[i]; j!=i; j=NR[j]) cover2(Cl[j]);
        search();
        for(int j=NL[i]; j!=i; j=NL[j]) uncover2(Cl[j]);
        depth_--;
        if(maxsol && nsol>=maxsol){ uncover2(c); return; }
    }
    uncover2(c);
}

/* force a specific row (by row id) into the partial solution before search */
static int force_row(int target_row){
    for(int c=Rc[0]; c!=0; c=Rc[c])
        for(int i=D[c]; i!=c; i=D[i])
            if(Rw[i]==target_row){
                solrows[depth_++] = target_row;
                cover2(Cl[i]);
                for(int j=NR[i]; j!=i; j=NR[j]) cover2(Cl[j]);
                return 1;
            }
    return 0;
}

int main(int argc, char **argv){
    if(argc < 6){ fprintf(stderr,"usage: %s v k n c f [maxsol] [fixfirst]\n", argv[0]); return 2; }
    V=atoi(argv[1]); K=atoi(argv[2]); N=atoi(argv[3]); C=atoi(argv[4]); F=atoi(argv[5]);
    if(argc>6) maxsol=atoll(argv[6]);
    if(argc>7) fixfirst=atoi(argv[7]);
    if(N*C+F != V){ fprintf(stderr,"bad cycle type: n*c+f != v\n"); return 2; }
    if((V*(V-1))%K){ fprintf(stderr,"k does not divide v(v-1)\n"); return 2; }
    B = V*(V-1)/K;
    ncols = (K-1)*V*(V-1);

    hs_size = 1; while(hs_size < 8LL*3000000) hs_size<<=1;
    hs = malloc(hs_size*sizeof(uint64_t)); memset(hs,0xff,hs_size*sizeof(uint64_t));

    /* first pass: enumerate canonical cyclic blocks, group into sigma-orbits,
       validate (no repeated (d,pair) inside an orbit), collect rows. */
    long cap_rows = 4000000, cap_store = 80000000;
    orboff = malloc(cap_rows*sizeof(long));
    orblen = malloc(cap_rows*sizeof(int));
    orbstore = malloc(cap_store*sizeof(int));
    nrows = 0; long storepos = 0;

    unsigned char *seencol = calloc(ncols+1,1);
    int t[16], ct[16], perm[16];
    int idx[16];
    /* enumerate ordered k-tuples of distinct elements with t[0] = min of tuple
       (canonical rotation starts at min elem => enumerate canonical forms directly) */
    long long ncanon = 0;
    /* iterative DFS over positions */
    int pos = 0; idx[0] = 0; int used[64]; memset(used,0,sizeof(used));
    /* simple recursive via explicit stack is messy; use recursion */
    void rec(int p){
        if(p==K){
            /* t[0] must be the minimum (canonical) */
            for(int i=1;i<K;i++) if(t[i] < t[0]) return;
            ncanon++;
            uint64_t key = enc(t,K);
            if(!hs_insert(key)) return; /* already in an earlier orbit */
            /* build orbit */
            long rowstart = storepos;
            int olen = 0;
            memcpy(ct,t,sizeof(int)*K);
            int bad = 0;
            int touched[1024]; int ntouched=0;
            while(1){
                /* record block ct (canonical) */
                if(storepos + K > cap_store){ fprintf(stderr,"store overflow\n"); exit(3); }
                memcpy(orbstore+storepos, ct, sizeof(int)*K); storepos += K; olen++;
                /* mark columns */
                for(int d=1;d<K && !bad;d++) for(int i=0;i<K;i++){
                    int cid = colid(d, ct[i], ct[(i+d)%K]);
                    if(seencol[cid]){ bad=1; break; }
                    seencol[cid]=1; touched[ntouched++]=cid;
                }
                if(bad) break;
                /* next block in orbit */
                for(int i=0;i<K;i++) perm[i] = sigma(ct[i]);
                canon(perm,K,ct);
                uint64_t k2 = enc(ct,K);
                if(k2==key) break;
                hs_insert(k2);
                if(olen > 512){ fprintf(stderr,"orbit too long?\n"); exit(3); }
            }
            for(int i=0;i<ntouched;i++) seencol[touched[i]]=0;
            if(bad){ storepos = rowstart; return; }
            if(nrows>=cap_rows){ fprintf(stderr,"row overflow\n"); exit(3); }
            orboff[nrows] = rowstart; orblen[nrows] = olen; nrows++;
            return;
        }
        for(int e=0;e<V;e++){
            if(used[e]) continue;
            t[p]=e; used[e]=1; rec(p+1); used[e]=0;
        }
    }
    rec(0);
    fprintf(stderr,"canonical cyclic blocks: %lld, valid orbit rows: %ld, stored blocks: %ld\n",
            ncanon, nrows, storepos/K);

    /* build DLX */
    long total_ones = 0;
    for(long r=0;r<nrows;r++) total_ones += (long)orblen[r]*K*(K-1);
    nnodes_alloc = total_ones + 8;
    U=malloc(nnodes_alloc*sizeof(int)); D=malloc(nnodes_alloc*sizeof(int));
    Cl=malloc(nnodes_alloc*sizeof(int)); Rw=malloc(nnodes_alloc*sizeof(int));
    NL=malloc(nnodes_alloc*sizeof(int)); NR=malloc(nnodes_alloc*sizeof(int));
    Lc=malloc((ncols+1)*sizeof(int)); Rc=malloc((ncols+1)*sizeof(int));
    collen=calloc(ncols+1,sizeof(int));
    int *coltail = malloc((ncols+1)*sizeof(int));
    for(int j=0;j<=ncols;j++){ Lc[j]=(j==0?ncols:j-1); Rc[j]=(j==ncols?0:j+1); coltail[j]=-1; }
    /* column header "node" index: we treat header of col j as virtual node -j?  Simpler:
       allocate header nodes 0..ncols in the node arrays too. */
    /* Reallocate with headers occupying node ids 0..ncols */
    long base = ncols+1;
    int *U2=malloc((nnodes_alloc+base)*sizeof(int)), *D2=malloc((nnodes_alloc+base)*sizeof(int));
    int *Cl2=malloc((nnodes_alloc+base)*sizeof(int)), *Rw2=malloc((nnodes_alloc+base)*sizeof(int));
    int *NL2=malloc((nnodes_alloc+base)*sizeof(int)), *NR2=malloc((nnodes_alloc+base)*sizeof(int));
    for(int j=0;j<=ncols;j++){ U2[j]=j; D2[j]=j; Cl2[j]=j; Rw2[j]=-1; NL2[j]=j; NR2[j]=j; }
    long nid = base;
    for(long r=0;r<nrows;r++){
        long first = -1, prev = -1;
        long off = orboff[r];
        for(int bblk=0;bblk<orblen[r];bblk++){
            int *blk = orbstore + off + (long)bblk*K;
            for(int d=1;d<K;d++) for(int i=0;i<K;i++){
                int cid = colid(d, blk[i], blk[(i+d)%K]);
                long nd = nid++;
                Cl2[nd]=cid; Rw2[nd]=(int)r;
                /* vertical: insert above header (append at bottom) */
                D2[nd]=cid; U2[nd]=U2[cid]; D2[U2[cid]]=(int)nd; U2[cid]=(int)nd;
                collen[cid]++;
                if(first<0){ first=nd; NL2[nd]=(int)nd; NR2[nd]=(int)nd; }
                else { NL2[nd]=(int)prev; NR2[nd]=NR2[prev]; NL2[NR2[prev]]=(int)nd; NR2[prev]=(int)nd; }
                prev=nd;
            }
        }
    }
    free(U);free(D);free(Cl);free(Rw);free(NL);free(NR);
    U=U2;D=D2;Cl=Cl2;Rw=Rw2;NL=NL2;NR=NR2;
    fprintf(stderr,"DLX built: %ld nodes, %d cols\n", nid-base, ncols);

    if(fixfirst){
        /* find row that is the orbit of block (0,1,...,k-1); for trivial group it's the block itself */
        int want[16]; for(int i=0;i<K;i++) want[i]=i;
        uint64_t wk = enc(want,K);
        int target=-1;
        for(long r=0;r<nrows;r++){
            int *blk = orbstore + orboff[r];
            if(enc(blk,K)==wk || 1){
                /* check any block in orbit equals want */
                for(int bblk=0;bblk<orblen[r];bblk++)
                    if(enc(orbstore+orboff[r]+(long)bblk*K,K)==wk){ target=(int)r; break; }
            }
            if(target>=0) break;
        }
        if(target<0){ fprintf(stderr,"fixfirst: block 0..k-1 not in any valid orbit -> UNSAT under this restriction\n"); printf("SOLUTIONS 0\nNODES 0\n"); return 0; }
        if(!force_row(target)){ fprintf(stderr,"fixfirst: could not force row\n"); return 3; }
        fprintf(stderr,"forced row %d (orbit len %d)\n", target, orblen[target]);
    }

    search();
    printf("SOLUTIONS %lld\nNODES %llu\n", nsol, nodes);
    return 0;
}
