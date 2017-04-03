# -*- coding: utf-8 -*-
import argparse
# import get_entity_count
# import get_top_entities_list
# import traceback
# import granurality
# import various_name
# import tf_idf_sheet
# import query_num_sheet
# import duration_event
# from util import db
from util import dt
from util import xlsx
# import sqlite3
import os
# import sys
# from util import dt
# import traceback
# import set_peak_to_info
import copy
import pickle
# from multiprocessing import Pool
import datetime


def ndb_to_xlsx_data(ndb):
    pickle_name = ndb + ".pickle"
    print pickle_name

    if os.path.exists(pickle_name):
        with open(pickle_name, 'r') as f:
            ret = pickle.load(f)
            return ret

    xlsx_data = []
    return xlsx_data


def list_xlsx_data_to_xlsx(list_xlsx_data):
    di = dict()
    for x in list_xlsx_data:
        for t in x:
            if t[0] in di:
                di[t[0]].append(t[1])
            else:
                di[t[0]] = [t[1]]

    out_xlsx_data = []

    for t in di.items():
        if t[0] == "entity_count":
            d = summarize_entity_count(t[1])
            out_xlsx_data.append((t[0], d))
        elif t[0] == "various_name":
            d = summarize_n_various_name(t[1])
            out_xlsx_data.append((t[0], d))
        elif t[0] == "articles_for_each_query":
            d = summarize_article_for_each_query(t[1])
            out_xlsx_data.append((t[0], d))
        elif t[0].count("top_entities_list"):
            d = summarize_top_enetities_list(t[1])
            out_xlsx_data.append((t[0], d))
        elif t[0] == "tf_idf":
            d = summarize_tf_idf_sheet(t[1])
            out_xlsx_data.append((t[0], d))

    # print "list_xlsx_data_to_xlsx"
    # print out_xlsx_data

    return out_xlsx_data


# list data is list of (data, duration)
# duration = (start, end)
def summarize_entity_count(list_data):
    retdata = copy.deepcopy(list_data[0][0])
    # print retdata
    for i in range(1, len(retdata)):
        for j in range(1, len(retdata[i])):
            retdata[i][j] = 0
    nonzero_starts = [-1 for d in list_data]

    # print list_data[0][1]
    # print list_data[1][1]

    for (k, (d, dur)) in enumerate(list_data):
        for i in range(1, len(d)):
            a = dur[0]
            if type(a) == datetime.datetime:
                a = a.date()
                # print a, d[i][0]
            if nonzero_starts[k] == -1 and a <= dt.str2date(d[i][0]):
                nonzero_starts[k] = i

        # This is the process of normalization
        for j in range(1, len(d[i])):
            s = 0.0
            for i in range(1, len(d)):
                s += float(d[i][j])
            for i in range(1, len(d)):
                if not s == 0.0:
                    d[i][j] = float(d[i][j]) / float(s)

    for i in range(1, len(retdata)):
        for j in range(1, len(retdata[i])):
            s = 0
            n = 0
            for (k, (d, dur)) in enumerate(list_data):
                if nonzero_starts[k] + i < len(retdata):
                    # print i, nonzero_starts[k] + j
                    # maneuver on index is shifting
                    s += float(d[nonzero_starts[k] + i][j])
                    n += 1
            # print s
            if n != 0:
                retdata[i][j] = float(s) / float(n)

    # print retdata
    return retdata


