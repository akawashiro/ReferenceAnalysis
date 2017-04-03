# -*- coding: utf-8 -*-
import argparse
from util import db
from util import dt
# from util import pb
from util import slr


LOCALHOST = 'http://localhost:8983/solr/nytimes_nitf/select'
KAREN = 'http://lab.dl.kuis.kyoto-u.ac.jp/~adam/solr/select'


if __name__ == '__main__':
    # Parse args
    ap = argparse.ArgumentParser(
        description='Calculate word value.')

    ap.add_argument('db_file_name',
                    help='SQLite3 DB file name')

    ap.add_argument('-u', '--solr-url', default=KAREN,
                    help='Solr URL')

    args = ap.parse_args()
    print 'DB: {0}'.format(args.db_file_name)
    print 'Solr URL: {0}'.format(args.solr_url)
    print '-' * 40

    # Connect to DB file
    dh = db.DbHandler(args.db_file_name)

    # Get info
    print 'Getting info'
    info_dic = dh.get_info_dic()
    bdate_s = info_dic['begin_date']
    edate_s = info_dic['end_date']
    bdate = dt.str2date(bdate_s)
    edate = dt.str2date(edate_s)
    ev_bdate_s = info_dic['event_begin_date']
    ev_edate_s = info_dic['event_end_date']
    ev_bdate = dt.str2date(ev_bdate_s)
    ev_edate = dt.str2date(ev_edate_s)
    print 'article begin date: {0}'.format(bdate_s)
    print 'article   end date: {0}'.format(edate_s)
    print 'event   begin date: {0}'.format(ev_bdate_s)
    print 'event     end date: {0}'.format(ev_bdate_s)
    print '-' * 40

    # Create Solr NITF handler
    sh = slr.SolrNitfHandler(args.solr_url, bdate, edate)

    # Create tables
    dh.create_table_wordval()
    # Maybe Tanaka wants to make date depending refernce analysis but he failed
    dh.create_table_dateval()

    # Calculate word vals
    print 'Calculating word vals'
    cur, maxval = dh.select_count_distinct_word()
    # pbar = pb.create_pbar(maxval).start()
    for tag, n_name in cur:
        w_doc_num = sh.get_num(n_name)
        w_num = dh.get_w_num(tag, n_name)
        dh.insert_wordval(tag, n_name, w_doc_num, w_num)
        if tag == db.DATE:
            period = dt.dateent2period(n_name)
            if period:
                ft_bdate, ft_edate = period
                days = dt.days(ft_bdate, ft_edate)
                overlap = dt.overlap(ft_bdate, ft_edate, ev_bdate, ev_edate)
                distance = dt.avg_distance(
                    ft_bdate, ft_edate, ev_bdate, ev_edate)
            else:
                days = 0
                overlap = 0
                distance = 0
            dh.insert_dateval(n_name, days, overlap, distance)
        # pbar.update(pbar.currval + 1)
    # pbar.finish()

    # Set info
    print '-' * 40
    print 'Setting info'
    event_doc_num = dh.get_art_num(bdate, edate)
    all_doc_num = sh.get_num('')
    dh.insert_info('event_doc_num', str(event_doc_num))
    dh.insert_info('all_doc_num', str(all_doc_num))
    print 'event_doc_num: {0}'.format(event_doc_num)
    print 'all_doc_num:   {0}'.format(all_doc_num)

    print 'Done'
