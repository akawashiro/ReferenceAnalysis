# -*- coding: utf-8 -*-
import sys
import argparse
import datetime
from util import db
from util import txt
from util import dt
from util import pb
from util import slr


LOCALHOST = 'http://localhost:8983/solr/nytimes_nitf/select'
KAREN = 'http://lab.dl.kuis.kyoto-u.ac.jp/~adam/solr/select'
BEGIN_DATE = datetime.date(1987, 1, 1)
END_DATE = datetime.date(2007, 6, 20)
MIN_ARTICLE_NUM = 10
INCLUDE_NEIGHBOR = 1
REFERENCE_TYPE = 'd'


if __name__ == '__main__':
    # Parse args
    ap = argparse.ArgumentParser(
        description='Collect news articles from Solr NITF.')

    ap.add_argument('db_file_name',
        help='SQLite3 DB file name')

    ap.add_argument('-u', '--solr-url', default=KAREN,
        help='Solr URL')

    ap.add_argument('-b', '--begin-date', type=dt.str2date, default=BEGIN_DATE,
        help='begin date (YYYY-MM-DD)')

    ap.add_argument('-e', '--end-date', type=dt.str2date, default=END_DATE,
        help='end date (YYYY-MM-DD)')

    ap.add_argument('-i', '--include-neighbor',
        type=int, default=INCLUDE_NEIGHBOR,
        help='# of neighbor sentences to include')

    ap.add_argument('-m', '--reference-type', default=REFERENCE_TYPE, choices='wpd',
        help='Type of reference (whole/part/divide)')

    args = ap.parse_args()
    print 'DB: {0}'.format(args.db_file_name)
    print 'Solr URL: {0}'.format(args.solr_url)
    print 'article begin date: {0}'.format(dt.date2str(args.begin_date))
    print 'article   end date:   {0}'.format(dt.date2str(args.end_date))
    print 'neighbor sentences: {0}'.format(args.include_neighbor)
    print 'reference type: {0}'.format(args.reference_type)
    print '-' * 40

    # Connect to DB and create table
    dh = db.DbHandler(args.db_file_name)
    dh.create_table_article()
    dh.create_table_reference()

    # Set Info
    print 'Setting info'
    dh.insert_info('begin_date', dt.date2str(args.begin_date))
    dh.insert_info('end_date', dt.date2str(args.end_date))
    dh.insert_info('include_neighbor', str(args.include_neighbor))
    dh.insert_info('reference_type', args.reference_type)
    print '-' * 40

    # Create Solr NITF handler
    sh = slr.SolrNitfHandler(args.solr_url, args.begin_date, args.end_date)

    # Show query and article num list    
    print '# query (article num)'
    cur, query_num = dh.select_count_all_query()
    q_id_query_num_lis = []
    for q_id, query in cur:
        num = sh.get_num(query)
        if num < MIN_ARTICLE_NUM:
            continue
        q_id_query_num_lis.append((q_id, query, num))
        print '[{0: 3d}]{1} ({2})'.format(q_id, query, num)

    # Ask whether use all query or select some of them or exit
    print '# Use them all?'
    print '# y: yes, c: choose manually, (other): no'
    answer = raw_input('> ')
    if answer == 'y':
        pass
    elif answer == 'c':
        print 'Input query ids.'
        q_ids = [int(s) for s in raw_input('> ').split()]
        q_id_query_num_lis = [
            (q_id, query, num)
            for q_id, query, num
            in q_id_query_num_lis
            if q_id in q_ids]
    else:
        sys.exit()
    print '-' * 40

    # Collect articles
    for q_id, query, num in q_id_query_num_lis:
        print 'Processing \"{0}\"'.format(query)
        docs = sh.get_all_docs(query)
        maxval = len(docs)
        pbar = pb.create_pbar(maxval).start()
        for d in docs:
            # Save article
            a_id = d['guid']
            date = d['publicationDate'].split('T')[0]
            if 'headline' in d:
                headline = d['headline']
            else:
                headline = ''
            if 'body' in d:
                body = d['body']
            else:
                body = ''
            dh.insert_article(a_id, date, headline, body)

            # Save reference
            if args.reference_type == 'w':
                sentences = body
                dh.insert_reference(a_id, q_id, sentences)
            elif args.reference_type == 'p':
                sentences = txt.find_sentences(query, body, args.include_neighbor)
                dh.insert_reference(a_id, q_id, sentences)
            elif args.reference_type == 'd':    # default
                sents_lis = txt.find_sentences_lis(query, body, args.include_neighbor)
                for ss in sents_lis:
                    dh.insert_reference(a_id, q_id, ss)     # article id, query id, 

            # Update progress bar
            pbar.update(pbar.currval + 1)
        pbar.finish()

    print 'Done'
