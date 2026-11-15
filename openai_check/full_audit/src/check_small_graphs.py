"""Exhaustive independent small-instance check of a target-2 source adaptation."""
from pathlib import Path
import subprocess,json
R=Path(__file__).resolve().parent.parent
s=(R/'upstream/stageC.cpp').read_text();m=s[s.index(' static inline bool tick(){'):s.index(' static bool duo(')]
assert m.count('6')==4
m=m.replace('6','2').replace('clique(', 'clique2(').replace('exist(', 'exist2(').replace('tick()', 'tick2()')
# Add separate adapted methods using the exact source BS operations.
base=(R/'src/graph_check.cpp').read_text().split('int main(){')[0]
head=base+'\nstruct adapted { static uint64_t steps;static bool gaveup;\n'+m+'\n};\nuint64_t adapted::steps=0;bool adapted::gaveup=false;\n'
mut=m.replace('if(n==2)u.del(i);','u.del(i);').replace('clique2(', 'cliqueBad(').replace('exist2(', 'existBad(').replace('tick2()', 'tickBad()')
head+='struct unsafe {static uint64_t steps;static bool gaveup;\n'+mut+'\n};\nuint64_t unsafe::steps=0;bool unsafe::gaveup=false;\n'
main=r'''
int main(){searchMode=1;capSteps=1000000;int pos=0,mutation=-1;words=1;
for(int code=0;code<(1<<20);code++){nodes.clear();nodes.resize(5);int z=code;F(i,5)F(j,i){int e=z&3;z>>=2;edge(i,j,e&1,e&2);}bool truth=oracle(5,2);pos+=truth;BS p;F(i,5)p.set(i);adapted::steps=0;adapted::gaveup=false;bool q=adapted::exist2(p,p,2);if(adapted::gaveup||q!=truth)abort();if(mutation<0){unsafe::steps=0;unsafe::gaveup=false;if(unsafe::existBad(p,p,2)!=truth)mutation=code;}}
if(mutation!=2471)abort();printf("{\"result\":\"PASS\",\"adapted_target\":2,\"graph_pairs\":1048576,\"positive_pairs\":%d,\"unsafe_mutation_counterexample\":%d}\n",pos,mutation);}
'''
(R/'build/small_graphs.cpp').write_text(head+main)
subprocess.run(['g++','-std=gnu++17','-O2','-ffp-contract=off','-I',str(R/'src'),str(R/'build/small_graphs.cpp'),'-o',str(R/'build/small_graphs')],check=True)
out=subprocess.check_output([str(R/'build/small_graphs')],text=True);json.loads(out)
(R/'results/small-graphs.json').write_text(out);print(out)
