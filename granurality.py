#-*- encoding: utf-8 -*-
import argparse
import datetime
import csv
import math
import copy
import re
import sys
from util import dt
from util import txt
from util import db
from util import wk


def is_past(s):
    p = '^PAST_REF$'
    p = re.compile(p)
    return re.match(p, s) != None


def is_present(s):
    p = '^PRESENT_REF$'
    p = re.compile(p)
    return re.match(p, s) != None


def is_date(s):
    p = '^[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'
    p = re.compile(p)
    return re.match(p, s) != None


def is_mounth(s):
    p = '^[0-9][0-9][0-9][0-9]-[0-9][0-9]'
    p = re.compile(p)
    return re.match(p, s) != None


def is_season(s):
    p = '^[0-9][0-9][0-9][0-9]-[A-Z][A-Z]'
    p = re.compile(p)
    return re.match(p, s) != None


def is_year(s):
    p = '^[0-9][0-9][0-9][0-9]'
    p = re.compile(p)
    return re.match(p, s) != None


def get_granurality_list(ndb):
    # Connect to DB and create table
    dh = db.DbHandler(ndb)
    begin_event_date = dh.get_info_dic()['event_begin_date']
    begin_event_date = dt.str2date(begin_event_date)
    begin_date = dh.get_info_dic()['begin_date']
    begin_date = dt.str2date(begin_date)
    end_date = dh.get_info_dic()['end_date']
    end_date = dt.str2date(end_date)

    def make_out_data(get_data_func):
        threemonth = datetime.timedelta(days=92)
        dout = ["period"]
        dout.append("xxxx-xx-xx")
        dout.append("xxxx-xx")
        dout.append("xxxx")
        dout.append("PRESENT_REF")
        dout.append('xxxx-SU/SP/FA/WN')
        dout.append("PAST_REF")
        for i in range(-6, 0):
            dout.append("normalized_" + dout[-i])
        dout = [dout]

        # make all_dict
        b = begin_date
        e = end_date
        while b < e:
            p = get_data_func(b, b + threemonth)
            p = map(lambda x: x[0], p)
            d = len(filter(is_date, p))
            m = len(filter(is_mounth, p))
            y = len(filter(is_year, p))
            n = len(filter(is_present, p))
            s = len(filter(is_season, p))
            o = len(filter(is_past, p))
            dout.append([dt.date2str(b), d, m, y, n, s, o, 0, 0, 0, 0, 0, 0])

            b += threemonth
        for i in range(-6, 0):
            maxv = 0
            for j in range(1, len(dout)):
                maxv = max(maxv, dout[j][i - 6])
            if maxv != 0:
                for j in range(1, len(dout)):
                    dout[j][i] = dout[j][i - 6] / float(maxv)

        return dout

    return make_out_data(lambda b, e: dh.get_ent(b, e, 'HEIDEL_TIME', 1000000000))

if __name__ == '__main__':
    print is_date('2009-09-18')
    print is_date('2009-09-kk')
    print is_mounth('2009-09')

    gr = get_granurality_list(sys.argv[1])
    print gr

# classify HEIDEL_TIME values
