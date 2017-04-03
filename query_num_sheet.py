# -*- coding: utf-8 -*-
import sys
import argparse
import datetime
from util import db
from util import txt
from util import dt
from util import pb
from util import slr


LOCALHOST = 'http://localhost:8983/solr/nytimes_nitf/select'
KAREN = 'http://lab.dl.kuis.kyoto-u.ac.jp/~adam/solr/select'
BEGIN_DATE = datetime.date(1987, 1, 1)
END_DATE = datetime.date(2007, 6, 20)
MIN_ARTICLE_NUM = 10
INCLUDE_NEIGHBOR = 1
REFERENCE_TYPE = 'd'


# Get article for a given query
# Return raw articles list
def get_articles(query):
    sh = slr.SolrNitfHandler(KAREN, BEGIN_DATE, END_DATE)

    num = sh.get_num(query)
    if num < MIN_ARTICLE_NUM:
        return []
    docs = sh.get_all_docs(query)
    return docs


# Count the number of articles in each period
# Return dictionary whose keys are period and values are the number of articles
def count_articles(articles):
    pubtimes = map(lambda x: x['publicationDate'].split('T')[0], articles)
    pubtimes = map(dt.str2date, pubtimes)
    # print pubtimes
    begin = BEGIN_DATE
    end = END_DATE
    threemonth = datetime.timedelta(days=92)
    ret = dict()
    while begin < end:
        e = begin + threemonth
        c = len(filter(lambda x: begin <= x and x < e, pubtimes))
        ret[(begin, e)] = c
        begin = e
    # print ret
    return ret


def make_csv_data(db_file_name):
    dh = db.DbHandler(db_file_name)
    queries = dh.select_various_names_of_query()
    ret = [['']]

    begin = BEGIN_DATE
    end = END_DATE
    threemonth = datetime.timedelta(days=92)
    periods = []
    while begin < end:
        e = begin + threemonth
        ret[0].append(dt.date2str(begin) + '_' + dt.date2str(e))
        periods.append((begin, e))
        begin = e

    for q in queries:
        arts = get_articles(q)
        d = count_articles(arts)
        ret.append([])
        ret[-1].append(q)
        for p in periods:
            ret[-1].append(d[p])
    return ret


if __name__ == '__main__':
    arts = get_articles("Berlin Wall")
    count_articles(arts)
    d = make_csv_data(
        '../heidel7/result/BerlinWall_one_sentence_filter.sqlite3')
    print d
