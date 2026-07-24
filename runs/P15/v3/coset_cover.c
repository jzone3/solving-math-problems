/* C port of coset_cover.py (v1): symbolic greedy cover of Z by congruence
 * classes with distinct smooth moduli >= m; holes tracked exactly as cosets
 * (a mod M), uint64. Weighted CRT-greedy residue choice per modulus, with a
 * fragmentation cap (skipping a hit only under-credits coverage => sound).
 * Full sibling families are merged back. Success criterion: hole set empty.
 *
 * Usage: coset_cover inc_cap m max_mod frag_cap out.txt [alpha] [hit_cap]
 * hit_cap: max holes split per emitted class (best = smallest L first)
 * alpha: hole weight = M^alpha / L (alpha>0 favors exact alignment/urgency)
 * frag_cap: split cap for the bootstrap hole (M=1); inc_cap: for all others.
 * Output file: lines "b d" (class b mod d). Verify externally.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#include <math.h>

typedef uint64_t u64;
typedef unsigned __int128 u128;

static const u64 PR[] = {2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,
                         67,71,73,79,83,89,97};
#define NPR (sizeof(PR)/sizeof(PR[0]))

static u64 gcd64(u64 a, u64 b){ while(b){ u64 t=a%b; a=b; b=t;} return a; }

/* ---------- hole hash set (open addressing) ---------- */
typedef struct { u64 a, M; } Hole;
static Hole *tab;
static u64 cap = 1ULL<<22, count = 0, tomb = 0;
static Hole *live; static u64 live_n = 0, live_cap = 1ULL<<22;
#define EMPTY 0xFFFFFFFFFFFFFFFFULL
#define TOMBM 0xFFFFFFFFFFFFFFFEULL

static inline u64 hmix(u64 a, u64 M){
    u64 h = a*0x9E3779B97F4A7C15ULL ^ (M+0x9E3779B97F4A7C15ULL);
    h ^= h>>32; h *= 0xD6E8FEB86659FD93ULL; h ^= h>>32;
    return h;
}
static void tab_init(void){
    tab = malloc(sizeof(Hole)*cap);
    for(u64 i=0;i<cap;i++) tab[i].M = EMPTY;
    live = malloc(sizeof(Hole)*live_cap);
}
static int tab_has(u64 a, u64 M);
static void live_compact(void){
    u64 k=0;
    for(u64 i=0;i<live_n;i++){
        if(tab_has(live[i].a, live[i].M)) live[k++]=live[i];
    }
    live_n=k;
}
static void tab_grow(void);
static int tab_add(u64 a, u64 M){
    if((count+tomb)*10 > cap*7) tab_grow();
    u64 i = hmix(a,M) & (cap-1);
    u64 slot = EMPTY;
    while(tab[i].M != EMPTY){
        if(tab[i].M == TOMBM){ if(slot==EMPTY) slot=i; }
        else if(tab[i].a==a && tab[i].M==M) return 0;
        i = (i+1)&(cap-1);
    }
    if(slot!=EMPTY){ i=slot; tomb--; }
    tab[i].a=a; tab[i].M=M; count++;
    if(live_n==live_cap){ live_cap<<=1; live=realloc(live,sizeof(Hole)*live_cap); }
    live[live_n].a=a; live[live_n].M=M; live_n++;
    return 1;
}
static int tab_has(u64 a, u64 M){
    u64 i = hmix(a,M)&(cap-1);
    while(tab[i].M != EMPTY){
        if(tab[i].M!=TOMBM && tab[i].a==a && tab[i].M==M) return 1;
        i=(i+1)&(cap-1);
    }
    return 0;
}
static int tab_del(u64 a, u64 M){
    u64 i = hmix(a,M)&(cap-1);
    while(tab[i].M != EMPTY){
        if(tab[i].M!=TOMBM && tab[i].a==a && tab[i].M==M){
            tab[i].M = TOMBM; count--; tomb++;
            return 1;
        }
        i=(i+1)&(cap-1);
    }
    return 0;
}
static void tab_grow(void){
    u64 ocap = cap; Hole *ot = tab;
    cap <<= 1;
    tab = malloc(sizeof(Hole)*cap);
    for(u64 i=0;i<cap;i++) tab[i].M = EMPTY;
    count = 0; tomb = 0;
    for(u64 i=0;i<ocap;i++)
        if(ot[i].M!=EMPTY && ot[i].M!=TOMBM) tab_add(ot[i].a, ot[i].M);
    free(ot);
}

