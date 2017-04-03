# -*- coding: utf-8 -*-
import argparse
from nltk import tokenize
from util import db
from util import cnlp
import traceback
# from util import pb
import kawata_corenlp
import heidel_wrapper

if __name__ == '__main__':
    # Parse args
    ap = argparse.ArgumentParser(
        description='Extract words from references.')

    ap.add_argument('db_file_name',
                    help='SQLite3 DB file name')

    ap.add_argument('--no_heidel', action='store_true', default=False,
                    help='Use when it takes too much time')

    args = ap.parse_args()
    print 'DB: {0}'.format(args.db_file_name)
    print '-' * 40

    # Connect to DB file
    dh = db.DbHandler(args.db_file_name)
    dh.create_table_word()

    # Connect to Stanford NER Server
    ch = cnlp.CoreNlpHandler()
    kch = kawata_corenlp.kawata_corenlp_handler()

    # Extract and Save word_lis from reference
    print 'Extracting words'
    cur, maxval = dh.select_count_all_reference()
    # pbar = pb.create_pbar(maxval).start()
    for r_id, a_id, q_id, sentences in cur:
        date = dh.get_ref_date(r_id)
        sent_lis = tokenize.sent_tokenize(sentences)
        word_lis = []
        for s in sent_lis:
            try:
                words = kch.get_words(s, date)
            except:
                traceback.print_exc()
                words = []
            print s, " was processed"
            word_lis += [(r_id, w[0], w[1], w[2]) for w in words]
            if not args.no_heidel:
                times = heidel_wrapper.doc_to_timex3(s, date)
                word_lis += [(r_id, w[0], w[1], w[2]) for w in times]
               # 'tag TEXT, '
               # 'name TEXT, '
               # 'n_name TEXT)')
               # What is n_name?
               # When HEIDEL_TIME tag (HEIDEL_TIME,normalized time,expression)
        dh.insert_word_many(word_lis)
        # pbar.update(pbar.currval + 1)
    # pbar.finish()

    print 'Done'
