/* P14 V4: exhaustive shallow search ("polish") from a near-miss.
 * Moves: compound trades (i1,i2,j1,j2) that preserve row compositions AND
 * column sums (swap entries j1,j2 in row i1, and the opposite-diff swap in
 * row i2). Only pair inner products change.
 * DFS up to depth D, pruning any prefix whose L1 pair-violation exceeds the
 * starting violation (plateau-connected exploration). Prints SOLVED + matrix
 * if a zero-violation matrix is reachable within D trades.
 *
 * Usage: polish V B rho1 rho2 K Lam depth matrixfile
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int V,B,K,LAM,D;
static long long SLACK=0;
static int M[32][64],P[32][32];
static long long E0;
static int iabs(int x){return x<0?-x:x;}
static long long nodes=0;

static long long pairE(void){
    long long e=0;
    for(int i=0;i<V;i++)for(int k=i+1;k<V;k++)e+=iabs(P[i][k]-LAM);
    return e;
}
static void apply(int i1,int i2,int j1,int j2,int sign){
    /* sign=+1 apply, -1 undo (same op is involution, sign unused but kept clear) */
    (void)sign;
    int a=M[i1][j1];M[i1][j1]=M[i1][j2];M[i1][j2]=a;
    a=M[i2][j1];M[i2][j1]=M[i2][j2];M[i2][j2]=a;
}
static void updP(int i1,int i2,int j1,int j2,int d){
    /* call BEFORE apply, with d = M[i1][j2]-M[i1][j1] (post-move col j1 delta for row i1) */
    for(int k=0;k<V;k++){
        if(k==i1||k==i2)continue;
        int dk=d*(M[k][j1]-M[k][j2]);
        if(dk){P[i1][k]+=dk;P[k][i1]+=dk;P[i2][k]-=dk;P[k][i2]-=dk;}
    }
}
static int dfs(int depth,long long E){
    nodes++;
    if(E==0)return 1;
    if(depth==D)return 0;
    for(int j1=0;j1<B;j1++)for(int j2=j1+1;j2<B;j2++){
        for(int i1=0;i1<V;i1++){
            int a=M[i1][j1],b=M[i1][j2];
            if(a==b)continue;
            int d=b-a;
            for(int i2=i1+1;i2<V;i2++){
                if(M[i2][j1]-M[i2][j2]!=d)continue;
                /* delta E */
                long long dE=0;
                for(int k=0;k<V;k++){
                    if(k==i1||k==i2)continue;
                    int dk=d*(M[k][j1]-M[k][j2]);
                    if(!dk)continue;
                    int p1=P[i1][k]-LAM,p2=P[i2][k]-LAM;
                    dE+=iabs(p1+dk)-iabs(p1)+iabs(p2-dk)-iabs(p2);
                }
                if(E+dE>E0+SLACK)continue;
                updP(i1,i2,j1,j2,d);
                apply(i1,i2,j1,j2,1);
                if(dfs(depth+1,E+dE))return 1;
                apply(i1,i2,j1,j2,-1);
                updP(i1,i2,j1,j2,-d); /* careful: undo with pre-undo values */
            }
        }
    }
    return 0;
}
int main(int argc,char**argv){
    if(argc<9){fprintf(stderr,"usage: %s V B r1 r2 K Lam depth file [slack]\n",argv[0]);return 2;}
    if(argc>9)SLACK=atoll(argv[9]);
    V=atoi(argv[1]);B=atoi(argv[2]);K=atoi(argv[5]);LAM=atoi(argv[6]);D=atoi(argv[7]);
    FILE*f=fopen(argv[8],"r"); if(!f){perror("file");return 2;}
    for(int i=0;i<V;i++)for(int j=0;j<B;j++){int c=fgetc(f);while(c=='\n'||c==' '||c=='\r')c=fgetc(f);M[i][j]=c-'0';}
    fclose(f);
    for(int i=0;i<V;i++)for(int k=i+1;k<V;k++){int s=0;for(int j=0;j<B;j++)s+=M[i][j]*M[k][j];P[i][k]=P[k][i]=s;}
    E0=pairE();
    fprintf(stderr,"start pairE=%lld depth=%d\n",E0,D);
    if(dfs(0,E0)){
        printf("SOLVED\n");
        for(int r=0;r<V;r++){for(int c=0;c<B;c++)putchar('0'+M[r][c]);putchar('\n');}
        return 0;
    }
    fprintf(stderr,"no solution within depth %d (nodes=%lld)\n",D,nodes);
    return 1;
}