/* ---------- smooth number generator (heap, dedup via min-prime-index) --- */
typedef struct { u64 v; unsigned pi; } SN;
static SN *heap; static u64 hn=0, hcap;
static void hpush(u64 v, unsigned pi){
    if(hn==hcap){ hcap<<=1; heap=realloc(heap,sizeof(SN)*hcap); }
    u64 i=hn++; heap[i].v=v; heap[i].pi=pi;
    while(i && heap[(i-1)/2].v>heap[i].v){
        SN t=heap[(i-1)/2]; heap[(i-1)/2]=heap[i]; heap[i]=t; i=(i-1)/2;
    }
}
static SN hpop(void){
    SN r=heap[0]; heap[0]=heap[--hn];
    u64 i=0;
    for(;;){
        u64 l=2*i+1, rr=2*i+2, s=i;
        if(l<hn && heap[l].v<heap[s].v) s=l;
        if(rr<hn && heap[rr].v<heap[s].v) s=rr;
        if(s==i) break;
        SN t=heap[i]; heap[i]=heap[s]; heap[s]=t; i=s;
    }
    return r;
}

/* merge full sibling families around (a, M) */
static void merge_around(u64 a, u64 M){
    int changed = 1;
    while(changed){
        changed = 0;
        for(unsigned pi=0; pi<NPR; pi++){
            u64 p = PR[pi];
            if(M % p) continue;
            u64 Mp = M/p, ap = a % Mp;
            int all = 1;
            for(u64 j=0;j<p;j++)
                if(!tab_has(ap+j*Mp, M)){ all=0; break; }
            if(all){
                for(u64 j=0;j<p;j++) tab_del(ap+j*Mp, M);
                tab_add(ap, Mp);
                a = ap; M = Mp;
                changed = 1;
                break;
            }
        }
    }
}

static u64 m_, inc_cap_, frag_cap_, hit_cap_ = 512;
static double alpha_;
static FILE *out_;
static u64 ncover_ = 0;
static long double density_ = 1.0L;
static time_t t0_;
static u64 scap_;
static Hole *cands;
static u64 *cL;

/* distinct hole moduli snapshot (for cheap prefilter in passes) */
static u64 distM[1<<16]; static u64 ndistM=0;
static u64 dmslot[1<<18];
static void snapshot_distM(void){
    ndistM=0;
    memset(dmslot, 0, sizeof(dmslot));
    for(u64 i=0;i<live_n && ndistM<(1<<16);i++){
        if(!tab_has(live[i].a, live[i].M)) continue;
        u64 M=live[i].M;
        u64 s = (M*0x9E3779B97F4A7C15ULL >> 46) & ((1<<18)-1);
        int found=0;
        while(dmslot[s]){
            if(dmslot[s]==M){ found=1; break; }
            s=(s+1)&((1<<18)-1);
        }
        if(!found){ dmslot[s]=M; distM[ndistM++]=M; }
    }
}
static int worth_trying(u64 d){
    for(u64 j=0;j<ndistM;j++){
        u64 M=distM[j], g=gcd64(d,M);
        u128 L=(u128)(d/g)*M;
        if(L > ((u128)1<<62)) continue;
        if(L/M <= (M==1?frag_cap_:inc_cap_)) return 1;
    }
    return 0;
}

