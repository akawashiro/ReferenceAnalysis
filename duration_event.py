# coding:utf-8
# references https://www.wikidata.org/wiki/Wikidata:List_of_properties/Generic
import json
import urllib2
import datetime
from util import db
from util import dt
import argparse

threemonth = datetime.timedelta(days=92)


def get_begin_date_wikidata(event_name):
    url = 'https://en.wikipedia.org/w/api.php?action=query&format=json&prop=pageprops&titles=' + \
        urllib2.quote(event_name) + '&formatversion=2&ppprop=wikibase_item'

    try:
        r = urllib2.urlopen(url)
        root = json.loads(r.read())
        id = root[u'query'][u'pages'][0][u'pageprops'][u'wikibase_item']
        url = 'https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&ids=' + \
            id + '&props=claims&languages=&sitefilter=&formatversion=2'
        r = urllib2.urlopen(url)
        root = json.loads(r.read())
        begin_date = root['entities'][id]['claims']['P580'][
            0]['mainsnak']['datavalue']['value']['time']
        tdatetime = datetime.datetime.strptime(
            begin_date, '+%Y-%m-%dT%H:%M:%SZ')
        return tdatetime.date()
    except:
        d = datetime.date(1900, 1, 1)
        return d


def get_duration(ndb):
    dh = db.DbHandler(ndb)
    event_name = dh.get_info_dic()["event_name"]
    r = get_begin_date_wikidata(event_name)
    senti = (datetime.date(1900, 1, 1), datetime.date(1900, 1, 1) + threemonth)
    dur = senti
    if not r == datetime.date(1900, 1, 1):
        dur = (r, r + threemonth)
    b = dh.get_info_dic()['begin_date']
    b = dt.str2date(b)
    e = dh.get_info_dic()['end_date']
    e = dt.str2date(e)
    if dur == senti:
        while b < e:
            if len(dh.get_ent_all_tag(b, b + threemonth, 100000)) > 0:
                dur = (b, b + threemonth)
                break
            b += threemonth
    if dur == senti:
        dur = (datetime.date(1987, 1, 1),
               datetime.date(1987, 1, 1) + threemonth)
    dh.insert_info('event_begin_date', dt.date2str(dur[0]))
    # print dt.date2str(dur[0])
    # begin_event_date = dh.get_info_dic()['event_begin_date']
    # print begin_event_date
    dh.insert_info('event_duration', dt.date2str(
        dur[0]) + '-' + dt.date2str(dur[1]))
    print "duration of ", ndb, " is ", dur[0], "-", dur[1]
    return dur


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ndb', help='name of database')
    args = ap.parse_args()

    print get_duration(args.ndb)

    # print get_duration('Bosnian War')
    # print get_duration('Berlin Wall')
    # print get_duration('World War II')
    # print get_duration('German reunification')

if __name__ == '__main__':
    main()
