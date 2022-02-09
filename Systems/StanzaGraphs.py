from pydoc import doc
import sys
from base_classes import NLPSystem
import os

class StanzaGraphs(NLPSystem):
    def __init__(self, stanza_path):
        """
        Args:
          stanza_path: Path to the StanzaGraphs folder for importing purpose
        """
        self.stanza_path = stanza_path
        sys.path.append(stanza_path)
    
    def __str__(self):
        return "StanzaGraphs System at " + self.stanza_path
    
    def process_text(self, document, summarize=True, key_words=True, sum_len=5, kwds_len=5):
        this_dir = os.getcwd()
        os.chdir(self.stanza_path)

        from summarizer import Summarizer
        
        nlp = Summarizer() #new
        nlp.from_text(document.as_text())
        kws, _, sents, _ = nlp.info(kwds_len, sum_len)
        
        os.chdir(this_dir)

        return kws, sents