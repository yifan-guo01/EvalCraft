from basesystem import BaseSystem
import sys
import networkx as nx

class Textstar(BaseSystem):
    def __init__(self, stanza_path):
        """
        Args:
          stanza_path: Path to the StanzaGraphs folder for importing purpose
        """
        sys.path.append(stanza_path)
    
    def process_text(self, text, summarize=True, key_words=True, sum_len=5, kwds_len=5):
        from textstar.textstar import process_text
        
        sentids, kws = process_text(
            text=text,
            ranker=nx.pagerank,
            kwsize=kwds_len,
            sumsize=sum_len)

        sents = [s for _,s in sentids]

        return kws, sents