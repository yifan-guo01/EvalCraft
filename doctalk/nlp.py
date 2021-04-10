# stanfordnlp client
import json
from .params import *
import stanza
stanza.install_corenlp()
def ies_of(sentence):
  if not NLPclient: return
  ts=[]
  for triple in sentence['openie']:
    s1,s2 = triple['subjectSpan']
    v1,v2 = triple['relationSpan']
    o1,o2 = triple['objectSpan']
    #t=( (s1-1,s2-1),(v1-1,v2-1),(o1-1,o2-1))
    t = ((s1, s2), (v1, v2), (o1, o2))
    ts.append( t )
  yield ts

def deps_of(sentence):
  deps = []
  # print('SENT',[x for x in sentence['entitymentions']])
  for x in sentence['enhancedPlusPlusDependencies']:
    r = x['dep']
    t = x['governor']
    f = x['dependent']
    deps.append((f - 1, r, t - 1))
  return deps


def lexs_of(sentence):
  toks = sentence['tokens']
  for tok in toks:
    # print('TOKENS',[x for x in tok])
    w = cleaned(tok['word'])
    # print('TOK',tok['index'],w)
    l = cleaned(tok['lemma'])
    t = tok['pos']
    n = tok['ner']
    l=l.lower()
    yield (w, l, t, n)

def to_json(infile,outfile):
  client = NLPclient()
  with ropen(infile) as f : text=f.read()
  with wopen(outfile) as g:
    xs=[x for x in client.extract(text)]
    json.dump(xs,g,indent=2)

def clean_text(text) :
  #text=clean_ascii(text)
  text=text.replace('..',' ')
  return text

def cleaned(w) :
  if w in ['-LRB-','-lrb-'] : return '('
  if w in ['-RRB-','-rrb-'] : return ')'
  if w in ['-LSB-', '-lsb-']: return '['
  if w in ['-RSB-', '-rsb-']: return ']'
  return w

class NLPclient:
  def __init__(self, core_nlp_version = '2018-10-05'):
    from stanza.server import CoreNLPClient
    self.client = CoreNLPClient(annotators=['tokenize','ssplit','pos',
    'lemma','ner','parse','coref'])

  def __enter__(self): return self
  def __exit__(self, exc_type, exc_val, exc_tb): pass
  def __del__(self): self.client.stop()

  def step(self,text) :
      core_nlp_output = self.client.annotate(text=text,
                      annotators=annotators, output_format='json')
      for sentence in core_nlp_output['sentences']:
        lexs=tuple(lexs_of(sentence))
        deps=deps_of(sentence)
        ies=tuple(ies_of(sentence))
        yield lexs,deps,ies

  def extract(self, text):
    tail=clean_text(text)
    while tail:
      chunk=2**13
      head=tail[0:chunk]
      tail=tail[chunk:]
      #print('EXTRACTING FROM',len(head), 'chars.')
      yield from self.step(head)
    #print('DONE EXTRACTING.')

def show_extract(infile):
  client = NLPclient()
  with ropen(infile) as f : text=f.read()
  for x in client.extract(text) :
    print(x)
