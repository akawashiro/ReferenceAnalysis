# -*- coding: utf-8 -*-
import argparse
# import get_entity_count
# import get_top_entities_list
# import granurality
import various_name
# import tf_idf_sheet
# import query_num_sheet
import duration_event
from util import db
from util import dt
from util import xlsx
import sqlite3
import os
import sys
import traceback
import set_peak_to_info


MONTH_DELTA = 1
LIM_WORD = 10
LIM_HSCORE = 20


if __name__ == '__main__':
    # Parse args
    ap = argparse.ArgumentParser(
        description='Export experiment result to Excel workbook.')
    ap.add_argument('db_file_name',
                    help='SQLite3 DB file name')
    ap.add_argument('-f', '--xlsx-file-name',
                    help='Excel workbook file name')
    ap.add_argument('-d', '--month-delta', type=int, default=MONTH_DELTA,
                    help='# of months in each period')
    ap.add_argument('-t', '--lim-word', type=int, default=LIM_WORD,
                    help='# of top words')
    ap.add_argument('-s', '--lim-hscore', type=int, default=LIM_HSCORE,
                    help='# of high score mentions')
    ap.add_argument('-e', '--top-word',
                    help='create "top N X sheet"')
    args = ap.parse_args()

    # Connect to DB and create table
    dh = db.DbHandler(args.db_file_name)
    event_name = dh.get_info_dic()["event_name"].replace(" ", "")
    event_begin_date = dt.str2date(dh.get_info_dic()["event_begin_date"])
    # end_date = dt.str2date(dh.get_info_dic()["end_date"])

    print 'DB: {0}'.format(args.db_file_name)
    if not args.xlsx_file_name:
        args.xlsx_file_name = args.db_file_name.split('.')[0] + '.xlsx'
    print args.xlsx_file_name
    print 'Excel workbook: {0}'.format(args.xlsx_file_name)
    print '# of months / period: {0}'.format(args.month_delta)
    print '# of top word: {0}'.format(args.lim_word)
    print '# of high score mentions: {0}'.format(args.lim_hscore)
    print '-' * 40

    # Create DB handler and xlsx workbook
    xh = xlsx.XlsxHandler(
        args.db_file_name,
        args.xlsx_file_name,
        args.month_delta)

    try:
        # Write sheets
        print 'Writing "info" sheet'
        xh.write_info()

        print "Writing various_name sheet"
        dout = various_name.make_csv_data(args.db_file_name)
        xh.write_csv_date('various_name', dout)
        del xh

        print 'Done\n\n'

    except:
        del xh
        print "Cannot make xlsx. because"
        print traceback.format_exc(sys.exc_info()[2])
        os.remove(args.xlsx_file_name)
        print "Remove trash xlsx file\n\n"
