# -*- coding: utf-8 -*-
import argparse
import get_entity_count
import get_top_entities_list
import granurality
import various_name
import tf_idf_sheet
import query_num_sheet
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
        # Set duration info to database
        duration_event.get_duration(args.db_file_name)
        # Set peak_mention info to database
        set_peak_to_info.set_peak(args.db_file_name)

        if int(xh.info_dic["event_doc_num"]) == 0:
            raise sqlite3.OperationalError(
                'int(xh.info_dic["event_doc_num"]) == 0')

        # Write sheets
        print 'Writing "info" sheet'
        xh.write_info()

        print "Writing entity_count sheet"
        dout = get_entity_count.get_entity_count(args.db_file_name)
        xh.write_csv_date("entity_count", dout)

        print "Writing various_name sheet"
        dout = various_name.make_csv_data(args.db_file_name)
        xh.write_csv_date('various_name', dout)

        print "Writing #articles_for_each_query sheet"
        dout = query_num_sheet.make_csv_data(args.db_file_name)
        xh.write_csv_date('#articles_for_each_query', dout)

        print "Writing top_entities_list_person sheet"
        dout = get_top_entities_list.get_sheet(
            args.db_file_name, "PERSON")
        xh.write_csv_date("top_entities_list_person", dout)

        print "Writing top_entities_list_location"
        dout = get_top_entities_list.get_sheet(
            args.db_file_name, "LOCATION")
        xh.write_csv_date("top_entities_list_location", dout)

        print "Writing top_entities_list_organization"
        dout = get_top_entities_list.get_sheet(
            args.db_file_name, "ORGANIZATION")
        xh.write_csv_date("top_entities_list_organization", dout)

        print "Writing top_entities_list_date"
        dout = get_top_entities_list.get_sheet(
            args.db_file_name, "DATE")
        xh.write_csv_date("top_entities_list_date", dout)

        # print "Writing top_entities_list_heidel_time"
        # dout = get_top_entities_list.get_sheet(
        # args.db_file_name, "HEIDEL_TIME")
        # xh.write_csv_date("top_entities_list_heidel_time", dout)

        print "Writing tf_idf sheet."
        dout = tf_idf_sheet.make_tf_idf_sheet(args.db_file_name)
        xh.write_csv_date("tf_idf", dout)

        # print "Writing granurality"
        # dout = granurality.get_granurality_list(args.db_file_name)
        # xh.write_csv_date("granurality", dout)
        # Close before exit
        del xh

        print 'Done\n\n'

    except:
        del xh
        print "Cannot make xlsx. because"
        print traceback.format_exc(sys.exc_info()[2])
        os.remove(args.xlsx_file_name)
        print "Remove trash xlsx file\n\n"
