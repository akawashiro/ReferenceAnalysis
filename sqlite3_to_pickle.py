# -*- coding: utf-8 -*-
import argparse
import get_entity_count
import get_top_entities_list
import traceback
import various_name
import tf_idf_sheet
import query_num_sheet
import duration_event
from util import db
import sqlite3
from util import dt
import set_peak_to_info
import copy
import os
import pickle
from multiprocessing import Pool


def ndb_to_xlsx_data(ndb):
    pickle_name = ndb + ".pickle"
    if os.path.exists(pickle_name):
        return

    xlsx_data = []
    try:
        # Set duration info to database
        dur = duration_event.get_duration(ndb)
        # Set peak_mention info to database
        set_peak_to_info.set_peak(ndb)

        dh = db.DbHandler(ndb)
        if int(dh.get_info_dic()["event_doc_num"]) == 0:
            print 'int(xh.info_dic["event_doc_num"]) == 0'
            raise sqlite3.OperationalError(
                'int(xh.info_dic["event_doc_num"]) == 0')

        print "Start for ", ndb

        print "Writing entity_count sheet"
        dout = get_entity_count.get_entity_count(ndb)
        xlsx_data.append(("entity_count", (dout, dur)))

        print "Writing various_name sheet"
        dout = various_name.make_csv_data(ndb)
        xlsx_data.append(("various_name", (dout, dur)))

        print "Writing #articles_for_each_query sheet"
        dout = query_num_sheet.make_csv_data(ndb)
        xlsx_data.append(("articles_for_each_query", (dout, dur)))

        print "Writing top_entities_list_person sheet"
        dout = get_top_entities_list.get_sheet(ndb, "PERSON")
        xlsx_data.append(("top_entities_list_person", (dout, dur)))

        print "Writing top_entities_list_location"
        dout = get_top_entities_list.get_sheet(ndb, "LOCATION")
        xlsx_data.append(("top_entities_list_location", (dout, dur)))

        print "Writing top_entities_list_organization"
        dout = get_top_entities_list.get_sheet(ndb, "ORGANIZATION")
        xlsx_data.append(("top_entities_list_organization", (dout, dur)))

        print "Writing top_entities_list_date"
        dout = get_top_entities_list.get_sheet(ndb, "DATE")
        xlsx_data.append(("top_entities_list_date", (dout, dur)))

        print "Writing tf_idf sheet."
        dout = tf_idf_sheet.make_tf_idf_sheet(ndb)
        xlsx_data.append(("tf_idf", (dout, dur)))

        print 'Done', ndb, '\n\n'

    except:
        traceback.print_exc()
        print "Cannot make xlsx. because"
        print "Remove trash xlsx file\n\n"

    with open(pickle_name, 'w') as f:
        pickle.dump(xlsx_data, f)

    return xlsx_data


def list_xlsx_data_to_xlsx(list_xlsx_data):
    di = dict()
    for xlsx in list_xlsx_data:
        for t in xlsx:
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
    for i in range(1, len(retdata)):
        for j in range(1, len(retdata[i])):
            retdata[i][j] = 0
    nonzero_starts = [-1 for d in list_data]

    # print list_data[0][1]
    # print list_data[1][1]

    for (k, (d, dur)) in enumerate(list_data):
        for i in range(1, len(d)):
            if dur[0] <= dt.str2date(d[i][0]):
                nonzero_starts[k] = i

        # This is the process of normalization
        for j in range(1, len(d[i])):
            s = 0.0
            for i in range(1, len(d)):
                s += float(d[i][j])
            for i in range(1, len(d)):
                d[0][i][j] = float(d[i][j]) / s

    for i in range(1, len(retdata)):
        for j in range(0, len(retdata[i]) - 1):
            s = 0
            n = 0
            for (k, (d, dur)) in enumerate(list_data):
                if nonzero_starts[k] + j < len(retdata[i]):
                    # maneuver on index is shifting
                    s += int(d[i][nonzero_starts[k] + j])
                    n += 1
            if n != 0:
                retdata[i][j] = float(s) / float(n)

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
            if dur[0] <= dt.str2date(data[0][i]):
                nonzero = i
            list_narts[-1].append(na)
            s = s + na

        # This is a process of normalization
        for i in len(list_narts[-1]):
            list_narts[-1][i] = float(list_narts[-1][i]) / float(s)
        nonzero_starts.append(nonzero)

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
    a = float(sum(map(lambda x: len(x), list_data[0]))) / float(len(list_data))
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
            if dur[0] <= dt.str2date(data[0][i]):
                nonzero_starts.append(i)
                break

    for i in range(0, H):
        if not data0[i][0].replace("-", "").isdigit():
            H = i
            break

    for i in range(0, H):
        l = [data0[i][0]]
        for j in range(21, W):
            a = float(0)
            n = 0
            for (k, (d, dur)) in enumerate(list_data):
                if i + nonzero_starts[k] <= H:
                    a += float(d[i + nonzero_starts[k]][j])
                    n = n + 1
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
                l.append(list_data[0][i][j])
            else:
                a = 0
                n = 0
                for (k, (d, dur)) in enumerate(list_data):
                    if i + nonzero_starts[k] < H:
                        a += d[i][j]
                        n = n + 1
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

    # p = Pool(2)
    # list_xlsx_data = p.map(ndb_to_xlsx_data, list_of_ndb)

    # 非並列化版
    list_xlsx_data = map(ndb_to_xlsx_data, list_of_ndb)
