from .params import talk_params
from .talk import Talker,run_with
from .think import Thinker,reason_with

def new_params(from_json=None) :
  ''' get an editable 'talk_params' instance.
      Use  its `show' method to list them.
      You can change these parameter before using
      them to make a new Talker or Thinker
  '''
  return talk_params(from_json=from_json)

def new_talker(**kwargs) :
  '''first 3 parameters indicate the source document's format
     the last allows custom configuration of algorithms
     via a dozen parameters defaulting to params.talk_params()
               from_json=None,
               from_file=None,
               from_text=None,
               params=talk_params()
  '''
  return Talker(**kwargs)

def new_thinker(**kwargs) :
  '''
  parmeters the same as Talker - the superclass
  '''
  return Thinker(**kwargs)

def summary_sentences(talker) :
  '''
  returns summary as a list of sentences,
  each a list of words
  '''
  return talker.summary_sentences()

def keyphrases(talker) :
  '''
  returns a list of keyphrases
  '''
  return talker.keyphrases()

def answer_question(talker,quest) :
  '''
  given the json string quest as input containing a question
  in English, ended with '?', to be parsed with json.loads,
  it returns a list of answers about he document,
  as a json string that can be parsed with with json.loads
  to a list of lists of words
  '''
  return talker.answer_question(quest)
