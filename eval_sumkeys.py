import glob
import sys
import os
import random
import datetime
import time
import networkx as nx

import rouge_stats as rs
import key_stats as ks

from systems.textstar import Textstar
from systems.stanzagraphs import StanzaGraphs
from systems.doctalk import DocTalk

from dataset.Krapivin2009 import Karpivin2009
from dataset.cnn_big import CnnBig
from dataset.nus import NUS
from dataset.arxiv import Arxiv
from dataset.pubmed import Pubmed
from dataset.kp20k import KP20K

# SETTINGS ------------------------------------------------

# number of keyphrases and summary sentences
# wk,sk=6,6
# wk,sk=10,9
wk, sk = 14, 6  # best
# wk, sk = 10, 8

# max number of documents to process (None to process all)
max_docs = 100
docs_to_skip = 0

# delete previously generated keys+abs
delete_old = True

# Stop running on errors
show_errors = False

# Prevent printing from summarization code
quiet = True

# Save generated summaries and kwds
save_out = True

# choice of NLP summarizer and key-word extractor
# SYSTEM = StanzaGraphs(
#   stanza_path="/Users/brockfamily/Documents/UNT/StanzaGraphs/"
# )
# SYSTEM = Textstar(
#     stanza_path="/Users/brockfamily/Documents/UNT/StanzaGraphs/",
#     ranker=nx.degree_centrality,
#     trim=70
# )
SYSTEM = DocTalk(
  doctalk_path="/Users/brockfamily/Documents/UNT/DocTalk/"
)

# choice of dataset
# DATASET = Karpivin2009(
#   count=max_docs,
#   include_abs=False,
#   direct=False
# )
# DATASET = CnnBig(
#   count=max_docs
# )
# DATASET = NUS(
#   count=max_docs,
#   include_abs=False
# )
# DATASET = Arxiv(
#     count=max_docs,
#     dataset="test"
# )
# DATASET = Pubmed(
#   count=max_docs,
#   dataset="test"
# )
DATASET = KP20K(
  count=max_docs,
  dataset="test"
)

# SETTINGS ------------------------------------------------


out_dir = DATASET.path + "out/"
out_abs_dir = out_dir + "abs/"
out_keys_dir = out_dir + "keys/"
# temp_dir = DATASET.path + 'temp_docs/'


def avg(xs):
    s = sum(xs)
    l = len(xs)
    if 0 == l:
        return None
    return s/l

# clean output directories


def clean_all():
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(out_abs_dir, exist_ok=True)
    os.makedirs(out_keys_dir, exist_ok=True)
    # os.makedirs(temp_dir,exist_ok=True)
    if not delete_old:
        return
    if sys.platform != 'win32':
        # linux
        clean_path(out_abs_dir)
        clean_path(out_keys_dir)
        # if force>1 : clean_path(temp_dir)
    else:
        # windows
        clean_path(out_abs_dir + '/docsutf8/')
        clean_path(out_keys_dir + '/docsutf8/')
        # if force>1 : clean_path(temp_dir + '/docsutf8/')

# clean files at given directory path


def clean_path(path):
    if not delete_old:
        return
    os.makedirs(path, exist_ok=True)

    files = glob.glob(path+"/*")
    for f in files:
        os.remove(f)

# turns a string into given file


def string2file(fname, text):
    with open(fname, 'w', encoding='utf8') as f:
        f.write(text)


def printProgress(progress, width=100, end="", same_line=True):
    count = round(progress * width)
    line_end = '\r' if same_line else '\n'
    print("|" + "="*count + " "*(width-count) +
          "| %.1f%%" % (progress * 100), end, end=line_end)


class Quiet():
    """Prevent printing. Usage:
    with Quiet():
      run_and_print_a_lot(args) #Nothing will print
    """

    def __enter__(self):
        self.devnull = open(os.devnull, "w")
        self.original = sys.stdout
        sys.stdout = self.devnull

    def __exit__(self, type, value, traceback):
        sys.stdout = self.original
        self.devnull.close()


