#-*- encoding: utf-8 -*-
import datetime
import math
import copy
from util import dt
from util import db
import get_entity_count
import duration_event
import argparse

column_entropy = 28
threemonth = datetime.timedelta(days=92)

BEGIN_DATE = datetime.date(1987, 1, 1)
END_DATE = datetime.date(2007, 6, 20)


def get_all_dict(begin_event_date, end_event_date, get_data_func):
    # print "get_top_entities_list-get_all_dict"
    b = begin_event_date
    e = end_event_date
    all_dict = dict()
    while b < e:
        # print "get_all_dict", b
        p = get_data_func(b, b + threemonth)
        ds = sorted(map(lambda w: (w[0], p.count(w)), list(
            set(p))), key=lambda x: x[1], reverse=True)
        for d in ds:
            if d[0] in all_dict.keys():
                all_dict[d[0]] += d[1]
            else:
                all_dict[d[0]] = d[1]
        b += threemonth
    return all_dict


def score_word(begin_event_date, end_event_date, get_data_func):
    all_dict = get_all_dict(begin_event_date, end_event_date, get_data_func)
    all_dict = {w: c for (w, c) in filter(
        lambda x: x[1] > 3, all_dict.items())}
    b = begin_event_date
    N = 1

    period_dict = dict()
    while b < end_event_date:
        p = get_data_func(b, b + threemonth)
        d = dict(map(lambda x: (x[0], p.count(x)), list(set(p))))
        period_dict[b] = d
        b += threemonth
        N += 1
    normal_average = list()
    geometric_average = list()
    harmonic_average = list()

    for w in all_dict.keys():
        s = 0
        p = 1
        f = 1
        for d in period_dict.values():
            if w in d:
                s += d[w]
                p *= (d[w] + 1)
                f += float(1) / float((d[w] + 1))
        normal_average.append((w, float(s) / N))
        geometric_average.append((w, math.pow(p, 1 / float(N))))
        harmonic_average.append((w, 1 / f * float(N)))

    normal_average = sorted(normal_average, key=lambda x: x[1], reverse=True)
    geometric_average = sorted(
        geometric_average, key=lambda x: x[1], reverse=True)
    harmonic_average = sorted(
        harmonic_average, key=lambda x: x[1], reverse=True)

    print 'normal_average = ["highest top 10 normal_average criterion"]'
    normal = ["highest top 10 normal_average criterion"]
    for (w, c) in normal_average[0:10]:
        normal.append(str(w))
        normal.append(str(c))
    print normal

    print 'geometric_average = ["highest top 10 geometric_average criterion"]'
    geometric = ["highest top 10 geometric_average criterion"]
    for (w, c) in geometric_average[0:10]:
        geometric.append(str(w))
        geometric.append(str(c))
    print geometric

    print 'harmonic_average = ["highest top 10 harmonic_average criterion"]'
    harmonic = ["highest top 10 harmonic_average criterion"]
    for (w, c) in harmonic_average[0:10]:
        harmonic.append(str(w))
        harmonic.append(str(c))
    print harmonic
    return [normal, geometric, harmonic]


def changing_freqeuency_word(begin_event_date, end_event_date, get_data_func):

    # print "changing_freqeuency_word"

    all_dict = get_all_dict(begin_event_date, end_event_date, get_data_func)
    all_dict = {w: c for (w, c) in filter(
        lambda x: x[1] > 3, all_dict.items())}
    word_freq = {w: 0 for w in all_dict.keys()}
    b = begin_event_date
    N = 1

    period_dict = dict()
    while b < end_event_date:
        p = get_data_func(b, b + threemonth)
        d = dict(map(lambda x: (x[0], p.count(x)), list(set(p))))
        period_dict[b] = d
        b += threemonth
        N += 1

    b = begin_event_date
    while b + threemonth < end_event_date:
        # print "changing_freqeuency_word first loop", b
        for w in all_dict.keys():
            # print w
            ds1 = period_dict[b]
            ds2 = period_dict[b + threemonth]
            a1 = 0
            a2 = 0
            if w in ds1.keys():
                a1 = ds1[w]
            if w in ds2.keys():
                a2 = ds2[w]
            word_freq[w] += float(a2 - a1) / float(a2 + a1 + 1) / float(N)
        b += threemonth
    word_freq = sorted(word_freq.items(), key=lambda x: x[1])
    word_freq.reverse()
    print 'res1 = ["highest top 10 changing criterion"]'
    res1 = ["highest top 10 changing criterion"]
    for (w, c) in word_freq[0:10]:
        res1.append(str(w))
        res1.append(str(c))
    print res1
    word_freq.reverse()
    print 'res2 = ["lowest top 10 changing criterion"]'
    res2 = ["lowest top 10 changing criterion"]
    for (w, c) in word_freq[0:10]:
        res2.append(str(w))
        res2.append(str(c))
    print res2
    return [res1, res2]


