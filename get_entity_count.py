#-*- encoding: utf-8 -*-
import argparse
import datetime
import csv
from util import dt
from util import db

BEGIN_DATE = datetime.date(1987, 1, 1)
END_DATE = datetime.date(2007, 6, 20)

if __name__ == '__main__':
    # Parse args
    ap = argparse.ArgumentParser(
        description='Get event info.')

    ap.add_argument('db_file_name',
                    help='SQLite3 DB file name')

    ap.add_argument('event_name',
                    help='event name')

    ap.add_argument('event_begin_date', type=dt.str2date,
                    help='event begin date')

    ap.add_argument('event_end_date', type=dt.str2date,
                    help='event end date')

    args = ap.parse_args()
    print 'DB: {0}'.format(args.db_file_name)
    print 'event name: {0}'.format(args.event_name)
    print 'event begin date: {0}'.format(dt.date2str(args.event_begin_date))
    print 'event   end date: {0}'.format(dt.date2str(args.event_end_date))
    print '-' * 40

    # Connect to DB and create table
    dcon = db.DbHandler(args.db_file_name)

    threemonth = datetime.timedelta(days=92)
    # b = args.event_begin_date
    b = BEGIN_DATE
    e = args.event_end_date
    output = [["period", "#mention", "#person(all)", "#person(new)", "#person(unique)", "#location(all)",
               "#location(new)", "#location(unique)", "#organization(all)", "#organization(new)", "#organization(unique)"]]
    ps = set()
    ls = set()
    os = set()
    while b < e:
        d = dt.date2str(b)
        m = dcon.get_ref_num(b, b + threemonth)
        p = dcon.get_ent(b, b + threemonth, "PERSON", 100000000)
        l = dcon.get_ent(b, b + threemonth, "LOCATION", 100000000)
        o = dcon.get_ent(b, b + threemonth, "ORGANIZATION", 100000000)
        nps = ps.union(set(p))
        nls = ls.union(set(l))
        nos = os.union(set(o))
        output.append([d, m, len(p), len(nps) - len(ps), len(set(p)), len(l),
                       len(nls) - len(ls), len(set(l)), len(o), len(nos) - len(os), len(set(o))])
        ps = nps
        ls = nls
        os = nos
        b += threemonth

    with open("entity_count_" + args.event_name.replace(" ", "") + ".csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(output)
        f.close()

    print 'Done'


def peak_period_mention(ndb):
    dcon = db.DbHandler(ndb)
    # b = dt.str2date(dcon.get_info_dic()["event_begin_date"])
    b = BEGIN_DATE
    e = dt.str2date(dcon.get_info_dic()["end_date"])
    threemonth = datetime.timedelta(days=92)
    mm = 0
    ret = b
    while b < e:
        m = dcon.get_ref_num(b, b + threemonth)
        if mm < m:
            mm = m
            ret = b
        b += threemonth
    return ret


def get_entity_count(fdb):
    # Connect to DB and create table
    dcon = db.DbHandler(fdb)
    # begin_event_date = dcon.get_info_dic()['event_begin_date']
    # begin_event_date = dt.str2date(begin_event_date)
    begin_event_date = BEGIN_DATE
    end_event_date = dcon.get_info_dic()['end_date']
    end_event_date = dt.str2date(end_event_date)

    threemonth = datetime.timedelta(days=92)
    b = begin_event_date
    e = end_event_date
    output = [["period", "#mention", "#person(all)", "#person(new)", "#person(unique)", "#location(all)",
               "#location(new)", "#location(unique)", "#organization(all)", "#organization(new)", "#organization(unique)"]]
    ps = set()
    ls = set()
    os = set()
    while b < e:
        d = dt.date2str(b)
        m = dcon.get_ref_num(b, b + threemonth)
        p = dcon.get_ent(b, b + threemonth, "PERSON", 100000000)
        l = dcon.get_ent(b, b + threemonth, "LOCATION", 100000000)
        o = dcon.get_ent(b, b + threemonth, "ORGANIZATION", 100000000)
        nps = ps.union(set(p))
        nls = ls.union(set(l))
        nos = os.union(set(o))
        output.append([d, m, len(p), len(nps) - len(ps), len(set(p)), len(l),
                       len(nls) - len(ls), len(set(l)), len(o), len(nos) - len(os), len(set(o))])
        ps = nps
        ls = nls
        os = nos
        b += threemonth
    return output
