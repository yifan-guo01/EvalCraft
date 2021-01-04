from collections import defaultdict
import subprocess
from pathlib import Path
import math
import networkx as nx
from nltk.corpus import words as wn_words
import statistics as stat
from collections import OrderedDict
import os.path as osp
import os
#from pprint import pprint
import json

from .nlp import *
from .sim import *
from .refiner import refine, ask_bert
from .vis import pshow,gshow

client = NLPclient()

def my_path() :
  '''
  detects directory where package sources get installed
  useful to load .json, .txt etc. resources from there
  '''
  if __name__=='__main__' :
    return "./"
  else :
    return __file__

def get_freqs() :
  '''
  loads .json file contining frequencies
  for around 20k English words
  '''
  global lemma_freqs
  if lemma_freqs : return lemma_freqs
  fname=my_path().replace('talk.py','lemmas.json')
  with ropen(fname) as f:
    lemma_freqs=json.load(f)
    return lemma_freqs

# set of WordNet words
wnet_words = set(wn_words.words())

# global holder for lemma frequences, filled out on first use
lemma_freqs = None

def run_with(fname,query=True) :
  '''
  Activates dialog about document in <fname>.txt with questions
  in <fname>_quests.txt
  Assumes stanford corenlp server listening on port 9000
  with annotators listed in params.py  available.
  '''
  t = Talker(from_file=fname+'.txt')
  show =t.params.show_pics

  t.show_all()
  if query:
    fshown=fname+'_quest.txt'
    t.query_with(fshown)
    if show :
      pshow(t,file_name=fshown,
          cloud_size=t.params.cloud_size,
          show=t.params.show_pics)

def run_with_pdf(fname,**kwargs) :
  pdf2txt(fname)
  run_with(fname, **kwargs)

def chat_about(fname,qs=None) :
  t = Talker(from_file=fname + '.txt')
  t.show_all()
  t.query_with(qs)



def tprint(*args) :
  ''' custom print when trace on'''
  if trace : print(*args)


def tload(infile) :
  ''' load a .txt file'''
  tprint('LOADING:',infile,'\n')
  with ropen(infile) as f: text = f.read()
  return digest(text)

def jload(infile) :
  ''' loads .json file, preprocessed from a .txt file'''
  with ropen(infile) as f:
    res = json.load(f)
    return res

def jsave(infile,outfile):
  '''preprocesses a .txt file to a .json file'''
  d=tload(infile)
  with wopen(outfile) as g:
    json.dump(d,g,indent=0)

def exists_file(fname) :
  '''true when a file exists'''
  path = Path(fname)
  return path.is_file()

def load(fname,force=0) :
  '''loads a .txt file or its .json file if it exists'''
  if fname[-4:]==".txt":
    if force:
      db = tload(fname)
    else :
      jfname=fname[:-4]+".json"
      if not exists_file(jfname) :
        jsave(fname,jfname)
      db=jload(jfname)
  else:
    db = jload(fname)
  return db

def get_quests(qs) :
  ''' decodes questions from list or file'''
  if not isinstance(qs,list) :
    qfname=qs
    with ropen(qfname) as f:
      qs = list(l.strip() for l in f)
  return qs

def digest(text) :
  ''' process text with the NLP toolkit'''
  l2occ = defaultdict(list)
  sent_data=[]
  # calls server here
  for i,xss in enumerate(client.extract(text)) :
    lexs,deps,ies=xss
    sent,lemma,tag,ner,before=[],[],[],[], []
    for j,t in enumerate(lexs):
      w,l,p,n,b=t
      wi=len(l2occ)
      l2occ[l].append((i,j))
      sent.append(w)
      lemma.append(l)
      tag.append(p)
      ner.append(n)
      before.append(b)
    d=(tuple(sent),tuple(lemma),tuple(tag),
       tuple(ner), tuple(before), tuple(deps),tuple(ies))
    sent_data.append(d)
    '''
    for i in range(len(sent_data)):
      text = ""
      for j in range(len(sent_data[i][SENT])):
         text += sent_data[i][BEFORE][j] + sent_data[i][SENT][j]
      print(i, ':', text )  
    '''  
    #print("\nl2occ:")
    #print(l2occ)
  return sent_data,l2occ

# names of components of fileds in json array
# collecting results of corenlp, for faster processing
SENT,LEMMA,TAG,NER,BEFORE,DEP,IE=0,1,2,3,4,5,6

def to_sents (text) :
  '''
  generator of sentences from text string
  '''
  sent_data,_= digest(text)
  for x in sent_data :
    yield x[SENT]

def rel_from(d):
  ''' extracts several relations as SVO triplets'''
  def to_lems(ux):
    f,t=ux
    if f>=0:
      for u in range(*ux):
        yield lemma[u],tag[u]
  def lems(xs) : return tuple(x[0] for x in xs)
  rs,svos=set(),set()
  for ts in d[IE] :
    for t in ts :
      sx, vx, ox = t
      lemma = d[LEMMA]
      tag=d[TAG]
      sub = tuple(to_lems(sx))
      rel = tuple(to_lems(vx))
      ob = tuple(to_lems(ox))
      res = (sub, rel, ob)
      s=()
      for l,tl in sub:
        if tl[0]=='N' :
          s=l
      o=()
      for l, tl in ob:
        if tl[0] == 'N':
          o = l
      v=()
      for l, tl in rel:
        if tl[0] == 'V':
          v = l
      rs.add(res)
      svo=s,v,o
      if () in svo or s==o : continue
      svos.add(svo)
      if len(sub)>1 : svos.add((s,'subject_in',lems(sub)))
      if len(ob) > 1 : svos.add((o, 'object_in', lems(ob)))
      if len(rel)>1 : svos.add((v, 'verb_in', lems(rel)))

  return tuple(rs),tuple(svos)