/* try modulus d; returns 1 if a class (b mod d) was emitted */
static int try_modulus(u64 d){
    u64 m = m_, inc_cap = inc_cap_, frag_cap = frag_cap_;
    double alpha = alpha_;
    FILE *out = out_;
    time_t t0 = t0_;
    u64 scap = scap_;
    if(d<m) return 0;
        { static time_t tlast=0;
          time_t nw=time(0);
          if(nw-tlast>=30){ tlast=nw;
            printf("hb d=%llu holes=%llu live=%llu n=%llu t=%lds\n",
              (unsigned long long)d,
              (unsigned long long)count,(unsigned long long)live_n,
              (unsigned long long)ncover_,(long)(nw-t0)); fflush(stdout); }
        }
        /* factorize d */
        u64 pf[NPR], pe[NPR]; unsigned npf=0;
        { u64 x=d;
          for(unsigned pi=0; pi<NPR && x>1; pi++){
              if(x%PR[pi]==0){
                  pf[npf]=PR[pi]; pe[npf]=1; x/=PR[pi];
                  while(x%PR[pi]==0){ pe[npf]*=PR[pi]; x/=PR[pi]; }
                  pe[npf]*=PR[pi]; /* pe = p^e */
                  npf++;
              }
          }
          if(x>1) return 0; /* shouldn't happen */
        }
        if(live_n > 4*count + 1024) live_compact();
        /* collect candidate holes */
        u64 nc=0;
        for(u64 i=0;i<live_n;i++){
            if(!tab_has(live[i].a, live[i].M)) continue;
            u64 M=live[i].M, g=gcd64(d,M);
            u128 L=(u128)(d/g)*M;
            if(L > ((u128)1<<62)) continue;
            if(L/M > (M==1?frag_cap:inc_cap)) continue;
            if(nc==scap){ scap<<=1; scap_=scap; cands=realloc(cands,sizeof(Hole)*scap); cL=realloc(cL,8*scap); }
            cands[nc]=live[i]; cL[nc]=(u64)L; nc++;
        }
        if(!nc) return 0;
        /* CRT greedy per prime power */
        u64 b=0, bmod=1;
        for(unsigned f=0; f<npf; f++){
            u64 p=pf[f], P=pe[f];
            /* weights per (pk, r): use small linear table */
            static u64 wpk[4096], wr[4096]; static double wv[4096];
            unsigned nw=0;
            for(u64 c=0;c<nc;c++){
                u64 M=cands[c].M;
                u64 pk=gcd64(P,M); /* p^min(e,vp(M)) since P=p^e */
                if(pk==1) continue;
                u64 r=cands[c].a % pk;
                unsigned j;
                for(j=0;j<nw;j++) if(wpk[j]==pk&&wr[j]==r) break;
                if(j==nw){ if(nw<4096){ wpk[nw]=pk; wr[nw]=r; wv[nw]=0; nw++; } else continue; }
                wv[j] += pow((double)M, alpha)/(double)cL[c];
            }
            u64 best_r=0; double best_w=-1;
            for(unsigned j0=0;j0<=nw;j0++){
                u64 r = (j0<nw)? wr[j0] : 0;
                double s=0;
                for(unsigned j=0;j<nw;j++) if(r%wpk[j]==wr[j]) s+=wv[j];
                if(s>best_w){ best_w=s; best_r=r; }
            }
            /* filter cands */
            u64 keep=0;
            for(u64 c=0;c<nc;c++){
                u64 pk=gcd64(P,cands[c].M);
                if(pk==1 || best_r%pk==cands[c].a%pk){
                    cands[keep]=cands[c]; cL[keep]=cL[c]; keep++;
                }
            }
            nc=keep;
            /* CRT combine b (mod bmod) with best_r (mod P), coprime */
            { u128 mm=(u128)bmod*P;
              /* find x = b mod bmod, x = best_r mod P */
              u64 x=b;
              while(x % P != best_r) x += bmod; /* P small-ish; ok since P<=d */
              b = x; bmod=(u64)mm;
            }
        }
        /* apply coverage: scan all holes */
        u64 removed_any=0;
        /* collect hits first (can't mutate while scanning) */
        static Hole hits[1<<16]; static u64 hitsL[1<<16]; u64 nh_=0;
        for(u64 i=0;i<live_n;i++){
            if(!tab_has(live[i].a, live[i].M)) continue;
            u64 M=live[i].M, a=live[i].a, g=gcd64(d,M);
            if(b%g != a%g) continue;
            u128 L=(u128)(d/g)*M;
            if(L > ((u128)1<<62)) continue;
            if(L/M > (M==1?frag_cap:inc_cap)) continue;
            if(nh_ < (1<<16)){ hits[nh_]=live[i]; hitsL[nh_]=(u64)L; nh_++; }
        }
        /* keep only the hit_cap_ hits with smallest L (largest coverage);
         * skipping the rest only under-credits coverage (sound) */
        if(nh_ > hit_cap_){
            /* partial selection by L ascending (quickselect) */
            u64 lo=0, hi=nh_-1, k=hit_cap_;
            while(lo<hi){
                u64 pv=hitsL[(lo+hi)/2], i2=lo, j2=hi;
                while(i2<=j2){
                    while(hitsL[i2]<pv) i2++;
                    while(hitsL[j2]>pv) j2--;
                    if(i2<=j2){
                        u64 tl=hitsL[i2]; hitsL[i2]=hitsL[j2]; hitsL[j2]=tl;
                        Hole th=hits[i2]; hits[i2]=hits[j2]; hits[j2]=th;
                        i2++; if(j2) j2--; else break;
                    }
                }
                if(k<=j2) hi=j2;
                else if(k>=i2) lo=i2;
                else break;
            }
            nh_ = hit_cap_;
        }
        for(u64 hI=0;hI<nh_;hI++){
            u64 a=hits[hI].a, M=hits[hI].M, g=gcd64(d,M);
            if(!tab_has(a,M)) continue; /* stale/duplicate */
            u64 L=(u64)((u128)(d/g)*M);
            u64 split=L/M;
            tab_del(a,M);
            density_ -= 1.0L/(long double)L;
            for(u64 j=0;j<split;j++){
                u64 aa=a+j*M;
                if(aa%d==b%d) continue;
                tab_add(aa,L);
            }
            removed_any=1;
            for(u64 j=0;j<split;j++){
                u64 aa=a+j*M;
                if(aa%d==b%d) continue;
                if(tab_has(aa,L)) merge_around(aa,L);
            }
        }
        if(!removed_any) return 0;
        fprintf(out,"%llu %llu\n",(unsigned long long)b,(unsigned long long)d);
        ncover_++;
        if(ncover_%200==0){
            printf("n=%llu d=%llu density=%.3Le holes=%llu t=%lds\n",
                   (unsigned long long)ncover_,(unsigned long long)d,density_,
                   (unsigned long long)count,(long)(time(0)-t0));
            fflush(stdout);
        }
    return 1;
}

