from basesystem import BaseSystem
import sys
import networkx as nx


class Textstar(BaseSystem):
    def __init__(self, stanza_path, ranker=nx.pagerank, trim=80):
        """
        Args:
          stanza_path: Path to the StanzaGraphs folder for importing purpose
        """
        self.ranker = ranker
        self.trim = trim
        self.stanza_path = stanza_path
        sys.path.append(stanza_path)

        import textstar.textstar as textstar
        self.textstar = textstar
    
    def __str__(self):
        return "Textstar System at " + self.stanza_path

    def process_text(self, text, summarize=True, key_words=True, sum_len=5, kwds_len=5):
        sentids, kwds = self.textstar.process_text(
            text,
            self.ranker,
            sum_len,
            kwds_len,
            self.trim,
            False
        )

        sents = [s for _,s in sentids]

        return kwds, sents