def get_sheet(ndb, tag):
    print "get_top_entities_list.py-get_sheet-get_top_entities_list"
    d1 = get_top_entities_list(ndb, tag)
    # CATION
    # d1 = list()

    print "Connect to DB and create table"
    dh = db.DbHandler(ndb)
    # begin_event_date = dh.get_info_dic()['event_begin_date']
    # begin_event_date = dt.str2date(begin_event_date)
    begin_event_date = BEGIN_DATE
    end_event_date = dh.get_info_dic()['end_date']
    end_event_date = dt.str2date(end_event_date)
    # begin_date = dh.get_info_dic()['begin_date']
    # begin_date = dt.str2date(begin_date)
    # end_date = dh.get_info_dic()['end_date']
    # end_date = dt.str2date(end_date)

    get_data_func = (lambda b, e: dh.get_ent(b, e, tag, 1000000000))

    print "get_sheet-changing_freqeuency_word"
    d2 = changing_freqeuency_word(
        begin_event_date, end_event_date, get_data_func)
    for d in d2:
        d1.append(d)

    d3 = score_word(
        begin_event_date, end_event_date, get_data_func)
    for d in d3:
        d1.append(d)

    return d1


def get_top_entities_list(ndb, tag):
    print "get_top_entitites_list-get_top_entities_list"
    # Connect to DB and create table
    dh = db.DbHandler(ndb)
    # begin_event_date = dh.get_info_dic()['event_begin_date']
    # begin_event_date = dt.str2date(begin_event_date)
    begin_event_date = BEGIN_DATE
    end_event_date = dh.get_info_dic()['end_date']
    end_event_date = dt.str2date(end_event_date)
    # begin_date = dh.get_info_dic()['begin_date']
    # begin_date = dt.str2date(begin_date)
    end_date = dh.get_info_dic()['end_date']
    end_date = dt.str2date(end_date)

    get_data_func = (lambda b, e: dh.get_ent(b, e, tag, 1000000000))

    dout = ["period"]
    for i in range(0, 10):
        dout.append("Name")
        dout.append("#")
    dout.append("one_to_before_one_cosine_sim")
    dout.append("one_to_all_cosine_sim")
    dout.append("one_to_all_before_cosine_sim")
    dout.append("one_to_all_future_cosine_sim")
    dout.append("one_to_first_three_mounth_sim")
    dout.append("one_to_peak_three_mounth_sim")
    dout.append("one_to_duration_sim")

    dout.append("entropy")
    dout.append("normalized_" + dout[-1])

    dout = [dout]
    all_dict = get_all_dict(begin_event_date, end_event_date, get_data_func)
    future_dict = dict()
    past_dict = dict()
    before_dict = dict()
    first_dict = dict()
    peak_dict = dict()
    dur_dict = dict()

    # make all_dict
    print "make all_dict"
    b = begin_event_date
    e = end_date
    peak_mention = get_entity_count.peak_period_mention(ndb)
    # peak_begin = 0
    # peak_end = 0
    dur = duration_event.get_duration(ndb)

    # print "get_top_entities_list first loop"
    while b < e:
        # print "get_top_entities_list first loop", b
        p = get_data_func(b, b + threemonth)
        ds = sorted(map(lambda w: (w[0], p.count(w)), list(
            set(p))), key=lambda x: x[1], reverse=True)
        if begin_event_date <= b and begin_event_date < b + threemonth:
            for d in ds:
                if d[0] in first_dict.keys():
                    first_dict[d[0]] += d[1]
                else:
                    first_dict[d[0]] = d[1]
        if b < peak_mention and peak_mention <= b + threemonth:
            for d in ds:
                peak_dict[d[0]] = d[1]
        if dur[0] <= b and b + threemonth <= dur[1]:
            for d in ds:
                if d[0] in dur_dict.keys():
                    dur_dict[d[0]] += d[1]
                else:
                    dur_dict[d[0]] = d[1]
        b += threemonth
    future_dict = copy.deepcopy(all_dict)

    b = begin_event_date
    e = end_date
    print "get_top_entities_list second loop"
    while b < e:
        # print "get_top_entities_list second loop", b
        do = [dt.date2str(b)]
        p = get_data_func(b, b + threemonth)
        ds = sorted(map(lambda w: (w[0], p.count(w)), list(
            set(p))), key=lambda x: x[1], reverse=True)
        now_dict = dict()
        for d in ds:
            now_dict[d[0]] = d[1]
        for d in ds[0:10]:
            do.append(d[0])
            do.append(d[1])
        for i in range(0, 10 - len(ds[0:10])):
            do.append("")
            do.append("")
        future_dict = sub_dict(future_dict, now_dict)

        do.append(cosine_sim(now_dict, before_dict))
        do.append(cosine_sim(now_dict, all_dict))
        do.append(cosine_sim(now_dict, past_dict))
        do.append(cosine_sim(now_dict, future_dict))
        do.append(cosine_sim(now_dict, first_dict))
        do.append(cosine_sim(now_dict, peak_dict))
        do.append(cosine_sim(now_dict, dur_dict))

        do.append(entropy(now_dict))
        do.append(0)

        dout.append(do)

        before_dict = now_dict
        past_dict = add_dict(past_dict, now_dict)

        b += threemonth

    # Calculate normalized_entropy
    maxv = 0
    for i in range(1, len(dout)):
        maxv = max(maxv, dout[i][column_entropy])
    if maxv != 0:
        for i in range(1, len(dout)):
            dout[i][column_entropy + 1] = dout[i][column_entropy] / float(maxv)

    return dout


