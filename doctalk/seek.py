from .talk import *

def tp(x,y) :
  return nx.tensor_product(x,y)


class Seeker(Talker) :
  '''
  extends Talker with tensor product ranking
  based QA attempt

  '''
  def __init__(self,**kwargs):
    super().__init__(**kwargs)

  def qa(self):
    #self.show_all()
    qfname=self.from_file.replace('.txt','_quest.txt')
    l=''
    with ropen(qfname) as f:
      q=f.readline()
    answerer = Talker(from_text=q)
    #answerer.show_all()

    dg=self.g

    qg=nx.DiGraph()
    for e  in answerer.g.edges() :
      fr, to=e
      if fr==0 : fr= -1
      if to==0 : to= -1
      qg.add_edge(fr,to)

    print(dg.number_of_edges())
    print(qg.number_of_edges())

    tg=tp(qg,dg)
    pr=nx.pagerank(tg)

    print('TG:',tg.number_of_nodes(),tg.number_of_edges())

    print('QUESTION:',q)
    ids=defaultdict(set)
    for n,r in pr.items() :
      f,t=n
      if f!= -1 and isinstance(t,int) :
        ids[t].add(r)

    d=dict()
    for s,rs in ids.items() :
      d[s]=sum(rs)

    d=self.adjust_sent_ranks(d)

    pr = sorted(d.items(), key=lambda x: x[1], reverse=True)

    for id,r in take(3,pr) :
      print(id,nice(self.get_sentence(id)))