def dep_from(id,d):
  ''' extracts dependenciy relations deom given sentece id'''
  deps=d[DEP]
  lemmas=d[LEMMA]
  tags=d[TAG]
  for dep in deps :
    f, r, t = dep
    if t == -1 : target,ttag=id,'SENT'
    else: target,ttag = lemmas[t],tags[t]
    res = lemmas[f],tags[f],r,target,ttag
    yield res

def deps_from(id,d) :
  ''' extracts all dependency relations as nexted tuples'''
  return tuple(t for t in dep_from(id,d))

def comp_from(id,d) :
  '''turns compound annotations into pairs'''
  for x in dep_from(id,d) :
    f,tf,rel,t,tt=x
    if rel in ('compound', 'amod', 'conj:and') and \
       good_word(f) and good_word(t) and \
       good_tag(tf) and good_tag(tt) :
      yield (f,t)

def comps_from(id,d) :
  ''' returns compounds in sentence id as nested tuples of positions'''
  return tuple(t for t in comp_from(id,d) if t)

def sub_centered(id,dep,all_to_sent=True) :
  '''builds dependency graphs centered on subjects and sentences'''
  f, f_, r, t, t_ = dep
  if r == 'punct' or f == t:
    pass
  elif r in ['nsubj'] and f_[0] == 'N':
    yield (id, f)  # sent to subject
    yield (f, id)  # subject to sent
    yield (t, f)  # pred to subject
  elif r in ['nsubj', 'dobj', 'iobj'] : #or t_[0] == 'V':
    if good_word(t) and good_word(f) :
      yield f, t  # arg to pred
      yield t, id  # pred to sent
  # elif r == 'ROOT': yield (f, t)
  else:
    yield (f, t)
    if all_to_sent:
      yield (f,id)


def pred_mediated(id,dep) :
  '''build dependency graphs mediated by predicates'''
  f, f_, r, t, t_ = dep
  if r == 'punct' or f==t:
    pass
  elif r in ['nsubj', 'dobj', 'iobj'] or t_[0] == 'V':
    yield (id, f)  # sent to predicate
    if good_word(t) and good_word(f) : yield t,f  #  pred to arg
    if good_word(t) : yield id, t  # sent to pred
    yield (f, id)  # arg to sent
  elif r == 'ROOT':
    yield (t, f)
  else:
    yield (f, t)


def get_avg_len(db) :
  ''' returns average length of sentences'''
  sent_data,_=db
  lens=[len(x[LEMMA]) for x in sent_data]
  n=len(lens)
  s=sum(lens)
  return round(s/n)

def rank_sort(pr) :
  ''' sort dict by ranks associatied to its keys'''
  by_rank=[(x,r) for (x,r) in pr.items()]
  by_rank.sort(key=lambda x : x[1],reverse=True)
  #for x in take(100, by_rank):
    #if not isinstance(x, int):
      #ppp('BY RANK', x)
  return by_rank

def ners_from(d):
  ''' extracts useful named entities'''
  ners=[]
  for j, ner in enumerate(d[NER]):
    lemma = d[LEMMA][j]
    if ner != 'O' and good_word(lemma): ners.append((lemma,ner))
  return tuple(ners)

def materialize(db) :
  '''converts relations from positions to actual lemmas'''
  sent_data,l2occ= db
  for i,d in enumerate(sent_data) :
      rels,svos = rel_from(d)
      deps=deps_from(i,d)
      comps=comps_from(i,d) # or directly from deps
      ners=ners_from(d)
      yield tuple(d[SENT]),tuple(d[LEMMA]),tuple(d[TAG]),\
            ners,rels,svos,deps,comps

def wn_from(l2occ) :
  '''extracts likely WordNet relations between lemmas'''
  for w in l2occ :
    if not good_word(w) : continue
    for s,v,o in wn_svo(2,10,w,'n') :
      if l2occ.get(o) :
        yield (s,v,o)
    for s, v, o in wn_svo(2, 10, w, 'v'):
      if l2occ.get(o):
        yield (s, v, o)
    for s, v, o in wn_svo(2, 10, w, 'a'):
      if l2occ.get(o):
        yield (s, v, o)

def v2rel(v) :
  '''rewrites "be" lemma to "i"s, for more natural reading of relations'''
  if v=='be' : return 'is'
  return v

def e2rel(e) :
  '''turns NER tags into common words'''
  if e=='MISC' : return 'entity'
  return e.lower()

