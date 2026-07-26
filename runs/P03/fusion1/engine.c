/* Bitmask orientation/packing engine for P03.
 *
 * Input lines: n m u0 v0 u1 v1 ... (one undirected graph per line).
 * Usage: engine k mode shard nshards < graphs.txt
 * mode is tau3 or tau4; graph sharding is by input line.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#define MAXN 20
#define MAXM 40
#define MAXCUT 20000

static int n,m,k,mode,shard,nshards;
static int eu[MAXM],ev[MAXM],deg[MAXN],od[MAXN],idg[MAXN];
static int ou[MAXM], ov[MAXM], arc_m;
static uint64_t reachv[MAXN];
static int cuts[MAXCUT], clen[MAXCUT], ncuts, mincut[MAXCUT], minlen[MAXCUT], nmin, tauv;
static int enum_deferred, ideal_count, cut_mode_fast=1, orient_mode_fast=1;
static int lazy_mode=0;
static int topo[MAXN], predmask[MAXN], topo_n;
static int color[MAXM], used[MAXCUT], leftc[MAXCUT], arc_cuts[MAXM][MAXCUT], narc[MAXM];
static int target_od[MAXN], role_code[MAXN], role_profile;
static int rem_inc[MAXN];
static uint64_t lazy_boundary, lazy_bad_boundary;
static long long graphs, orientations, profiles, ss_skip, tau_skip, safe_skip;
static long long packed, candidates, checks, deferred;
static int role[32][4], nroles;

static int pop(uint64_t x){ return __builtin_popcountll(x); }
static int bit(uint64_t x,int i){ return (int)((x>>i)&1ULL); }

static int cut_for(uint64_t x){
    uint64_t cm=0;
    for(int i=0;i<arc_m;i++) if(bit(x,ou[i]) && !bit(x,ov[i])) cm|=1ULL<<i;
    return (int)cm;
}
static int cmpcut(const void*a,const void*b){
    int x=*(const int*)a,y=*(const int*)b;
    return clen[x]-clen[y];
}
static void finalize_cuts(void){
    int ord[MAXCUT];
    for(int i=0;i<ncuts;i++) ord[i]=i;
    qsort(ord,ncuts,sizeof(int),cmpcut);
    nmin=0;
    for(int oi=0;oi<ncuts;oi++){
        int i=ord[oi], sub=0;
        for(int j=0;j<nmin;j++)
            if((((uint64_t)mincut[j]) & (uint64_t)cuts[i])==(uint64_t)mincut[j]){
                sub=1;break;
            }
        if(!sub){ mincut[nmin]=cuts[i]; minlen[nmin]=clen[i]; nmin++; }
    }
}
static void enumerate_cuts_old(void){
    ncuts=0; tauv=999;
    uint64_t full=(1ULL<<n)-1;
    for(uint64_t x=1;x<full;x++){
        int closed=1;
        for(int i=0;i<arc_m;i++)
            if(bit(x,ov[i]) && !bit(x,ou[i])) { closed=0; break; }
        if(!closed) continue;
        int cm=cut_for(x), z=pop((uint64_t)cm);
        if(z<tauv) tauv=z;
        if(ncuts<MAXCUT){ cuts[ncuts]=cm; clen[ncuts++]=z; }
    }
    finalize_cuts();
}
static void fast_ideal_rec(int p, uint64_t set){
    if(enum_deferred)return;
    if(++ideal_count > 1000000 || ncuts >= MAXCUT){
        enum_deferred=1; return;
    }
    if(p==topo_n){
        uint64_t full=(1ULL<<n)-1;
        if(set && set!=full){
            int cm=cut_for(set), z=pop((uint64_t)cm);
            if(z<tauv)tauv=z;
            cuts[ncuts]=cm;clen[ncuts++]=z;
        }
        return;
    }
    int v=topo[p];
    fast_ideal_rec(p+1,set);
    if((predmask[v]&~(int)set)==0)
        fast_ideal_rec(p+1,set|(1ULL<<v));
}
static void enumerate_cuts_fast(void){
    ncuts=0; nmin=0; tauv=999; enum_deferred=0; ideal_count=0;
    int indeg[MAXN]={0}, q[MAXN],qh=0,qt=0;
    memset(predmask,0,sizeof(predmask));
    for(int i=0;i<arc_m;i++){predmask[ov[i]]|=1<<ou[i];indeg[ov[i]]++;}
    for(int v=0;v<n;v++)if(!indeg[v])q[qt++]=v;
    while(qh<qt){
        int v=q[qh++];topo[topo_n++]=v;
        for(int i=0;i<arc_m;i++)if(ou[i]==v&&!--indeg[ov[i]])q[qt++]=ov[i];
    }
    if(topo_n!=n){enum_deferred=1;return;}
    fast_ideal_rec(0,0);
    if(!enum_deferred)finalize_cuts();
}
static void enumerate_cuts(void){
    topo_n=0;
    if(cut_mode_fast)enumerate_cuts_fast();
    else enumerate_cuts_old();
}
static uint64_t implication_closure(uint64_t boundary, int start){
    uint64_t reach[MAXN];
    uint64_t full=(1ULL<<n)-1;
    for(int v=0;v<n;v++)reach[v]=1ULL<<v;
    for(int i=0;i<arc_m;i++){
        reach[ov[i]]|=1ULL<<ou[i];
        if(!bit(boundary,i))reach[ou[i]]|=1ULL<<ov[i];
    }
    for(int z=0;z<n;z++)
        for(int v=0;v<n;v++)
            if(reach[v]&(1ULL<<z))reach[v]|=reach[z];
    return reach[start]&full;
}
static uint64_t color_implication_closure(int c, int start){
    uint64_t reach[MAXN],full=(1ULL<<n)-1;
    for(int v=0;v<n;v++)reach[v]=1ULL<<v;
    for(int i=0;i<arc_m;i++){
        reach[ov[i]]|=1ULL<<ou[i];
        if(color[i]!=c)reach[ou[i]]|=1ULL<<ov[i];
    }
    for(int z=0;z<n;z++)
        for(int v=0;v<n;v++)
            if(reach[v]&(1ULL<<z))reach[v]|=reach[z];
    return reach[start]&full;
}
static int lazy_find_boundary(uint64_t boundary, int exact){
    uint64_t full=(1ULL<<n)-1;
    for(int v=0;v<n;v++){
        uint64_t set=implication_closure(boundary,v);
        if(set==full)continue;
        uint64_t cm=(uint64_t)cut_for(set);
        if((exact && cm!=boundary) || (!exact && !cm))continue;
        if(exact ? cm==boundary : ((cm&~boundary)==0)){
            lazy_boundary=cm;
            return 1;
        }
    }
    return 0;
}
static int flow_cap[MAXN+2][MAXN+2], flow_n;
static int flow_max(int s, int t){
    int ans=0, parent[MAXN+2], aug[MAXN+2];
    for(;;){
        for(int i=0;i<flow_n;i++)parent[i]=-1;
        int q[MAXN+2],qh=0,qt=0;
        q[qt++]=s; parent[s]=s; aug[s]=1000000;
        while(qh<qt && parent[t]<0){
            int u=q[qh++];
            for(int v=0;v<flow_n;v++)
                if(parent[v]<0 && flow_cap[u][v]>0){
                    parent[v]=u; aug[v]=aug[u]<flow_cap[u][v]?aug[u]:flow_cap[u][v];
                    q[qt++]=v;
                    if(v==t)break;
                }
        }
        if(parent[t]<0)break;
        int d=aug[t]; ans+=d;
        for(int v=t;v!=s;v=parent[v]){
            int u=parent[v];flow_cap[u][v]-=d;flow_cap[v][u]+=d;
        }
    }
    return ans;
}
static int tau_lazy(void){
    int src[MAXN],snk[MAXN],ns=0,nt=0;
    for(int v=0;v<n;v++){if(!idg[v])src[ns++]=v;if(!od[v])snk[nt++]=v;}
    int best=k;
    for(int si=0;si<ns;si++)for(int ti=0;ti<nt;ti++){
        int S=n,T=n+1; flow_n=n+2;
        memset(flow_cap,0,sizeof(flow_cap));
        for(int i=0;i<arc_m;i++){
            flow_cap[ou[i]][ov[i]]++;
            flow_cap[ov[i]][ou[i]]+=1000;
        }
        flow_cap[S][src[si]]+=1000;
        flow_cap[snk[ti]][T]+=1000;
        int z=flow_max(S,T);
        if(z<best)best=z;
    }
    return best;
}
static int is_star_cut(uint64_t cm){
    int tails=-1,heads=-1,nt=0,nh=0;
    for(int i=0;i<arc_m;i++)if(bit(cm,i)){
        if(tails!=ou[i]){tails=ou[i];nt++;}
        if(heads!=ov[i]){heads=ov[i];nh++;}
    }
    return (nt==1 && idg[tails]==0 && od[tails]==k) ||
           (nh==1 && od[heads]==0 && idg[heads]==k);
}
static int reduced_boundary_rec(int start, int left, uint64_t boundary){
    if(!left){
        if(!lazy_find_boundary(boundary,1))return 0;
        if(!is_star_cut(lazy_boundary)){
            lazy_bad_boundary=lazy_boundary;
            return 1;
        }
        return 0;
    }
    for(int i=start;i<=arc_m-left;i++)
        if(reduced_boundary_rec(i+1,left-1,boundary|(1ULL<<i)))return 1;
    return 0;
}
static int reduced_cuts_ok_lazy(void){
    /*
     * The lazy path does not need the explicit reduced-dicut optimization:
     * the CEGAR packer remains an exact decision procedure.  Keep this
     * hook separate so the explicit path retains the original filter.
     */
    return 1;
}
static int lazy_color_dfs(int p){
    if(p==arc_m)return 1;
    for(int c=0;c<k;c++){
        int ok=1,touched[MAXCUT],oldused[MAXCUT],oldleft[MAXCUT],nt=0;
        for(int z=0;z<narc[p];z++){
            int q=arc_cuts[p][z],next=used[q]|(1<<c),miss=0;
            for(int cc=0;cc<k;cc++)if(!(next&(1<<cc)))miss++;
            if(miss>leftc[q]-1){ok=0;break;}
            touched[nt]=q;oldused[nt]=used[q];oldleft[nt]=leftc[q];nt++;
        }
        if(!ok)continue;
        color[p]=c;
        for(int z=0;z<narc[p];z++){int q=arc_cuts[p][z];used[q]|=1<<c;leftc[q]--;}
        if(lazy_color_dfs(p+1))return 1;
        for(int z=0;z<nt;z++){used[touched[z]]=oldused[z];leftc[touched[z]]=oldleft[z];}
        color[p]=-1;
    }
    return 0;
}
static uint64_t violated_color_cut(int c){
    uint64_t full=(1ULL<<n)-1;
    for(int v=0;v<n;v++){
        uint64_t set=color_implication_closure(c,v);
        if(set!=full)return (uint64_t)cut_for(set);
    }
    return 0;
}
static int packs_lazy(void){
    ncuts=0;
    for(int iter=0;iter<MAXCUT*2;iter++){
        for(int i=0;i<arc_m;i++){narc[i]=0;color[i]=-1;}
        for(int q=0;q<ncuts;q++){
            used[q]=0;leftc[q]=clen[q];
            for(int i=0;i<arc_m;i++)if(bit((uint64_t)cuts[q],i))arc_cuts[i][narc[i]++]=q;
        }
        if(!lazy_color_dfs(0))return 0;
        int added=0;
        for(int c=0;c<k;c++){
            uint64_t cm=violated_color_cut(c);
            if(!cm)continue;
            int known=0;
            for(int q=0;q<ncuts;q++)if((uint64_t)cuts[q]==cm)known=1;
            if(!known){
                if(ncuts>=MAXCUT)return 0;
                cuts[ncuts]=(int)cm;clen[ncuts++]=pop(cm);added=1;
            }
        }
        if(!added)return 1;
    }
    return 0;
}
static int reaches(int s,int t){
    uint64_t seen=1ULL<<s, todo=seen;
    while(todo){
        int u=__builtin_ctzll(todo); todo&=todo-1;
        for(int i=0;i<arc_m;i++) if(ou[i]==u && !(seen&(1ULL<<ov[i]))){
            seen|=1ULL<<ov[i]; todo|=1ULL<<ov[i];
        }
    }
    return bit(seen,t);
}
static int source_sink_ok(void){
    int src[MAXN],snk[MAXN],ns=0,nt=0;
    for(int v=0;v<n;v++){ if(!idg[v])src[ns++]=v; if(!od[v])snk[nt++]=v; }
    for(int i=0;i<ns;i++)for(int j=0;j<nt;j++)if(!reaches(src[i],snk[j]))return 0;
    return 1;
}
static int rho_ok(void){
    int ex[MAXN]={0};
    for(int i=0;i<arc_m;i++){ex[ou[i]]++;ex[ov[i]]--;}
    int sum=0; for(int v=0;v<n;v++){int r=ex[v]%k;if(r<0)r+=k;sum+=r;}
    return sum/k>=3;
}
static int rho_reverse_ok(void){
    int ex[MAXN]={0};
    for(int i=0;i<arc_m;i++){ex[ov[i]]++;ex[ou[i]]--;}
    int sum=0; for(int v=0;v<n;v++){int r=ex[v]%k;if(r<0)r+=k;sum+=r;}
    return sum/k>=3;
}
static int reduced_cuts_ok(void){
    for(int q=0;q<nmin;q++) if(minlen[q]==k){
        int tails=-1,heads=-1,nt=0,nh=0;
        for(int i=0;i<arc_m;i++) if(bit((uint64_t)mincut[q],i)){
            if(tails!=ou[i]){tails=ou[i];nt++;}
            if(heads!=ov[i]){heads=ov[i];nh++;}
        }
        if(!((nt==1 && idg[tails]==0 && od[tails]==k) ||
             (nh==1 && od[heads]==0 && idg[heads]==k))) return 0;
    }
    return 1;
}
static int color_dfs(int p){
    if(p==arc_m)return 1;
    int a=p;
    for(int c=0;c<k;c++){
        int ok=1;
        int touched[MAXCUT], oldused[MAXCUT], oldleft[MAXCUT], nt=0;
        for(int z=0;z<narc[a];z++){int q=arc_cuts[a][z];
            int next=used[q]|(1<<c), miss=0;
            for(int cc=0;cc<k;cc++)if(!(next&(1<<cc)))miss++;
            if(miss > leftc[q]-1){ok=0;break;}
            touched[nt]=q; oldused[nt]=used[q]; oldleft[nt]=leftc[q]; nt++;
        }
        if(!ok)continue;
        color[a]=c;
        for(int z=0;z<narc[a];z++){int q=arc_cuts[a][z];used[q]|=1<<c;leftc[q]--;}
        if(color_dfs(p+1))return 1;
        for(int z=0;z<nt;z++){used[touched[z]]=oldused[z];leftc[touched[z]]=oldleft[z];}
        color[a]=-1;
    }
    return 0;
}
static int packs(void){
    if(k>4)return 0;
    for(int q=0;q<nmin;q++)if(minlen[q]<k)return 0;
    for(int i=0;i<arc_m;i++){narc[i]=0;color[i]=-1;}
    for(int q=0;q<nmin;q++){
        used[q]=0;leftc[q]=minlen[q];
        for(int i=0;i<arc_m;i++)if(bit((uint64_t)mincut[q],i))arc_cuts[i][narc[i]++]=q;
    }
    return color_dfs(0);
}
static int profile_ok(void){
    int s=0,t=0,a=0,b=0;
    for(int v=0;v<n;v++){
        if(deg[v]==(k==3?3:4)&&idg[v]==0){s++;continue;}
        if(deg[v]==(k==3?3:4)&&od[v]==0){t++;continue;}
        if(deg[v]==3&&idg[v]==1&&od[v]==2){a++;continue;}
        if(deg[v]==3&&idg[v]==2&&od[v]==1){b++;continue;}
        return 0;
    }
    for(int i=0;i<nroles;i++)if(role[i][0]==s&&role[i][1]==t&&role[i][2]==a&&role[i][3]==b)return 1;
    return 0;
}
static void leaf(void){
    orientations++;
    if(!profile_ok())return;
    profiles++;
    reachv[0]=reachv[0]; /* keep compiler quiet: reach is maintained below */
    for(int v=0;v<n;v++){uint64_t r=1ULL<<v;for(int i=0;i<arc_m;i++)if(ou[i]==v)r|=1ULL<<ov[i];reachv[v]=r;}
    for(int z=0;z<n;z++)for(int v=0;v<n;v++)if(reachv[v]&(1ULL<<z))reachv[v]|=reachv[z];
    if(source_sink_ok()){ss_skip++;return;}
    if(!rho_ok()){safe_skip++;return;}
    if(!rho_reverse_ok()){safe_skip++;return;}
    if(lazy_mode){
        tauv=tau_lazy();
        if(tauv!=k){tau_skip++;return;}
        if(!reduced_cuts_ok_lazy()){safe_skip++;return;}
        checks++;
        if(packs_lazy())packed++;
        else {candidates++;printf("CAND n=%d m=%d",n,arc_m);for(int i=0;i<arc_m;i++)printf(" %d %d",ou[i],ov[i]);printf("\n");fflush(stdout);}
        return;
    }
    enumerate_cuts();
    if(enum_deferred){
        deferred++;
        fprintf(stderr,"DEFERRED n=%d m=%d arcs=",n,arc_m);
        for(int i=0;i<arc_m;i++)fprintf(stderr,"%s%d>%d",i?",":"",ou[i],ov[i]);
        fputc('\n',stderr); fflush(stderr);
        return;
    }
    if(tauv!=k){tau_skip++;return;}
    if(!reduced_cuts_ok()){safe_skip++;return;}
    checks++;
    if(packs())packed++;
    else {candidates++;printf("CAND n=%d m=%d",n,arc_m);for(int i=0;i<arc_m;i++)printf(" %d %d",ou[i],ov[i]);printf("\n");fflush(stdout);}
}
static void orient_old(int e){
    if(e==m){leaf();return;}
    int x=eu[e],y=ev[e];
    for(int z=0;z<2;z++){
        int u=z?y:x,v=z?x:y;
        if(od[u]>=deg[u]||idg[v]>=deg[v])continue;
        if(reachv[v]&(1ULL<<u))continue;
        uint64_t save[MAXN];memcpy(save,reachv,sizeof(save));
        od[u]++;idg[v]++;ou[e]=u;ov[e]=v;
        uint64_t add=reachv[v]|(1ULL<<v);
        for(int q=0;q<n;q++)if(q==u||(reachv[q]&(1ULL<<u)))reachv[q]|=add;
        orient_old(e+1);
        memcpy(reachv,save,sizeof(save));od[u]--;idg[v]--;
    }
}
static int degree_bounds_ok(void){
    for(int v=0;v<n;v++){
        int need=target_od[v]-od[v];
        if(need<0 || need>rem_inc[v])return 0;
    }
    return 1;
}
static void orient_fixed(int e){
    if(e==m){leaf();return;}
    int x=eu[e],y=ev[e];
    rem_inc[x]--; rem_inc[y]--;
    for(int z=0;z<2;z++){
        int u=z?y:x,v=z?x:y;
        if(target_od[u]<=od[u])continue;
        if(reachv[v]&(1ULL<<u))continue;
        uint64_t save[MAXN];memcpy(save,reachv,sizeof(save));
        od[u]++;idg[v]++;ou[e]=u;ov[e]=v;
        uint64_t add=reachv[v]|(1ULL<<v);
        for(int q=0;q<n;q++)if(q==u||(reachv[q]&(1ULL<<u)))reachv[q]|=add;
        if(degree_bounds_ok())orient_fixed(e+1);
        memcpy(reachv,save,sizeof(save));od[u]--;idg[v]--;
    }
    rem_inc[x]++; rem_inc[y]++;
}
static void role_rec(int v, int ns, int nt, int na, int nb){
    if(v==n){
        if(ns!=role[role_profile][0] || nt!=role[role_profile][1] ||
           na!=role[role_profile][2] || nb!=role[role_profile][3])return;
        for(int u=0;u<n;u++){od[u]=idg[u]=0;reachv[u]=1ULL<<u;rem_inc[u]=deg[u];}
        for(int u=0;u<n;u++)target_od[u]=role_code[u];
        if(degree_bounds_ok())orient_fixed(0);
        return;
    }
    int d=deg[v];
    if(d==(k==3?3:4) && ns<role[role_profile][0]){
        role_code[v]=d; role_rec(v+1,ns+1,nt,na,nb);
    }
    if(d==(k==3?3:4) && nt<role[role_profile][1]){
        role_code[v]=0; role_rec(v+1,ns,nt+1,na,nb);
    }
    if(d==3 && na<role[role_profile][2]){
        role_code[v]=2; role_rec(v+1,ns,nt,na+1,nb);
    }
    if(d==3 && nb<role[role_profile][3]){
        role_code[v]=1; role_rec(v+1,ns,nt,na,nb+1);
    }
}
static void orient_profiled(void){
    for(role_profile=0;role_profile<nroles;role_profile++)
        role_rec(0,0,0,0,0);
}
static void setup_roles(void){
    nroles=0;
    if(k==4&&(n==12||n==14)){
        int x[2][4];
        if(n==12){
            int y[2][4]={{2,2,4,4},{3,3,3,3}};
            memcpy(x,y,sizeof(x));
        } else {
            int y[2][4]={{2,2,5,5},{3,3,4,4}};
            memcpy(x,y,sizeof(x));
        }
        int which = mode == 42 ? 1 : 0;
        memcpy(role[nroles++],x[which],sizeof(x[which]));
    } else if(k==3&&(n==8||n==10||n==12)){
        int x[4];
        x[0]=2; x[1]=2; x[2]=(n-4)/2; x[3]=(n-4)/2;
        memcpy(role[nroles++],x,sizeof(x));
    } else if(k==3&&n==18){
        int x[][4]={{2,2,7,7},{3,3,6,6},{4,4,5,5},{5,5,4,4},
        {2,3,8,5},{3,2,5,8},{2,4,9,3},{4,2,3,9},{3,4,7,4},
        {4,3,4,7},{2,5,10,1},{5,2,1,10},{3,5,8,2},{5,3,2,8},
        {4,5,6,3},{5,4,3,6}};
        for(unsigned i=0;i<sizeof(x)/sizeof(x[0]);i++)memcpy(role[nroles++],x[i],sizeof(x[i]));
    } else if(k==3&&n==16){
        int x[][4]={{2,2,6,6},{3,3,5,5},{4,4,4,4},
                    {5,5,3,3},{6,6,2,2},{7,7,1,1}};
        for(unsigned i=0;i<sizeof(x)/sizeof(x[0]);i++)
            memcpy(role[nroles++],x[i],sizeof(x[i]));
    }
}
int main(int ac,char**av){
    if(ac<5)return 2;
    k=atoi(av[1]);
    mode = strcmp(av[2],"tau4b")==0 ? 42 :
           (strcmp(av[2],"tau4a")==0 ? 41 :
           (strcmp(av[2],"check3")==0 ? 3 :
           (strcmp(av[2],"check4")==0 ? 4 : 3)));
    if(ac>=6 && !strcmp(av[5],"old")){cut_mode_fast=0;orient_mode_fast=0;}
    if(ac>=6 && !strcmp(av[5],"lazy"))lazy_mode=1;
    shard=atoi(av[3]);nshards=atoi(av[4]);
    char line[4096];long long idx=0;
    while(fgets(line,sizeof(line),stdin)){
        if(idx++%nshards!=shard)continue;
        int nn,mm,pos=0;if(sscanf(line,"%d %d%n",&nn,&mm,&pos)!=2)continue;
        n=nn;m=mm;arc_m=m;setup_roles();
        int at=pos;for(int i=0;i<m;i++){sscanf(line+at,"%d %d%n",&eu[i],&ev[i],&pos);at+=pos;deg[eu[i]]++;deg[ev[i]]++;}
        if(!strncmp(av[2],"check",5)){
            for(int i=0;i<m;i++){ou[i]=eu[i];ov[i]=ev[i];od[ou[i]]++;idg[ov[i]]++;}
            enumerate_cuts();
            if(enum_deferred){printf("CHECK DEFERRED ideals=%d cuts=%d\n",ideal_count,ncuts);
                memset(deg,0,sizeof(deg)); continue;}
            printf("CHECK tau=%d mincuts=%d pack=%d masks=",tauv,nmin,packs());
            for(int q=0;q<nmin;q++)printf("%s%u",q?",":"",(unsigned)mincut[q]);
            putchar('\n');
            memset(deg,0,sizeof(deg)); continue;
        }
        for(int v=0;v<n;v++){od[v]=idg[v]=0;reachv[v]=1ULL<<v;}
        graphs++;
        if(orient_mode_fast && nroles)orient_profiled();
        else orient_old(0);
        fprintf(stderr,"GRAPH %lld orientations=%lld profiles=%lld ss=%lld tau_skip=%lld safe=%lld checks=%lld packed=%lld cand=%lld deferred=%lld\n",idx,orientations,profiles,ss_skip,tau_skip,safe_skip,checks,packed,candidates,deferred);fflush(stderr);
        memset(deg,0,sizeof(deg));
    }
    fprintf(stderr,"DONE graphs=%lld orientations=%lld profiles=%lld ss=%lld tau_skip=%lld safe=%lld checks=%lld packed=%lld cand=%lld deferred=%lld\n",graphs,orientations,profiles,ss_skip,tau_skip,safe_skip,checks,packed,candidates,deferred);
    return 0;
}
