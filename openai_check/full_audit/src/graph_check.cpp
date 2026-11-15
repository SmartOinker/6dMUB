#define STAGEC_HEADER
#include "../upstream/stageC.cpp"
#include <random>
#include <functional>
bool oracle(int n,int k){
 vector<vector<int>> sets;vector<int> c(k);iota(c.begin(),c.end(),0);
 if(n<2*k)return false;
 while(true){bool ok=true;FOR(i,k)FOR(j,i)if(!(nodes[c[i]].O.data[c[j]/64]>>(c[j]%64)&1))ok=false;if(ok)sets.push_back(c);
 int j=k-1;while(j>=0 && c[j]==n-k+j)--j;if(j<0)break;++c[j];for(int h=j+1;h<k;h++)c[h]=c[h-1]+1;}
 for(size_t i=0;i<sets.size();i++)for(size_t j=i+1;j<sets.size();j++){bool ok=true;for(int a:sets[i])for(int b:sets[j])if(a==b || !(nodes[a].U.data[b/64]>>(b%64)&1))ok=false;if(ok)return true;}
 return false;
}
void edge(int i,int j,bool o,bool u){if(o){nodes[i].O.set(j);nodes[j].O.set(i);}if(u){nodes[i].U.set(j);nodes[j].U.set(i);}}
pair<bool,bool> search(int n,uint64_t cap){BS p;FOR(i,n)p.set(i);capSteps=cap;graph::steps=0;graph::gaveup=false;bool q=graph::exist(p,p,6);return {q||graph::gaveup,graph::gaveup};}
int main(){
 searchMode=1;mt19937_64 rng(12420261114ull);int total=0,pos=0,caps=0;
 for(int n=12;n<=18;n++)FOR(t,50){nodes.clear();nodes.resize(n);words=(n+63)/64;
 FOR(i,n)FOR(j,i){bool o=rng()%100<40+(t%6)*10;bool u=rng()%100<45+(t%6)*10;edge(i,j,o,u);}
 if(t%5==0){vector<int> v(n);iota(v.begin(),v.end(),0);for(int h=n-1;h>0;--h)swap(v[h],v[rng()%(h+1)]);FOR(i,6)FOR(j,i){edge(v[i],v[j],1,0);edge(v[i+6],v[j+6],1,0);}FOR(i,6)for(int j=6;j<12;j++)edge(v[i],v[j],0,1);}
 bool truth=oracle(n,6);auto q=search(n,1000000000);if(q.second||q.first!=truth)abort();pos+=truth;total++;
 auto cap=search(n,0);if(!cap.first||!cap.second)abort();caps++;
 }
 // Exercise exact word boundary and maximal node ID in the source BS.
 vector<int> labels={0,1,62,63,64,65,127,128,129,1023,2046,2047};nodes.clear();nodes.resize(2048);words=32;
 FOR(i,6)FOR(j,i){edge(labels[i],labels[j],1,0);edge(labels[i+6],labels[j+6],1,0);}FOR(i,6)for(int j=6;j<12;j++)edge(labels[i],labels[j],0,1);
 auto p=search(2048,10000000);if(!p.first||p.second)abort();nodes[labels[0]].O.del(labels[1]);nodes[labels[1]].O.del(labels[0]);auto q=search(2048,10000000);if(q.first||q.second)abort();
 printf("{\"result\":\"PASS\",\"original_target6_cases\":%d,\"positive_cases\":%d,\"forced_cap_cases\":%d,\"boundary_2048_cases\":2,\"seed\":12420261114}\n",total,pos,caps);
}