def answer_quest_org(q,talker) :
  '''
  given question q, interacts with talker and returns
  its best answers
  '''
  max_answers = talker.params.max_answers
  db = talker.db
  sent_data, l2occ = db
  matches = defaultdict(set)
  nears = defaultdict(set)

  unknowns = []
  q_lemmas=[]
  if talker.params.with_answerer:
    answerer = Talker(from_text=q)
    q_sent_data,_=answerer.db
    for j, q_lemma in enumerate(q_sent_data[0][LEMMA]):
      q_sent_data, q_l2occ = answerer.db
      q_tag = q_sent_data[0][TAG][j]
      if q_tag[0] not in "NVJ": continue  # ppp(q_lemma,q_tag)
      q_lemmas.append((q_lemma,wn_tag(q_tag)))
  else:
    answerer = None
    from nltk.tokenize import word_tokenize
    from nltk.stem import WordNetLemmatizer
    wnl = WordNetLemmatizer()
    toks=word_tokenize(q)
    tag=None
    for t in toks:
      tag='n'
      l = wnl.lemmatize(t,tag)
      if l==t :
        tag='v'
        l=wnl.lemmatize(t,tag)
      if l==t :
        tag='a'
        l = wnl.lemmatize(t, tag)
      l=l.lower()
      q_lemmas.append((l,tag))

  for q_lemma,wn_q_tag in q_lemmas:
    if not good_word(q_lemma) or q_lemma in ".?": continue

    #  actual QA starts here
    ys = l2occ.get(q_lemma)

    if not ys:
      unknowns.append(q_lemma)
    else:
      for sent, _pos in ys:
        matches[sent].add(q_lemma)
    if talker.params.expand_query > 0:
      related = wn_all(talker.params.expand_query, 3, q_lemma, wn_q_tag)
      for r_lemma in related:
        if not good_word(q_lemma): continue
        zs = l2occ.get(r_lemma)
        if not zs: continue
        for r_sent, _r_pos in zs:
          nears[r_sent].add((r_lemma, q_lemma))
        if zs and not ys:
          if q_lemma in unknowns: unknowns.pop()
        tprint('EXPANDED:', q_lemma, '-->', r_lemma)
  tprint('')
  if unknowns: tprint("UNKNOWNS:", unknowns, '\n')

  best = []
  if talker.params.pers and talker.params.with_answerer:
    d = {x: r for x, r in answerer.pr.items() if good_word(x)}
    talker.pr = nx.pagerank(talker.g, personalization=d)

  for (id, shared) in matches.items():
    sent = sent_data[id][SENT]
    r = answer_rank(id, shared, sent, talker, expanded=0)
    # ppp(id,r,shared)
    best.append((r, id, shared, sent))
    # ppp('MATCH', id,shared, r)

  for (id, shared_source) in nears.items():
    shared = {x for x, _ in shared_source}
    sent = sent_data[id][SENT]
    r = answer_rank(id, shared, sent, talker, expanded=1)
    best.append((r, id, shared, sent))
    # ppp('EXPAND', id,shared, r)

  best.sort(reverse=True)

  answers = []
  for i, b in enumerate(best):
    if i >= max_answers: break
    #ppp(i,b)
    rank, id, shared, sent = b
    answers.append((id, sent, round(rank, 4), shared))

  if talker.params.with_refiner:
    wss =  [ws for (_,ws,_,_) in answers]
    wss=refine_wss(wss,talker)
    answers=[(0,ws,0,set()) for ws in wss]
  return answers, answerer


def refine_wss(wss,talker):
    '''
    refines a few dozen lists of lists of words (extractive summary or
    set of answer senteces) with BERT, for a second opinion on
    what the best shorter summary or answer would be
    '''
    sents = []
    for ws in wss:
      sents.append(nice(ws))
    if not wss: return wss
    input = " ".join(sents)
    how=talker.params.with_refiner
    output = refine(input,how)  # <====== calling refiner
    xss = list(to_sents(output))
    wss=list(take(talker.params.top_answers,wss))
    return [['DOCTALK:']]+wss+\
           [['BERT REFINING LARGER TEXT EXTRACTED BY DOCTALK:']]+\
           xss

def sigmoid(x): return 1 / (1 + math.exp(-x))


#Ripple
import networkx.algorithms as nxAlg
def answer_quest(q,talker) :
  '''
  given question q, interacts with talker and returns
  its best answers
  '''
  max_answers = talker.params.max_answers
  db = talker.db
  sent_data, l2occ = db

  unknowns = []
  q_lemmas=[]
  if talker.params.with_answerer:
    answerer = Talker(from_text=q)
    q_sent_data,_=answerer.db
    for j, q_lemma in enumerate(q_sent_data[0][LEMMA]):
      q_sent_data, q_l2occ = answerer.db
      q_tag = q_sent_data[0][TAG][j]
      if q_tag[0] not in "NVJ": continue  # ppp(q_lemma,q_tag)
      q_lemmas.append((q_lemma,wn_tag(q_tag)))
  else:
    answerer = None
    from nltk.tokenize import word_tokenize
    from nltk.stem import WordNetLemmatizer
    wnl = WordNetLemmatizer()
    toks=word_tokenize(q)
    tag=None
    for t in toks:
      tag='n'
      l = wnl.lemmatize(t,tag)
      if l==t :
        tag='v'
        l=wnl.lemmatize(t,tag)
      if l==t :
        tag='a'
        l = wnl.lemmatize(t, tag)
      l=l.lower()
      q_lemmas.append((l,tag))

  matches = []
  nears = []
  sharesDict = defaultdict(set)  
  count = defaultdict(int)

  for q_lemma,wn_q_tag in q_lemmas:
    if not good_word(q_lemma) or q_lemma in ".?": continue

    #  actual QA starts here
    ys = l2occ.get(q_lemma)

    if ys:
      matches.append(q_lemma)
      for sent, _pos in ys:
        sharesDict[sent].add(q_lemma)
        count[q_lemma] += 1 
    else:
      if talker.params.expand_query > 0:
        related = wn_all(talker.params.expand_query, 3, q_lemma, wn_q_tag)
        for r_lemma in related:
          if not good_word(q_lemma): continue
          zs = l2occ.get(r_lemma)
          if not zs: 
            tprint("UNKNOWNS:", q_lemma, '\n')
            continue
          nears.append(r_lemma)
          tprint('EXPANDED:', q_lemma, '-->', r_lemma)
          for sent, _pos in zs:
            sharesDict[sent].add(r_lemma)
            count[r_lemma] +=1 

  #print('count:',count )
  
  ignored = []
  for lemma in count:
    if(count[lemma] > 3):
      ignored.append(lemma)

  #print('ignored:', ignored)
  
  lavg=talker.avg_len
  
  best = []
  for id in sharesDict:
    sent = sent_data[id][SENT]
    lsent = len(sent)
    if lsent > 2*lavg :
      sharedNum = len(sharesDict[id])
      if sharedNum ==1 : 
        shares = list(sharesDict[id])
        if shares[0] in ignored : 
          continue
    r = 0
    for key in matches:
      if (key in ignored ): 
        if (key in sharesDict[id]):
          r += 1.0
        continue
        
      if (nxAlg.has_path(talker.g, key, id)):
        nodes = nxAlg.shortest_path(talker.g, key, id)
        if(len(nodes)<6):
          n = math.pow(2, len(nodes)-1)
          r += 16.0/n

    
    for key in nears:
      if key not in talker.g.nodes(): continue
      if (key in ignored ): 
        if (key in sharesDict[id]):
          r += 0.5
        continue

      if(nxAlg.has_path(talker.g, key, id)):
        nodes = nxAlg.shortest_path(talker.g, key, id)
        #print('****************nears, key:id=', key, ':', id, ', get nodes, length:', len(nodes), 'nodes:', nodes)
        if(len(nodes)<6):
          n = math.pow(2, len(nodes)-1)
          r += 8.0/n      
    best.append((r, id, sharesDict[id], sent))
  
  best.sort(reverse=True)

  answers = []
  last_rank = 0
  for i, b in enumerate(best):
    if i >= max_answers: break
    #ppp(i,b)
    rank, id, shared, sent = b
    if last_rank != 0:
      if rank/last_rank <0.70: break
    last_rank = rank
    answers.append((id, sent, round(rank, 4), shared))
  return answers, answerer

  

