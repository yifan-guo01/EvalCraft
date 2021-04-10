import stanza
import csv
import networkx as nx
from collections import defaultdict

class stanzaNLPClient :
  def __init__(self,lang='en'):
      stanza.download(lang)
      self.nlp = stanza.Pipeline(lang)
      self.lang = lang
  
  def from_text(self,text="Hello!"):
    self.doc = self.nlp(text)
    self.text = text

  
  def keynouns(self):
    '''collects important nouns'''
    ns=set()
    for sent in self.doc.sentences:
      for x in sent.words:
        if self.keynoun(x) :
          ns.add(x.lemma)
    return ns

  def keynoun(self,x):
    '''true for "important" nouns'''
    ok = x.upos in ('NOUN','PROPN') and \
        ('subj' in x.deprel or 'ob' in x.deprel)
    if self.lang=='en' : ok=ok and len(x.lemma)>3
    return ok

  def get_svos(self, sid, sent ):
    '''generates <from,link,to,sentence_id> tuples'''
    first_occ=dict()
    def fact(x,sent,sid) :
      if x.head==0 :
        yield x.lemma, 'PREDICATE_OF', sid
      else :
        hw=sent.words[x.head-1]
        if self.keynoun(x) : # reverse link to prioritize key nouns
          yield hw.lemma, "rev_"+x.deprel, x.lemma
          yield (sid, 'ABOUT', x.lemma)
          if not x.lemma in first_occ :
            first_occ[(x.lemma,x.upos)]=sid
            yield (x.lemma, 'DEFINED_IN', sid)
        else:
          yield x.lemma,  x.deprel, hw.lemma
        if  x.deprel in ("compound","flat") :
          comp = x.lemma+" "+hw.lemma
          yield x.lemma,  'as_in', comp
          yield hw.lemma,   'as_in',  comp
          yield (sid,   'ABOUT',  comp)
  
    for x in sent.words :
      yield from fact(x,sent,sid)
  


  def map2db(self) :
    ''' process text with the NLP toolkit'''
    l2occ = defaultdict(list)
    sent_data=[]
    
    for i,sentence in enumerate(self.doc.sentences) :
      '''
      print('\nsentence:\n', sentence)
      print('\nsentence.tokens:\n', sentence.tokens)
      print('\nsentence.words:\n', sentence.words)
      '''
      sent,lemma,tag,ner,deps=[],[],[],[],[]
      svos = self.get_svos(i, sentence)
      for token in sentence.tokens :
        ner.append(token.ner)
      for j, word in enumerate(sentence.words) :
        l2occ[word.lemma].append((i,j))
        sent.append(word.text)
        lemma.append(word.lemma)
        tag.append(word.upos)
        '''
        if word.xpos:
          tag.append(word.xpos)
        else :
          tag.append(word.upos)
        '''
        if word.deprel == 'root':
          deps.append((word.id-1, 'ROOT', word.head-1))
        elif word.deprel == 'flat':
          deps.append((word.head-1, 'compound', word.id-1))          
        elif word.deprel == 'conj' and sentence.words[word.head-1].deprel == 'nsubj':
          deps.append((word.id-1, word.deprel, word.head-1))
          deps.append((word.id-1, 'nsubj', sentence.words[word.head-1].head-1))
        else:
          deps.append((word.id-1, word.deprel, word.head-1))

      d=(tuple(sent),tuple(lemma),tuple(tag),tuple(ner),tuple(deps),tuple(svos))
      sent_data.append(d)
  
    
    return sent_data, l2occ
  

#ttest('examples/test.txt', lang='en')
#ttest('texts/chinese.txt', lang='zh')
#ttest('texts/spanish.txt',lang='es')
#ttest('texts/russian.txt',lang='ru')
'''
def extract_from_stanza(fname='texts/english_short') :
  text = file2text(fname)
  if len(text) > 200: 
    short = text[ :200]
  else:
     short = text
  lang = langid.classify(short)
  print('lang:', lang[0])
  stname=stanzaNLPClient(lang[0]) # initializes the NLP class with a certain language
  stname.from_text(text) #runs stanza nlp on the file and stores the result in self.doc
  return stname.map2db()
'''

if __name__=="__main__" :
  extract_from_stanza(text="Hello!")
  #qatest(file = 'texts/english', question = 'texts/english_quest',lang='en')
  #test(fname='texts/english_short',lang='en')
  #test(fname='texts/const',lang='en')
  #test(fname='texts/spanish',lang='es')
  #test(fname='texts/chinese',lang='zh')
  #test(fname='texts/russian',lang='ru')

