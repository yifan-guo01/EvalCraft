from .params import *
from graphviz import Digraph as DotGraph
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import networkx as nx
import json

def showGraph(dot, show=True, file_name='textgraph.gv'):
  dot.render(file_name, view=show)

def gshow(g, attr=None, file_name='temp.gv', show=1,json_save=True):

  size=g.number_of_edges()
  nsize=g.number_of_nodes()

  if size < 3 :
    #ppp('GRAPH TOO SMALL TO SHOW:', file_name, 'nodes:',nsize,'edges:', size)
    pass
    return
  elif size <3000 :
    #ppp('SHOWING:',file_name, 'nodes:',nsize,'edges:', size)
    pass
  else:
    #ppp('TOO BIG TO SHOW:',file_name, 'nodes:',nsize,'edges:', size)
    return
  dot = DotGraph()
  es=[]
  for e in g.edges():
    f, t = e
    if not attr : w= ''
    else :
      w = g[f][t].get(attr)
      if not w : w=''
    if not isinstance(f,str) : continue
    if not isinstance(t,str) : continue
    f= f.replace(':','.')
    t = t.replace(':', '.')
    f=str(f)
    t=str(t)
    w=str(w)
    dot.edge(f, t, label=w)
    if json_save : es.append((f,t,w))
  if json_save :
    jfile=file_name+".json"
    with wopen(jfile) as jf :
      json.dump(es,jf)
  dot.render(file_name, view=show>1)

def pshow(t, file_name="temp",cloud_size=24,show=1):
  file_name=file_name[:-4]
  def t2s(x) :
    if isinstance(x,tuple) :
      return " ".join(x)
    return x
  sum, kws = t.extract_content(5, cloud_size)
  #for x in t.by_rank:ppp(x)
  d=dict()
  s=set()
  for kw in kws:
    if isinstance(kw,tuple) :
      if any(isinstance(t,tuple) for t in kw) :
          continue
      kw0=tuple(map(lambda x: x.lower(),kw))
      d[t2s(kw)]=t.pr[kw0]
      s.add(kw0)
    else :
      lkw=kw.lower()
      d[kw]=t.pr[lkw]
      s.add(lkw)
  #ppp("CLOUD",d)
  show_ranks(d,file_name=file_name+"_cloud.pdf",show=show)
  '''
  #ppp('SUBGRAPH',s)
  if t.g.number_of_edges()<80:
    topg=t.g
  else :
    topg=nx.DiGraph()
    for x in s :
      for y in t.g[x] :
        if isinstance(y,int) : continue
        topg.add_edge(x,y)
        zs=t.g[y]
        if zs :
          for z in zs :
            if z in s :
              topg.add_edge(y,z)

  gshow(topg,file_name=file_name+".gv",show=show)
  '''

def show_ranks(rank_dict,file_name="cloud.pdf",show=1) :
  cloud=WordCloud(width=800,height=400)
  cloud.fit_words(rank_dict)
  f=plt.figure()
  plt.imshow(cloud, interpolation='bilinear')
  plt.axis("off")
  if show>1 : plt.show()
  f.savefig(file_name,bbox_inches='tight')
  plt.close('all')

def plot_rank_orbit(rs) :
  #plt.xscale('log')
  if not rs :
    print('empty plot')
    return
  xs,ys=zip(*rs)
  plt.plot(xs,ys)
  plt.show()