def cosine_sim(d1, d2):
    num = 0
    den1 = 0
    den2 = 0
    for k in d1.keys():
        den1 += d1[k] ** 2
        if k in d2:
            num += d1[k] * d2[k]
    for k in d2.keys():
        den2 += d2[k] ** 2
    if den1 * den2 == 0:
        return 0
    else:
        return num / math.sqrt(den1 * den2)


def add_dict(d1, d2):
    r = d1
    for k in d2.keys():
        if k in r:
            r[k] += d2[k]
        else:
            r[k] = d2[k]
    return r


def sub_dict(d1, d2):
    r = copy.deepcopy(d1)
    for k in d1.keys():
        if k in d2:
            r[k] = r[k] - d2[k]
    return r


def entropy(d):
    s = float(sum(d.values()))
    r = 0
    for v in d.values():
        r -= float(v) / s * math.log(float(v) / s, 2)
    return r


if __name__ == '__main__':
    # Parse args
    ap = argparse.ArgumentParser(
        description='Export experiment result to Excel workbook.')
    ap.add_argument('db_file_name',
                    help='SQLite3 DB file name')
    args = ap.parse_args()

    print "Writing top_entities_list_person sheet"
    dout = get_sheet(
        args.db_file_name, "PERSON")

    print "Writing top_entities_list_location"
    dout = get_sheet(
        args.db_file_name, "LOCATION")

    print "Writing top_entities_list_organization"
    dout = get_sheet(
        args.db_file_name, "ORGANIZATION")

    print "Writing top_entities_list_date"
    dout = get_sheet(
        args.db_file_name, "DATE")
