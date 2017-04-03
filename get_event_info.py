#-*- encoding: utf-8 -*-
import argparse
from util import dt
from util import txt
from util import db
from util import wk
import wikidate
import os.path


if __name__ == '__main__':
    # Parse args
    ap = argparse.ArgumentParser(
        description='Get event info.')

    ap.add_argument('db_file_name',
                    help='SQLite3 DB file name')

    ap.add_argument('event_name',
                    help='event name')

    args = ap.parse_args()
    print 'DB: {0}'.format(args.db_file_name)
    print 'event name: {0}'.format(args.event_name)
    event_begin_date = dt.date2str(wikidate.get_begin_date(args.event_name))
    end_date = '2007-06-20'
    print '-' * 40

    # Get black list of word
    black_list = []
    if os.path.exists("./black_words_list/" + args.event_name.replace(" ", "")):
        f = open("./black_words_list/" + args.event_name.replace(" ", ""), 'r')
        for r in f:
            black_list.append(r.replace("\n", ""))
    print "black list is ", black_list

    # Connect to DB and create table
    dh = db.DbHandler(args.db_file_name)

    # Set info
    print 'Setting info'
    dh.create_table_info()
    dh.insert_info('event_name', args.event_name)
    dh.insert_info('event_begin_date', event_begin_date)
    dh.insert_info('event_end_date', end_date)
    dh.insert_info('begin_date', event_begin_date)
    dh.insert_info('end_date', end_date)
    print '-' * 40

    # Fetch page body
    print 'Listing queries'
    dh.create_table_query()
    page = wk.get_page(args.event_name)
    title = page['title']
    titles = [title] + wk.get_redirects(args.event_name)
    queries = map(txt.remove_year, titles)
    queries = txt.reduce_similar_names(queries)
    queries = list(set(queries))
    queries = filter(lambda x: x not in black_list, queries)
    dh.insert_query_many([(q,) for q in queries])

    print 'Done'