int main(int argc, char **argv){
    if(argc < 6){ fprintf(stderr,"usage: %s inc_cap m max_mod frag_cap out [alpha]\n",argv[0]); return 2; }
    inc_cap_ = strtoull(argv[1],0,10);
    m_ = strtoull(argv[2],0,10);
    u64 max_mod = strtoull(argv[3],0,10);
    frag_cap_ = strtoull(argv[4],0,10);
    alpha_ = (argc>6)? atof(argv[6]) : 0.0;
    hit_cap_ = (argc>7)? strtoull(argv[7],0,10) : 512;
    u64 b2=1; while(b2<m_) b2<<=1;
    if(frag_cap_<b2) frag_cap_=b2;
    out_ = fopen(argv[5],"w");
    tab_init();
    tab_add(0,1);
    hcap=1<<20; heap=malloc(sizeof(SN)*hcap); hpush(1,0);
    t0_ = time(0);
    scap_ = 1<<20;
    cands = malloc(sizeof(Hole)*scap_);
    cL = malloc(8*scap_);
    /* pass 1: ascending over the smooth pool; unaccepted d stashed */
    u64 *unused = malloc(8*(1<<20)); u64 un=0, ucap=1<<20;
    u64 prev=0;
    while(count && hn){
        SN sn = hpop();
        u64 d = sn.v;
        for(unsigned pi=sn.pi; pi<NPR; pi++){
            u128 w = (u128)d*PR[pi];
            if(w<=max_mod) hpush((u64)w, pi);
        }
        if(d==prev) continue;
        prev=d;
        if(d<m_) continue;
        if(!try_modulus(d)){
            if(un==ucap){ ucap<<=1; unused=realloc(unused,8*ucap); }
            unused[un++]=d;
        }
    }
    /* further passes over unused moduli until no progress; when a pass
     * makes no progress, escalate the incidental cap (controlled
     * fragmentation of stuck families) until it reaches frag_cap_ */
    while(count){
        u64 k=0, progress=0;
        snapshot_distM();
        for(u64 i=0;i<un;i++){
            if(count && worth_trying(unused[i]) && try_modulus(unused[i])){
                progress++;
                if(progress % 256 == 0) snapshot_distM();
            }
            else unused[k++]=unused[i];
        }
        un=k;
        printf("pass done: accepted=%llu remaining_pool=%llu holes=%llu density=%.3Le inc_cap=%llu\n",
               (unsigned long long)progress,(unsigned long long)un,
               (unsigned long long)count,density_,
               (unsigned long long)inc_cap_);
        fflush(stdout);
        if(!progress){
            if(inc_cap_ >= frag_cap_) break;
            inc_cap_ *= 2;
            if(inc_cap_ > frag_cap_) inc_cap_ = frag_cap_;
        }
    }
    fclose(out_);
    if(count==0){ printf("COVERED n=%llu\n",(unsigned long long)ncover_); return 0; }
    printf("FAILED holes=%llu density=%.3Le\n",(unsigned long long)count,density_);
    return 1;
}