def answer_rank(id,shared,sent,talker,expanded=0) :
  '''ranks answer sentence id using several parameters'''

  lshared = len(shared)
  if not lshared : return 0

  sent_count=len(talker.db[0])
  #word_count=len(talker.db[1])

  lsent = len(sent)
  lavg=talker.avg_len
  srank=talker.pr.get(id)


  nrank=normalize_sent(srank,lsent,lavg)

  if nrank==0 : return 0

  def get_occ_count(x): return len(talker.db[1].get(x))

  unusual = sigmoid(1 - stat.harmonic_mean(
    get_occ_count(x) for x in shared) / sent_count)

  important=math.exp(nrank)

  # #r=stat.harmonic_mean((lshared,important,unusual))
  r=lshared*important*unusual

  if expanded : r=r/2

  #ppp('RANKS:',10000*srank,'-->',10000*nrank,lsent,lavg)
  #ppp('HOW  :', id, lshared, unusual, important, shared,'--->',r)

  #r=math.tanh(r)
  return r

def query_with(talker,qs_or_fname)     :
  ''' queries talker with questions from file or list'''
  if isinstance(qs_or_fname,str) :
    qs = get_quests(qs_or_fname) # file name
  else :
    qs=qs_or_fname # list of questions or None
  talkAnswer = []
  thinkAnswer = []
  if qs:
    for q in qs :
      if not q :break
      talka, thinka = interact(q,talker)
      talkAnswer.append(talka)
      thinkAnswer.append(thinka)
  else:
    while True:
      q=input('> ')
      if not q : break
      talka, thinka = interact(q,talker)
      talkAnswer.append(talka)
      thinkAnswer.append(thinka)
  return talkAnswer, thinkAnswer

def interact(q,talker):
  ''' prints/says query and answers'''
  tprint('----- QUERY ----\n')
  #print("\n===========>QUESTION: ",end='')
  #talker.say(q)
  #print('')
  ### answer is computed here ###
  answers,answerer=answer_quest(q, talker)
  #show_answers(talker,answers)
  return talker.distill(q,answers,answerer)

def show_answers(talker,answers) :
  ''' prints out/says answers'''
  print('ANSWERS:\n')
  if not talker.params.with_refiner :
    answers=take(talker.params.max_answers,answers)
    if not talker.params.answers_by_rank:
      answers=sorted(answers)
  for id, sent, rank, shared in answers:
    if not talker.params.with_refiner :
       print(id, ',rank=' , rank, end=': ')
    talker.say(niceWithSentId(id, talker))
    if not talker.params.with_refiner:
      tprint('  ', shared, rank)
    print('')
  tprint('------END-------', '\n')