# list data is list of (data, duration)
# duration = (start, end)
def summarize_article_for_each_query(list_data):
    periods = []
    naverages = []
    list_narts = []
    nonzero_starts = []
    for i in range(1, len(list_data[0][0][0])):
        periods.append(list_data[0][0][0][i])
    for (data, dur) in list_data:
        list_narts.append([])
        nonzero = len(data[0]) - 2
        s = 0

        for i in range(1, len(data[0])):
            na = 0
            for j in range(1, len(data)):
                na += data[j][i]
            a = data[0][i].split("_")[0]
            b = dur[0]
            if type(b) == datetime.datetime:
                b = b.date()
            if b <= dt.str2date(a):
                nonzero = min(i, nonzero)
            list_narts[-1].append(na)
            s = s + na

        # This is a process of normalization
        for i in range(len(list_narts[-1])):
            list_narts[-1][i] = float(list_narts[-1][i]) / float(s)
        nonzero_starts.append(nonzero)
    # print nonzero_starts

    for i in range(len(list_narts[0])):
        s = 0
        n = 0
        for j in range(len(list_narts)):
            # maneuver on index is shifting
            if nonzero_starts[j] + i < len(list_narts[j]):
                s += list_narts[j][nonzero_starts[j] + i]
            n += 1
        if not n == 0:
            naverages.append(float(s) / float(n))
        else:
            naverages.append(0)
    retdata = []
    for (p, n) in zip(periods, naverages):
        retdata.append([p, n])

    # print periods
    # print naverages

    return retdata


# list data is list of (data, duration)
# duration = (start, end)
def summarize_n_various_name(list_data):
    a = float(sum(map(lambda x: len(x[0]), list_data))) / float(len(list_data))
    print a
    retdata = [["average number of various name"], [a]]
    return retdata


# list data is list of (data, duration)
# duration = (start, end)
def summarize_top_enetities_list(list_data):
    W = len(list_data[0][0][0])
    H = len(list_data[0][0])
    data0 = list_data[0][0]

    retdata = list()
    l = []
    for j in [0] + range(21, W):
        l.append(data0[0][j])
    retdata.append(l)

    nonzero_starts = []
    for (data, dur) in list_data:
        for i in range(1, H):
            if not data0[i][0].replace("-", "").isdigit():
                break
            # print data[0]
            if dur[0] <= dt.str2date(data[i][0]):
                nonzero_starts.append(i)
                break

    for i in range(1, H):
        if not data0[i][0].replace("-", "").isdigit():
            H = i
            break

    for i in range(0, H):
        l = [data0[i][0]]
        for j in range(21, W):
            a = float(0)
            n = 0
            for (k, (d, dur)) in enumerate(list_data):
                if i + nonzero_starts[k] < H:
                    a += float(d[i + nonzero_starts[k]][j])
                    n = n + 1
            if n != 0:
                a /= float(n)
            l.append(a)
        retdata.append(l)
    return retdata


# list data is list of (data, duration)
# duration = (start, end)
def summarize_tf_idf_sheet(list_data):
    data0 = list_data[0][0]
    H = len(data0)
    W = len(data0[0])

    nonzero_starts = []
    for (data, dur) in list_data:
        for i in range(1, H):
            if dur[0] <= dt.str2date(data0[i][0]):
                nonzero_starts.append(i)
                break

    retdata = []
    for i in range(H):
        l = []
        for j in range(W):
            if i == 0 or j == 0:
                l.append(list_data[0][0][i][j])
            else:
                a = 0
                n = 0
                for (k, (d, dur)) in enumerate(list_data):
                    if i + nonzero_starts[k] < H:
                        a += d[i][j]
                        n = n + 1
                if 0 < n:
                    a /= float(n)
                l.append(a)
        retdata.append(l)
    return retdata


if __name__ == '__main__':
    ap = argparse.ArgumentParser(
        description='Summary CSV file for many db files.')
    ap.add_argument('-ld', '--list-of-databases', required=True)

    args = ap.parse_args()
    list_of_ndb = []

    with open(args.list_of_databases, 'r') as f:
        for s in f:
            list_of_ndb.append(s.replace("\n", ""))

    # p = Pool(4)
    list_xlsx_data = map(ndb_to_xlsx_data, list_of_ndb)

    out_xlsx_data = list_xlsx_data_to_xlsx(list_xlsx_data)
    xh = xlsx.XlsxHandler(
        list_of_ndb[0],
        "summary_for_" + args.list_of_databases + ".xlsx",
        1)
    for t in out_xlsx_data:
        # print t[0]
        # print type(t[0])
        # print t[1]
        xh.write_csv_date(t[0], t[1])

    del xh
