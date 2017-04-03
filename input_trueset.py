# -*- coding: utf-8 -*-
import argparse
import csv
from util import db


if __name__ == '__main__':
    # Parse args
    ap = argparse.ArgumentParser(
        description='Input true data set.')

    ap.add_argument('db_file_name',
        help='SQLite3 DB file name')

    ap.add_argument('csv_file_name',
        help='True data set CSV file name')

    args = ap.parse_args()
    print 'DB: {0}'.format(args.db_file_name)
    print 'CSV: {0}'.format(args.csv_file_name)
    print '-' * 40

    # Connect to DB file
    dh = db.DbHandler(args.db_file_name)

    # Input true data set
    print 'Inputting true data set'
    dh.create_table_trueset()
    with open(args.csv_file_name, 'rU') as csvfile:
        csvreader = csv.reader(csvfile, dialect='excel')
        for row in csvreader:
            r_id, c = int(row[0]), int(row[1])
            dh.insert_trueset(r_id, c)

    print 'Done'