class Talker :
  '''
  class aggregating summary, keyphrase, relation extraction
  as well as query answering in the form of extracted sentences
  based on given file or text or preprocessed json equivalent
  '''
  def __init__(self,
               from_json=None,
               from_file=None,
               from_text=None,
               from_pdf=None,
               params=talk_params()
               ):
    '''creates data container from file or text document'''
    self.params=params
    self.from_file=from_file
    if from_pdf:
       from_pdf=from_pdf.replace('.pdf','')
       pdf2txt(from_pdf)
       self.from_file=from_pdf+".txt"
       self.db = load(self.from_file, self.params.force)
    elif from_file:
       self.db=load(from_file,self.params.force)
       self.from_file=from_file
    elif from_text :
       self.db=digest(from_text)
    elif from_json :
      xs=json.loads(from_json)
      assert isinstance(xs,list) and len(xs)==1
      text=xs[0]
      self.db = digest(text)
    else :
      assert from_file or from_text or from_json

    self.avg_len = get_avg_len(self.db)

    self.svos=self.to_svos()
    self.svo_graph=None

    self.g,self.pr=self.to_graph()

    self.summary, self.keywords = \
      self.extract_content(self.params.max_sum, self.params.max_keys)
    assert self.by_rank != None

  def get_summary(self):
    '''
    function  extracting highest ranked sentences as summary
    '''
    yield from take(self.params.top_sum,self.summary)

  def get_keys(self):
    '''
       function for extracting highest ranked keywords
     '''
    yield from take(self.params.top_keys,nice_keys(self.keywords))

  def summary_sentences(self):
    '''
      API function  extracting highest ranked sentences as summary
      encoded as a list of list of words in json form
     '''

    wss=[x[2] for x in self.get_summary()]
    return json.dumps(wss)

  def keyphrases(self):
    ''' API  function for extracting highest ranked keywords as
        a json encoded list of words
    '''
    ks=json.dumps(list(self.get_keys()))
    return ks

  def answer_question(self,quest,is_json=False):
    '''
    answers question given as a string,
    returns answer possibly in jsno form
    '''
    assert isinstance(quest, str)
    if is_json :
      qs = json.loads(quest)
      q=qs[0]
    else :
      q =quest
    xs,_=self.answer_quest(q)
    rss=[a[1] for a in xs]
    b=None
    if self.params.with_bert_qa > 0 :
      wss=[' '.join(ws) for ws in rss]
      ws = ' '.join(wss)
      b=ask_bert(ws,q,confid=self.params.with_bert_qa)
    answers = list(take(self.params.top_answers,rss))

    if b :
       b="Short answer : "+b+" !"
       bs=b.split(' ')
       answers=[bs]+answers
    return json.dumps(answers)

  def answer_quest(self,q):
    '''answers question q'''
    return answer_quest(q,self)

  def query_with(self,qs):
    '''answers list of questions'''
    return query_with(self,qs)

  def get_tagged(self,w):
    '''adds tags to given lemma w'''
    l2occ=self.db[1]
    sent_data=self.db[0]
    occs=l2occ.get(w)
    if not occs : return None

    tags=set()
    words=set()
    for i,j in occs:
      word = sent_data[i][SENT][j]
      tag=sent_data[i][TAG][j]
      words.add(word)
      tags.add(tag)
    return words,tags

  def get_occs(self,lemma):
    return self.db[1].get(lemma)

  def to_ids(self,nodes) :
    '''
    returns sentence ids for lemma nodes in the graph
    by looking them up in the word-to-sentence occurrence map
    '''
    ids=set()
    for w in nodes :
      occs=self.get_occs(w)
      if not occs : continue
      for occ in self.get_occs(w) :
        ids.add(occ[0])
    #return {occ[0] for w in nodes for occ in self.get_occs(w)}
    return ids


  def adjust_sent_ranks(self,pr):
    '''
    adjust sentence and jeyword ranks via heuristics
    in normalize_sent and normalize_key
    '''
    npr = dict()
    for x, r in pr.items():
      if isinstance(x, int):
        ws = self.db[0][x][SENT]
        r = normalize_sent(r, len(ws), self.avg_len)
      else:
        r = self.normalize_key(x,r)
      npr[x] = r

    return npr

  def get_sentence(self,i):
    ''' returns sentence i as list of words'''
    return  self.db[0][i][SENT]

  def get_before(self,i):
    ''' gets the named entity annotations of sentence i'''
    before=self.db[0][i][BEFORE]
    return before

  def get_lemma(self,i):
    ''' returns lemmas of sentence i as list of words'''
    return  self.db[0][i][LEMMA]

  def get_word(self,i):
    ''' returns words of sentence i as list'''
    return  self.db[0][i][SENT]

  def get_tag(self,i):
    ''' gets the POS tags of sentence i'''
    return  self.db[0][i][TAG]

  def get_ner(self,i):
    ''' gets the named entity annotations of sentence i'''
    ner=  self.db[0][i][NER]
    if ner=='O' : return None
    return ner

  def extract_content(self,sk,wk):
    '''extracts summaries and keywords'''

    def maybe_cap(x) :
        ws,_ = self.get_tagged(x)
        cx = x.capitalize()
        if cx in ws and x not in ws: x = cx
        return x

    def nice_word(x,good_tags='N',lift=False) :
      '''
        heuristics for filtering and prioritizing
        words and compound words
      '''
      ws_ts=self.get_tagged(x)
      if not ws_ts : return None
      ws, tags = ws_ts
      ncount = 0
      for tag in tags:
        if tag[0] in good_tags:
          ncount += 1
      if ncount > len(tags) / 2:
        ns=self.g.adj.get(x)
        # lifts compounds to higher ranks if that makes sense
        if lift and ns and not isinstance(x,tuple):
          min_rank=self.pr[x] / self.params.prioritize_compounds
          xss=[(n,self.pr[n])
               for n in ns
                 if isinstance(n,tuple) and x==n[1] and
                   #self.pr[n[0]] > self.pr[n[1]]/2 and
                   n[0] != n[1] and
                   self.pr[n] >  min_rank
              ]
          if xss:
            xss.sort(key=lambda v: v[1], reverse=True)
            #ppp(xss)
            xs=xss[0][0]
            return xs
        return x
      else:
        return None

    sents,words=list(),OrderedDict()
    npr=self.adjust_sent_ranks(self.pr)
    # ordering all by rank here
    by_rank=rank_sort(npr)
    self.by_rank = by_rank

    # collect best by rank, but adjusting some
    for i  in range(len(by_rank)):
      x,r=by_rank[i]
      if sk and isinstance(x,int) :
        ws=self.db[0][x][SENT]
        ls=self.db[0][x][LEMMA]
        if not is_clean_sent(ls,self.params.known_ratio) : continue
        sk-=1
        sents.append((r,x,ws))
      elif wk and good_word(x) :
        #ppp('PWS', x)
        x=nice_word(x,lift=self.params.prioritize_compounds>0)
        if x:
          wk -= 1
          #ppp('LWS', x)
          words[x]=wk
      elif wk and isinstance(x,tuple) :
          x=tuple(map(nice_word,x))
          if all(x) :
            wk -= 1

            words[x]=wk

    # ordering sentences by id, not rank here
    sents.sort(key=lambda x: x[1])
    #for sss in sents : ppp(sss)
    summary=sents

    # remove word if in a tuple that is also selected
    for xs in words.copy() :
      if isinstance(xs,tuple) :
        for w in xs:
          if w in words:
            del words[w]
    clean_words=OrderedDict()
    for xs in words :
      if isinstance(xs,tuple) :
        clean_words[tuple(map(maybe_cap,xs))]=True
      else :
        clean_words[maybe_cap(xs)]=True

    if self.params.with_refiner:
      # mimics usual return types after refining with BERT
      summary=sorted(summary,reverse=True,key=lambda x : x[0])
      wss=[ws for (_,_,ws) in summary]
      wss=refine_wss(wss,self)
      xss = [(0,0,ws) for ws in wss]
      summary = xss

    return summary,list(clean_words)

  def to_svos(self):
    '''
    returns SVO relations as a dict associating to each
    SVO tuple the set of the sentences it comes from
    '''
    sent_data, l2occ = self.db
    d = defaultdict(set)
    for i, data in enumerate(sent_data):
      rels, svos = rel_from(data)
      comps = comps_from(i, data)  # or directly from deps
      ners = ners_from(data)
      for s, v, o in svos: #ok
        if s!=o and good_word(s) and good_word(o) :
           d[(s, v2rel(v), o)].add(i)
      for x, e in ners: #ok
        d[(e2rel(e), 'has_instance', x)].add(i)

      for a, b in comps: #ok
        c = (a, b)
        d[(a, 'as_in', c)].add(i)
        d[(b, 'as_in', c)].add(i)

    for svo in wn_from(l2occ):
      s,v,o=svo
      if s==o : continue
      s_occs=set()
      o_occs=set()
      for  id,_ in l2occ.get(s) :
        s_occs.add(id)
      for id, _ in l2occ.get(o):
        o_occs.add(id)
      shared_occs=s_occs.intersection(o_occs)
      if shared_occs :
        d[svo]=s_occs.intersection(o_occs)

    return d

  def to_word_orbit(self,lemma):
    '''
    extracts orbit of given lemma through sentence space
    as  (sentence,rank) pairs
    '''
    _, l2occ = self.db
    occs=l2occ.get(lemma)
    if not occs : return None
    sranks=[(id,self.pr[id]) for (id,_) in occs]
    return sranks

  def to_sent_orbit(self,id):
    '''
    extracts orbit of given sentence
    through lemma  space as (word,rank) pairs
    '''
    def pr_of(x) :
      r=self.pr.get(x)
      if r : return r
      return 0

    sent_data, _ = self.db
    ls=self.get_lemma(id)
    if not ls: return None
    ws=self.get_word(id)
    for i,l in enumerate(ls) :
      yield ws[i],pr_of(l)

  def to_svo_graph(self):
    ''' exposes svo relations as a graph'''
    if self.svo_graph: return self.svo_graph
    g=nx.DiGraph()
    for svo,occs in self.svos.items() :
      s,v,o=svo
      g.add_edge(s,o,rel=v,occs=occs)
    return g


  def to_dep_tree(self):
    '''
    extracts dependency graph (mostly a tree)
    by fusing dependency trees of all sentences
    '''
    g=nx.DiGraph()
    for f,r,t in self.dep_edge() :
      g.add_edge(f,t,rel=r)
      #print(f, r, t)
    return g

  def dep_edge(self):
    ''' dependency edge generator'''
    sent_data, l2occ = self.db
    for info in sent_data:
      ws,ls,ts,_,_,deps,_=info
      for dep in deps:
        #print(dep)
        f, r, t = dep
        if t== -1 : #  and r=='ROOT' :
          wt='SENT'
          tt = 'TOP'
        else :
          wt = ls[t]
          tt=ts[t]
        tf=ts[f]
        wf=ls[f]
        #r=r.replace(':','*')
        trt="_".join([tt,r,tf])
        yield wt, trt, wf

  # TODO: USE IT
  def raw_dep_edge(self,id):
      ''' dependency edge generator for sentence id'''
      sent_data, l2occ = self.db
      info = sent_data[id]
      ws,ls,ts,_,_,deps,_=info
      for dep in deps:
        #print(dep)
        f, r, t = dep
        if t== -1 : #  and r=='ROOT' :
          wt='SENT'
          tt = 'TOP'
        else :
          wt = ls[t]
          tt=ts[t]
        tf=ts[f]
        wf=ls[f]
        #r=r.replace(':','*')
        trt="_".join([tt,r,tf])
        yield wt, trt, wf

  def dep_tree(self,id) :
      g=nx.DiGraph()
      for f,r,t in self.raw_dep_edge(id) :
        if t != '.' : g.add_edge(f,t)
      if not 'SENT' in g :
        sent_data, l2occ = self.db
        tprint('BAD SENT:',sent_data[id])
        return None

      t0=next(iter(g['SENT']))
      seen=set()
      def walk(x) :
         if x in seen : return [x]
         seen.add(x)
         xs=[y for y in iter(g[x])]
         return ([x]+list(map(walk,xs)))
      return walk(t0)

  def dep_term(self,id,quote=False):
    tree=self.dep_tree(id)
    if not tree : return None
    term = tree2term(tree,quote=quote)
    return term


  def to_term_file(self,quote=False):
    fname=osp.basename(self.from_file)
    fname=fname.split('.')[0]
    file_name='temp/' + fname + ".pro"
    sent_data, _ = self.db

    with wopen(file_name) as outf:
      for id in range(len(sent_data)) :
         x=self.dep_term(id,quote=quote)
         if not x : continue
         term='term('+x+').'
         print(term,file=outf)

  def to_json_file(self):
    fname = osp.basename(self.from_file)
    fname = fname.split('.')[0]
    file_name = 'temp/' + fname + ".json"
    sent_data, _ = self.db
    trees=[]
    for id in range(len(sent_data)):
        x = self.dep_tree(id)
        if not x: continue
        trees.append(x)
    with wopen(file_name) as g:
      json.dump(trees, g, indent=1)



  def to_edges_in(self,id,sd):
    '''yields edges from dependency structure of sentence id'''
    for dep in dep_from(id, sd):
      if self.params.subject_centered:
        yield from sub_centered(id, dep,all_to_sent=self.params.all_to_sent)
      else:
        yield from pred_mediated(id, dep)
    if self.params.compounds:
      for ft in comps_from(id, sd):
        f, t = ft
        yield f, ft  # parts to compound
        yield t, ft
        yield f,t
        yield ft, id  # compound to sent


  def to_edges(self):
    '''yields all edges from syntactic dependency structure'''
    sent_data, l2occ = self.db
    for id, sd in enumerate(sent_data):
      yield from self.to_edges_in(id, sd)
    # nouns may also point to the first sent where they are "defined"
    if self.params.use_to_def:
      for lemma,occs in l2occ.items() :
        if occs and good_word(lemma):
          id,pos=occs[0]
          tag = sent_data[id][TAG][pos]
          if  good_tag(tag) : #,starts='N') :
            yield lemma,id
            # pumping senteces through word towards first
            # in which it occurs
            for i,occ in enumerate(occs) :
              if i>0:
                yield occ[0],lemma

  def to_graph(self, personalization=None):
    ''' builds document graph from several link types '''
    svos=self.svos
    g = nx.DiGraph()
    for e in self.to_edges():
      f, t = e
      g.add_edge(f, t)
    if self.params.svo_edges:
      for s, v, o in svos:
        if s == o: continue
        if v == 'as_in':
          g.add_edge(s, o)
        else:
          g.add_edge(o, s)

    if personalization == None and self.params.pers_idf :
      personalization=self.pers_from_freq(get_freqs())

    pr = nx.pagerank(g, personalization=personalization)
    if self.params.use_line_graph and g.number_of_edges()<20000 :
        lg=nx.line_graph(g)
        lpr= nx.pagerank(lg)
        for xy,r in lpr.items() :
          x,y=xy
          if isinstance(x,str) and isinstance(y,str):
            pr[x]=pr[x]+r
            pr[y]=pr[y]+r
    return g, pr

  def pers_from_freq(self,freqs):
    ''' returns personalization dictionary derived from word frequencies'''
    d=dict()
    _,l2occ=self.db
    for w,r in freqs.items() :
      if w in l2occ and r>0:
        p=(1+math.log(len(l2occ[w])))/math.log(1+r)
        d[w]=p
    return d

  def normalize_key(self,w,r):
    ''' heuristics for normalizing keyphrase ranks'''
    if not self.params.use_freqs : return r
    freqs=get_freqs()
    _, l2occ = self.db
    if not w in freqs or not w in l2occ : return r
    fr=freqs[w]
    approx_tf_idf=(1+math.log(len(l2occ[w]))) / math.log(1 + fr)
    p=(2*r*approx_tf_idf)/(r+approx_tf_idf)
    #p=math.sqrt(p)
    #p = r * approx_tf_idf
    return p


  def to_prolog(self):
    ''' generates a Prolog representation of a document's content'''
    if not self.from_file : return
    fname=self.from_file[:-4]
    with wopen(fname+".pro") as f :
      sent_data,l2occ=self.db
      f.write('% SENTENCES: \n')
      for i,data in enumerate(sent_data) :
        ws=list(data[SENT])
        f.write(f'sent({i},{ws}).\n')
      f.write('\n% LEMMAS: \n')
      for i, data in enumerate(sent_data):
        ws = list(data[LEMMA])
        f.write(f'lemma({i},{ws}).\n')
      f.write('\n% RELATIONS: \n')
      for svo,occs in self.svos.items() :
        s,v,o=svo
        occs=sorted(occs)
        f.write(f'svo{s,v,o,occs}.\n')

  def get_gist(self, q,answers):
    ''' extract short answer from BERT
        using query and a few dozen doctalk best answers
    '''
    if self.params.with_bert_qa ==0 : return
    from transformers import pipeline
    #ranks=[a[2] for a in answers]
    #assert ranks==sorted(ranks,reverse=True)
    txt = ""
    for a in answers:
      sentId = a[0]
      sent = a[1]
      before = self.db[0][sentId][BEFORE]
      ws = ""
      for j in range(len(sent)):
         ws += before[j] + sent[j]
      txt += ' ' + ws
    
    if txt == "":
      return ""
    print('*********get_gist, txt to ask_bert:', txt)
    r = ask_bert(txt, q)
    
    if not r :
      print('\n===========>NO ANSWER from BERT.\n')
      return ""


    removes = [",",".", "?", "!", ",\"", ".\"","?\"", "!\"", "'s"]

    for remove in removes:
      if r.endswith(remove):
        keepLen = len(r) - len(remove)
        r = r[:keepLen]
    print("===========>BERT SHORT ANSWER:",r+'<===========\n')
    
    return r


  def distill(self,q,answers,answerer):
    '''
    overridable answer distillation opertation
    '''
    return self.get_gist(q,answers)


  def say(self,what):
    ''' prints and ptionally says it, unless set to quiet'''
    print(what)
    if not self.params.quiet: subprocess.run(["say", what])


  def show_summary(self):
    ''' prints/says summary'''
    self.say('SUMMARY:')
    for r,x,ws in self.get_summary() :
      if not self.params.with_refiner :
        print(x,end=': ')
      self.say(niceWithSentId(x, self))
      print('')

  def show_keywords(self):
    ''' prints keywords'''
    print('KEYWORDS:')
    for w in self.get_keys():
      print(w)
    print('')


  def save_summary(self,out_file):
    '''
    saves summary as plain text for ROUGE evaluation
    '''
    with wopen(out_file) as g:
      for _, _, ws in self.get_summary():
        print(nice(ws),file=g)

  def save_keywords(self,out_file):
    '''
      saves keyphrases one per line for ROUGE evaluation
    '''
    with wopen(out_file) as g:
      for w in self.get_keys() :
        print(w,file=g)

  def show_rels(self):
    ''' prints extracted relations'''
    print('RELATIONS:')
    for svoi in self.svos.items():
       print(svoi)

  def show_svos(self):
    '''
    optionally shows highest ranked SVO relations as graph
    '''
    show = self.params.show_pics
    g = self.to_svo_graph()
    seeds = take(self.params.subgraph_size,
                 (x for x, r in self.by_rank if isinstance(x, str)))
    g = g.subgraph(seeds)
    self.show_svo_graph(g,file_name=self.from_file)

  def show_all(self):
    ''' prints out sevaral results'''
    if self.from_file :
      print('\n--------------  FILE:',self.from_file,'-----------\n')
    show = self.params.show_pics
    #self.show_summary()
    #self.show_keywords()
    #self.show_stats()
    if self.params.show_rels:
      self.show_rels()
    if self.params.to_prolog :
      self.to_prolog()
    if show and self.from_file:
      pshow(self, file_name=self.from_file)
      self.show_svos()

  def show_stats(self):
    ''' prints out some staistics'''
    print('SENTENCES:',len(self.db[0]))
    print('LEMMAS:', len(self.db[1]))
    print('GRAPH NODES:', self.g.number_of_nodes())
    print('GRAPH EDGES:',self.g.number_of_edges())
    print('SVO RELATIONS:', len(self.svos))
    print('')

  def show_svo_graph(self,g,file_name='temp.txt'):
    ''' depicts the subgraph of the highest ranked nodes in the SVO graph'''
    size = self.params.subgraph_size
    show = self.params.show_pics
    if size > 0:
      pr = nx.pagerank(g)
      best = set(take(size, [x[0] for x in rank_sort(pr)]))
      g = g.subgraph(best)
    fname = file_name[:-4] + "_svo.gv"
    gshow(g, file_name=fname, attr='rel', show=show)


