from basesystem import BaseSystem
import sys

class StanzaGraphs(BaseSystem):
    def __init__(self, stanza_path):
        """
        Args:
          stanza_path: Path to the StanzaGraphs folder for importing purpose
        """
        sys.path.append(stanza_path)
    
    def process_text(self, text, summarize=True, key_words=True, sum_len=5, kwds_len=5):
        from StanzaGraphs.summarizer import Summarizer
        
        nlp = Summarizer() #new
        nlp.from_text(text)
        kws, _, sents, _ = nlp.info(kwds_len, sum_len)

        return kws, sents