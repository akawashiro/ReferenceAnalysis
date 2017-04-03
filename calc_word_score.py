# -*- coding: utf-8 -*-
import argparse
import math
from util import db
# from util import pb


def calc_rel_word(w_num, t_num, w_doc_num, a_doc_num):
    '''
    Return (w_num / t_num) * log(a_doc_num / w_doc_num)
    '''
    if t_num == 0 or a_doc_num == 0 or w_doc_num == 0:
        return 0.0
    else:
        return (float(w_num) / float(t_num)) * math.log(float(a_doc_num) / float(w_doc_num), 2)


def calc_rel_date(days, overlap, distance):
    '''
    Return 1 / distance.
    '''
    if days == 0:
        return 0.0
    elif distance == 0:
        return 1.0
    else:
        return 1.0 / float(distance)


if __name__ == '__main__':
    # Parse args
    ap = argparse.ArgumentParser(
        description='Calculate mention score.')

    ap.add_argument('db_file_name',
                    help='SQLite3 DB file name')

    args = ap.parse_args()
    print 'DB: {0}'.format(args.db_file_name)
    print '-' * 40

    # Connect to DB file
    dh = db.DbHandler(args.db_file_name)

    # Get info
    info_dic = dh.get_info_dic()
    e_doc_num = int(info_dic['event_doc_num'])
    a_doc_num = int(info_dic['all_doc_num'])
    tag_counts = dict([(t, dh.get_tag_num(t)) for t in db.ALL_TAGS])

    # Calc WordScore
    print 'Calculating WordScore'
    dh.create_table_wordscore()
    cur, maxval = dh.select_count_all_wordval()
    # pbar = pb.create_pbar(maxval).start()
    for tag, n_name, w_num, w_doc_num in cur:
        t_num = tag_counts[tag]
        rel = calc_rel_word(w_num, t_num, w_doc_num, a_doc_num)
        dh.insert_wordscore(tag, n_name, rel)
        # pbar.update(pbar.currval + 1)
    # pbar.finish()

    # Calc WordScore
    print 'Calculating DateScore'
    dh.create_table_datescore()
    cur, maxval = dh.select_count_all_dateval()
    # pbar = pb.create_pbar(maxval).start()
    for n_name, days, overlap, distance in cur:
        rel = calc_rel_date(days, overlap, distance)
        dh.insert_datescore(n_name, rel)
        # pbar.update(pbar.currval + 1)
    # pbar.finish()

    print 'Done'