# helpers

# creates dep. tree database files from directory
# to be used for QA, possibly via ML tools
def dir_to_term_files(dir,target='json',quote=False):
  if not target in ['json','pro'] :
    raise "bad target in: dir_to_term_files"
  fs=os.listdir(dir)
  for fname in fs:
    suf=fname.split('.')[1]

    if suf == 'txt' : # and '_quest.' not in fname:
      fname=dir+fname
      t=Talker(from_file=fname)
      print(target + ' file from:',t.from_file)
      if target=='json' :
        t.to_json_file()
      elif target=='pro':
        t.to_term_file(quote=quote)


def tree2term(term, quote=True):
    buf = []
    def walk(t):
      f=t[0]
      xs=t[1:]
      f = f.replace("'", '').lower()
      if quote or not f.isalpha():
        f = "'" + f + "'"
      buf.append(f)
      if xs:
        buf.append('(')
        for i, x in enumerate(xs):
          if i > 0: buf.append(',')
          walk(x)
        buf.append(')')
    walk(term)
    s = ''.join(buf)
    return s

def nice_keys(keywords):
    '''
      joins coumpound keyphrases, if needed
    '''
    for w in keywords:
      if isinstance(w,tuple) :
        yield " ".join(w)
      else :
        yield w

def is_clean_sent(ls,known_ratio) :
  '''
  heuristic on ensuring extracted sentences
  contain mostly known English words
  '''
  goods=[w for w in ls if w.isalpha() and w in wnet_words]
  return len(goods)>known_ratio*len(ls)

