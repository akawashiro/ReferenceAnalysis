# -*- coding: utf-8 -*-
import argparse
import math
import datetime
from util import db
# from util import pb
from util import dt
from util import txt


def avg(rel_lis):
    '''
    Average rels.
    '''
    l = len(rel_lis)
    if l == 0:
        return 0.0
    else:
        return float(sum(rel_lis)) / float(l)


def sum_log(rel_lis):
    '''
    sum / log(len(rel_lis))
    '''
    l = len(rel_lis)
    if l == 0:
        return 0.0
    else:
        return float(sum(rel_lis)) / math.log(1 + l, 2)


def normalize_a(v, maxv, minv, avgv):
    '''
    Normalize score.
    '''
    r = maxv - minv
    if r == 0.0:
        return 0.0
    else:
        return (v - avgv) / r


def normalize_m(v, maxv, minv, avgv):
    '''
    Normalize score.
    '''
    r = maxv - minv
    if r == 0.0:
        return 0.0
    else:
        return (v - minv) / r


REDUCE_FUNCTIONS = {
    's': sum,
    'a': avg,
    'l': sum_log}


NORMALIZE_FUNCTIONS = {
    'a': normalize_a,
    'm': normalize_m}


if __name__ == '__main__':
    # Parse args
    ap = argparse.ArgumentParser(
        description='Calculate mention score.')

    ap.add_argument('db_file_name',
                    help='SQLite3 DB file name')

    ap.add_argument('-r', '--reduce-function', default='l', choices='sal',
                    help='Reduce function')

    ap.add_argument('-n', '--normalize-function', default='m', choices='am',
                    help='Normalize function')

    args = ap.parse_args()
    print 'DB: {0}'.format(args.db_file_name)
    print 'reduce function: {0}'.format(args.reduce_function)
    print 'normalize function: {0}'.format(args.normalize_function)
    print '-' * 40

    # Connect to DB file
    dh = db.DbHandler(args.db_file_name)

    # Get info
    print 'Getting info'
    info_dic = dh.get_info_dic()
    ev_bdate_s = info_dic['event_begin_date']
    ev_edate_s = info_dic['event_end_date']
    ev_bdate = dt.str2date(ev_bdate_s)
    ev_edate = dt.str2date(ev_edate_s)
    print 'event   begin date: {0}'.format(ev_bdate_s)
    print 'event     end date: {0}'.format(ev_bdate_s)
    print '-' * 40

    # Create table
    dh.create_table_refscore()

    # Set info
    print 'Setting info'
    dh.insert_info('reduce_function', args.reduce_function)
    dh.insert_info('normalize_function', args.normalize_function)
    print '-' * 40

    # Choose reduce function
    red_fun = REDUCE_FUNCTIONS[args.reduce_function]
    nor_fun = NORMALIZE_FUNCTIONS[args.normalize_function]

    # Calc rels
    print 'Calculating scores'
    cur, maxval = dh.select_count_all_reference()
    # pbar = pb.create_pbar(maxval).start()
    for r_id, a_id, q_id, sentences in cur:
        # rel_date
        date_score_lis = dh.get_datescore_lis(r_id)
        rel_date = red_fun([s for s, in date_score_lis])

        # rel_obj
        obj_score_lis = dh.get_wordscore_lis(r_id, db.OBJ_TAGS)
        rel_obj = red_fun([s for s, in obj_score_lis])

        # rel_noun
        noun_score_lis = dh.get_wordscore_lis(r_id, (db.NOUN,))
        rel_noun = red_fun([s for s, in noun_score_lis])

        # rel_ts
        ts = dh.get_ref_date(r_id)
        ts_ = ts + datetime.timedelta(1)
        d = dt.distance(ev_bdate, ev_edate, ts, ts_)
        if d == 0:
            rel_ts = 1.0
        else:
            rel_ts = 1.0 / float(d)

        # rel_pos
        body = dh.get_art_body(a_id)
        query = dh.get_query(q_id)
        rel_pos = 1.0 - txt.find_normalize(query, body)

        dh.insert_refscore(r_id, rel_date, rel_obj, rel_noun, rel_ts, rel_pos)
        # pbar.update(pbar.currval + 1)
    # pbar.finish()

    # Calc rels
    print 'Normalizing scores'
    max_rel_date = dh.get_agg_refscore('rel_date', 'MAX')
    avg_rel_date = dh.get_agg_refscore('rel_date', 'AVG')
    min_rel_date = dh.get_agg_refscore('rel_date', 'MIN')
    max_rel_obj = dh.get_agg_refscore('rel_obj', 'MAX')
    avg_rel_obj = dh.get_agg_refscore('rel_obj', 'AVG')
    min_rel_obj = dh.get_agg_refscore('rel_obj', 'MIN')
    max_rel_noun = dh.get_agg_refscore('rel_noun', 'MAX')
    avg_rel_noun = dh.get_agg_refscore('rel_noun', 'AVG')
    min_rel_noun = dh.get_agg_refscore('rel_noun', 'MIN')
    max_rel_ts = dh.get_agg_refscore('rel_ts', 'MAX')
    avg_rel_ts = dh.get_agg_refscore('rel_ts', 'AVG')
    min_rel_ts = dh.get_agg_refscore('rel_ts', 'MIN')
    max_rel_pos = dh.get_agg_refscore('rel_pos', 'MAX')
    avg_rel_pos = dh.get_agg_refscore('rel_pos', 'AVG')
    min_rel_pos = dh.get_agg_refscore('rel_pos', 'MIN')

    cur, maxval = dh.select_count_all_reference()
    # pbar = pb.create_pbar(maxval).start()
    for r_id, a_id, q_id, sentences in cur:
        rel_date, rel_obj, rel_noun, rel_ts, rel_pos = dh.get_rel(r_id)
        n_rel_date = nor_fun(rel_date, max_rel_date,
                             min_rel_date, avg_rel_date)
        n_rel_obj = nor_fun(rel_obj, max_rel_obj, min_rel_obj, avg_rel_obj)
        n_rel_noun = nor_fun(rel_noun, max_rel_noun,
                             min_rel_noun, avg_rel_noun)
        n_rel_ts = nor_fun(rel_ts, max_rel_ts, min_rel_ts, avg_rel_ts)
        n_rel_pos = nor_fun(rel_pos, max_rel_pos, min_rel_pos, avg_rel_pos)

        dh.update_refscore(r_id, n_rel_date, n_rel_obj,
                           n_rel_noun, n_rel_ts, n_rel_pos)
        # pbar.update(pbar.currval + 1)
    # pbar.finish()

    print 'Done'
