extractor = None

BERT_ABS=1
BERT_EX=2
ALL=3

def refine(doctalk_summary,how) :
  global extractor
  if how in {BERT_EX,ALL} :
    from summarizer import Summarizer
    if not extractor : extractor=Summarizer()
    extractive_bert=extractor(doctalk_summary)
    if how==BERT_EX :
      return extractive_bert
  if how in {BERT_ABS,ALL} :
    from sumbert import summarize
    abstractive_bert=summarize(doctalk_summary)
    if how == BERT_ABS:
      return abstractive_bert
  if how == ALL:
    e="BERT:EXTRACTIVE: "+extractive_bert
    a="BERT:ABSTRACTIVE: "+abstractive_bert+"."
    return "\n".join([e,a,"\n"])


nlp=None
def ask_bert(txt,q,confid=0) :
  global nlp
  import os
  import sys
  out = sys.stdout
  err =  sys.stderr
  null = open(os.devnull,'w')
  sys.stdout = null
  sys.stderr = null
  try :
    r=try_to_ask_bert(txt,q,confid)
  except:
    r=None
  sys.stdout = out
  sys.stderr = err
  null.close()
  return r

def try_to_ask_bert(txt,q,confid) :
  global nlp
  if not nlp :
    from transformers import pipeline
    '''
    from transformers import AutoTokenizer, AutoModelForQuestionAnswering
	model_name = "bert-large-uncased-whole-word-masking-finetuned-squad"
    nlp = pipeline("question-answering", model=model_name,  tokenizer=model_name)
    '''
    # for local disk
    ''' 
    path = "/root/squadModel"
    model = AutoModelForQuestionAnswering.from_pretrained(path)
    tokenizer = AutoTokenizer.from_pretrained(path)
    nlp = pipeline('question-answering', model=model, tokenizer=tokenizer)
    '''
    nlp = pipeline("question-answering")
  r = nlp(question=q, context=txt)
  if r==None : return r
  return r['answer']
  '''
  if confid == 0:
    return r['answer']+', with confidence ='+str(round(r['score'],3))
  elif r['score'] > confid :  
    return r['answer']
  else:
    return None
  '''