def evaluate(system, dataset, stop_on_error=True, save_out=True):
    def showParams():
        print("TIME :", datetime.datetime.now())
        print("SYSTEM :", system)
        print("DATASET :", dataset)
        print(
            'wk', wk, 'sk', sk, '\n'
            'docs = ', dataset.count, '\n'
            'delete_old = ', delete_old, '\n'
            'save_out = ', save_out, '\n'
        )

    print()
    showParams()
    # input("Press enter to start: ")

    random.seed(42)

    clean_all()

    keys_scores = ([], [], [])
    keys_rouge1 = ([], [], [])
    abs_scores = ([], [], [])
    abs_rouge1 = ([], [], [])
    abs_rouge2 = ([], [], [])
    abs_rougel = ([], [], [])
    abs_rougew = ([], [], [])
    bad_files = 0
    good_files = 0

    startTime = time.time()

    for i, document in enumerate(dataset):
        if i < docs_to_skip:
            continue
        try:
            # Try to summarize the document
            if quiet:
                with Quiet():
                    keys, exabs = system.process_text(
                        document,
                        summarize=True,
                        key_words=True,
                        sum_len=sk,
                        kwds_len=wk
                    )

            else:
                keys, exabs = system.process_text(
                    document,
                    summarize=True,
                    key_words=True,
                    sum_len=sk,
                    kwds_len=wk
                )

            key_words_str = "\n".join(keys).replace('-', ' ')
            summary_str = "\n".join(exabs).replace('-', ' ')

            if save_out:
                # Write key words and summaries to files
                doc_file = document.name + '.txt'
                kf = out_keys_dir + doc_file
                af = out_abs_dir + doc_file
                string2file(kf, key_words_str)
                string2file(af, summary_str)

            # Evaluate on different metrics
            if dataset.has_kwds:
                gold_kwds = document.key_words()

                # Keys Scores
                d = ks.kstat(key_words_str, gold_kwds)
                assert d
                keys_scores[0].append(d['p'])
                keys_scores[1].append(d['r'])
                keys_scores[2].append(d['f'])

                # Keys Rouge 1
                scores_iter = rs.rstat(key_words_str, gold_kwds)
                d = next(scores_iter)[0]
                keys_rouge1[0].append(d['p'][0])
                keys_rouge1[1].append(d['r'][0])
                keys_rouge1[2].append(d['f'][0])

            if dataset.has_sums:
                gold_summary = document.summary()

                # Abs Scores
                d = ks.kstat(summary_str, gold_summary)
                assert d
                abs_scores[0].append(d['p'])
                abs_scores[1].append(d['r'])
                abs_scores[2].append(d['f'])

                scores_iter = rs.rstat(summary_str, gold_summary)
                # Abs Rouge 1
                d = next(scores_iter)[0]
                abs_rouge1[0].append(d['p'][0])
                abs_rouge1[1].append(d['r'][0])
                abs_rouge1[2].append(d['f'][0])

                # Abs Rouge 2
                d = next(scores_iter)[0]
                abs_rouge2[0].append(d['p'][0])
                abs_rouge2[1].append(d['r'][0])
                abs_rouge2[2].append(d['f'][0])

                # Abs Rouge L
                d = next(scores_iter)[0]
                abs_rougel[0].append(d['p'][0])
                abs_rougel[1].append(d['r'][0])
                abs_rougel[2].append(d['f'][0])

                # Abs Rouge W
                d = next(scores_iter)[0]
                abs_rougew[0].append(d['p'][0])
                abs_rougew[1].append(d['r'][0])
                abs_rougew[2].append(d['f'][0])

            good_files += 1
            printProgress((i + 1) / dataset.count, end="(%i files)" % (i + 1), same_line=quiet)

        except KeyboardInterrupt as e:
            print("Keyboard Interrupt, stopping...")
            break

        except Exception as e:
            print('*** FAILING on:', document, 'ERROR:', sys.exc_info()[0])
            bad_files += 1
            if stop_on_error:
                raise
            else:
                continue

    endTime = time.time()

    print("\n\n")
    showParams()
    print("Failed on %i files, succeeded on %i files" %
          (bad_files, good_files))
    print("Run time: %.1fS (%.2fS per file)\n" %
          (endTime - startTime, (endTime - startTime) / good_files))

    print("                  Precision,          Recall,             F-Measure")

    if dataset.has_kwds:
        print("KEYS SCORES : %.16f  %.16f  %.16f" %
              (avg(keys_scores[0]), avg(keys_scores[1]), avg(keys_scores[2])))
        print("KEYS ROUGE 1: %.16f  %.16f  %.16f" %
              (avg(keys_rouge1[0]), avg(keys_rouge1[1]), avg(keys_rouge1[2])))

    else:
        print("KEYS SCORES : --                  --                  --")
        print("KEYS SCORES : --                  --                  --")

    if dataset.has_sums:
        print("ABS SCORES  : %.16f  %.16f  %.16f" %
            (avg(abs_scores[0]), avg(abs_scores[1]), avg(abs_scores[2])))
        print("ABS ROUGE 1 : %.16f  %.16f  %.16f" %
            (avg(abs_rouge1[0]), avg(abs_rouge1[1]), avg(abs_rouge1[2])))
        print("ABS ROUGE 2 : %.16f  %.16f  %.16f" %
            (avg(abs_rouge2[0]), avg(abs_rouge2[1]), avg(abs_rouge2[2])))
        print("ABS ROUGE l : %.16f  %.16f  %.16f" %
            (avg(abs_rougel[0]), avg(abs_rougel[1]), avg(abs_rougel[2])))
        print("ABS ROUGE w : %.16f  %.16f  %.16f" %
            (avg(abs_rougew[0]), avg(abs_rougew[1]), avg(abs_rougew[2])))
    
    else:
        print("ABS SCORES  : --                  --                  --")
        print("ABS ROUGE 1 : --                  --                  --")
        print("ABS ROUGE 2 : --                  --                  --")
        print("ABS ROUGE l : --                  --                  --")
        print("ABS ROUGE w : --                  --                  --")


if __name__ == '__main__':
    evaluate(
        SYSTEM, DATASET,
        stop_on_error=show_errors,
        save_out=save_out
    )
