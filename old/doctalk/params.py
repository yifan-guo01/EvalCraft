from inspect import getframeinfo, stack
import json

annotators=['tokenize','ssplit','pos','lemma','depparse','ner']+\
           ['natlog','openie']
trace=0

class talk_params:
  def __init__(self,from_dict=None,from_json=None):
    self.stanza_parsing = False  # if True, use stanza_nlp.py; if False, use nlp.py
    self.force = False # if True, forces erasure of pre-parsed .json files
    #self.chunk_size=2^15 # splits large dcouments into chunks to avoid parser overflows TODO

    # content extraction related
    self.compounds = True # aggregates compounds
    self.svo_edges = True # includes SVO edges in text graph
    self.subject_centered = True # redirects link from verb with predicate function to ists subject
    self.all_to_sent = False # forces adding links form all lemmas to sentence id
    self.use_to_def = True # forces adding links from sentences to where their important words occur first

    self.pers_idf = False #  both reduce rouge scores
    self.use_freqs = False # same
    self.prioritize_compounds = 16 # elevates rank of coumpound to favor them as keyphrases
    self.use_line_graph = False # spreads using line_graph

    # 0 : no refiner, just doctalk, but with_bert_qa might control short snippets
    # 1 : abstractive BERT summarizer, with sumbert postprocessing
    # 2 : extractive BERT summarizer postprocessing
    # 3 : all of the above, concatenated
    
    self.with_refiner = 0 # <==================
    # controls short answer snippets via bert_qa pipeline
    self.with_bert_qa = 0.1 # <================== should be higher - low just to debug

    self.thirdparty_model = '' # <== summarization model
                             # '' return pytalk summary by rank
                             #   'facebook/bart-large-cnn',  send summary to facebook bart-large-cnn, get final answer from bart-large-cnn
                             #   't5-large', send summary to google t5-large, get final answer from google t5-large
    self.with_answerer=False # <== if False, it runs without calling corenlp parser for answerer
    # summary, and keyphrase set sizes

    self.top_sum = 40 # default number of sentences in summary, set default 40 if thirdparty_model is used, default 5 if thirdparty_model= ''
    self.top_keys = 10 # # default number of keyphrases, set default 40 if thirdparty_model is used, default 8 if thirdparty_model= ''

    # maximum values generated when passing sentences to BERT
    self.max_sum = self.top_sum*(self.top_sum-1)/2
    self.max_keys = 1+2*self.top_keys # not used yet

    self.known_ratio=0.8 # ratio of known to unknown words in acceptable sentences

    # query answering related
    self.top_answers = 4 # max number of answers directly shown
    # maximum answer sentences generated when passing them to BERT
    self.max_answers = max(16,self.top_answers*(self.top_answers-1)/2)

    self.cloud_size = 24 # word-cloud size
    self.subgraph_size = 42 # subgraph nodes number upper limit

    self.quiet = True # stops voice synthesis
    self.answers_by_rank = False # returns answers by importance vs. natural order

    self.pers = True # enable personalization of PageRank for QA
    self.expand_query = 2 # depth of query expansion for QA
    self.guess_wh_word_NERs=0 # try to treat wh-word qurieses as special

    self.think_depth=1 # depth of graph reach in thinker.py

    # visualization / verbosity control

    self.show_pics = 0  # 1 : just generate files, 2: interactive
    self.show_rels = 0  # display relations inferreed from text
    self.to_prolog = 1 # generates Prolog facts

    if from_json:
      jd = json.loads(from_json)
      self.digest_dict(jd)

    if from_dict :
      self.digest_dict(from_dict)

  def digest_dict(self, pydict):
    d = self.__dict__.copy()
    for k, v in d.items():
      if isinstance(k, str) and k in pydict:
        self.__dict__[k] = pydict[k]

  def __repr__(self):
    return str(self.__dict__)

  def show(self):
    for x,y in self.__dict__.items():
      print(x,'=',y)

def ropen(f) :
  return open(f,'r',encoding='utf8')

def wopen(g) :
  return open(g,'w',encoding='utf8')

def ppp(*args) :
  if trace<0 : return
  caller = getframeinfo(stack()[1][0])

  print('DEBUG:',
        caller.filename.split('/')[-1],
        '->',caller.lineno,end=': ')
  print(*args)
