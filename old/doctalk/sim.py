from .down import ensure_nlk_downloads
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
'''
wordnet interface - mostly similarity relations
'''

stop_words=set(stopwords.words('english')).union(set('|(){}[]%'))

#print(stop_words)
# basic wordnet relations
  
def wn_hyper(k,w,t) : return wn_rel(hypers, 2, k, w, t)

def wn_hypo(k,w,t) : return wn_rel(hypos, 2, k, w, t)

def wn_mero(k,w,t) : return wn_rel(meros, 2, k, w, t)

def wn_holo(k,w,t) : return wn_rel(holos, 2, k, w, t)

def wn_syn(k,w,t) : return wn_rel(id, 2, k, w, t)

def wn_all(n,k,w,t) :
  res=wn_rel(id, n, k, w, t) # synonyms
  for r in (hypers,hypos,meros,holos) :
    res.update(wn_rel(r,n,k,w,t))
  return res

def wn_svo(n,k,w,t) :
  ''' wraps relations as S,V,O triplets'''
  for friend in wn_rel(id,n,k,w,t) :
    if w<friend: yield (w,'is_like',friend)
  for friend in wn_rel(hypers,n,k,w,t) :
    if w!=friend : yield (w,'kind_of',friend)
  for friend in wn_rel(meros, n, k, w, t):
    if w!=friend : yield (w, 'part_of', friend)


def id(w) : return [w]

def hypos(s) : return s.hyponyms()

def hypers(s) : return s.hypernyms()

def meros(s) : return s.part_meronyms()

def holos(s) : return s.part_holonyms()

#  ADJ,ADJ_SAT, ADV, NOUN, VERB = 'a','s', 'r', 'n', 'v'

def wn_tag(T) :
  c=T[0].lower()
  if c in 'nvr' : return c
  elif c == 'j' : return 'a'
  else : return None

def wn_rel(f,n,k,w,t) :
  '''
  word-to-word relations, by limited
  expansion of synset-to-synset relation f
  '''
  related = set()
  if w in stop_words : return related
  for i,syns in enumerate(wn.synsets(w,pos=t)):
    if i>=n : break
    for j,syn in enumerate(f(syns)) :
      if j>=n : break
      #print('!!!!!',syn)
      for l in syn.lemmas():
        #print('  ',l)
        s=l.name()
        if s in stop_words : continue
        if w == s : continue
        #s=s.replace('_', ' ')
        related.add(s)
        if len(related) >=k : return related
  return related

def simtest() :
  w,tag='bank','n'
  print(wn_rel(id,2,300,w,tag))
  print(wn_rel(hypers, 2, 300, w, tag))
  print(wn_rel(hypos, 2, 300, w, tag))
  print(wn_rel(meros, 2, 300, w, tag))
  print(wn_rel(holos, 2, 300, w, tag))
  print('')
  print(wn_all(2,3,w,tag))
      
######
