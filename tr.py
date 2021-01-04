import spacy
import pytextrank
#RUN FIRST: python -m spacy download en_core_web_sm

# example text
text = "Compatibility of systems of linear" \
       " constraints over the set of natural numbers. " \
       "Criteria of compatibility of a system of linear " \
       "Diophantine equations, strict inequations, " \
       "and nonstrict inequations are considered. " \
       "Upper bounds for components of a minimal set of " \
       "solutions and algorithms of construction of " \
       "minimal generating sets of solutions " \
       "for all types of systems are given. " \
       "These criteria and the corresponding algorithms " \
       "for constructing a minimal supporting set of " \
       "solutions can be used in solving all the considered " \
       "types systems and systems of mixed types."



# load a spaCy model, depending on language, scale, etc.
nlp = spacy.load("en_core_web_sm")

# add PyTextRank to the spaCy pipeline
tr = pytextrank.TextRank()
nlp.add_pipe(tr.PipelineComponent, name="textrank", last=True)


def keys_and_abs(text,wk,sk) :
  doc = nlp(text)
  return keys(doc,wk),summary(doc,sk)

def keys(doc,wk=6) :

  # examine the top-ranked phrases in the document
  for i,p in enumerate(doc._.phrases):
    #print("{:.4f} {:5d}  {}".format(p.rank, p.count, p.text))
    #print(p.chunks)
    #yield p.text
    #if i>= wk : break
    return doc._.phrases[:wk]

def summary(doc,sk=6) :
  return [sent for
          sent in doc._.textrank.summary(limit_phrases=15, limit_sentences=sk)]


if __name__ == '__main__' :
  ks,xs = keys_and_abs(text,3,3)
  for k in ks : print(k)
  print('')
  for x in xs : print(x)