def niceWithSentId(sentId, self) :
  sent =self.db[0][sentId][SENT]
  before = self.db[0][sentId][BEFORE]
  ws = ""
  for j in range(len(sent)):
     ws += before[j] + sent[j]
  return ws

def nice(ws) :
  ''' aggregates word lists into a nicer looking sentence'''
  ws=[cleaned(w) for w in ws]
  sent=" ".join(ws)
  #print(sent)
  sent=sent.replace(" 's","'s")
  sent=sent.replace(" ,",",")
  sent=sent.replace(" .",".")
  sent = sent.replace('``', '"')
  sent = sent.replace("''", '"')
  return sent


def normalize_sent(r,sent_len,avg_len):
  '''
  normalizes the ranking of sentences
  based on effect of their length on ranking
  also reduces chances that noisy short sentences that might have
  passed through the NLP toolkit make it into summaries or answers
  '''
  if not r:
    r=0
  #@@@@ if sent_len >= 64 : return 0
  if sent_len > 2*avg_len or sent_len < min(5,avg_len/4) :
    return 0
  factor =  1/(1+abs(sent_len-avg_len)+sent_len)
  #ppp("NORM:",factor,r,sent_len,avg_len)
  return r*factor

def good_word(w) :
  '''
  ensures that most noise words are avoided
  '''
  return isinstance(w,str) and len(w)>2 and w.isalpha() \
         and w not in stop_words

def good_tag(tag,starts="NVJA"):
  ''' true for noun,verb, adjective and adverb tags'''
  c=tag[0]
  return c in starts

def distinct(g) :
  '''ensures repetititions are removed from a generator'''
  yield from OrderedDict.fromkeys(g)

def remdup(seq) :
  '''
    removes duplicates in sequence in O(N) time
  '''
  return list(OrderedDict.fromkeys(seq))

def take(k,g) :
  ''' generates only the first k elements of a sequence'''
  for i,x in enumerate(g) :
    if i>=k : break
    yield x

def pdf2txt(fname) :
  '''
    pdf to txt conversion with external tool - optional
    make sure you install "poppler tools" for this to work!
  '''
  subprocess.run(["pdftotext", fname+".pdf"])
  clean_text_file(fname+".txt")

def file2string(fname):
  with ropen(fname) as f:
    return f.read()

def string2file(text,fname) :
  with wopen(fname) as g:
    g.write(text)

def clean_text_file(fname) :
  print('cleaning: '+fname)
  from nltk.tokenize import sent_tokenize, word_tokenize
  data = file2string(fname)
  texts=sent_tokenize(data)
  clean=[]
  for text in texts :
    ws=word_tokenize(text)
    good=0
    bad=0
    if len(ws)>256 : continue
    for w in ws :
      if w.isalpha() and len(w)>1 :good+=1
      else : bad+=1
    if good/(1+bad+good) <0.75 : continue
    if ws[-1] not in ".?!" : ws.append(".")
    sent=" ".join(ws)
    clean.append(sent)
  new_data="\n".join(clean)
  string2file(new_data,fname)


def path2fname(path) :
  '''
    extracts file name from path
  '''
  return path.split('/')[-1]


def trimSuf(path) :
  '''
    trimms suffix of in path+file
  '''
  return ''.join(path.split('.')[:-1])

def justFname(path) :
  '''
     returns just the name of the file
     no directory path, no suffix
  '''
  return trimSuf(path2fname(path))


