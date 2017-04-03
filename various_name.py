import sys
from util import db


def get_various_name(ndb):
    # Connect to DB and create table
    dh = db.DbHandler(ndb)
    names = dh.select_various_names_of_query()
    return names


def make_csv_data(ndb):
    res = []
    for r in get_various_name(ndb):
        res.append(r)
    return [['various name']] + [[x] for x in list(set(res))]


if __name__ == '__main__':
    ndb = sys.argv[1]
    ns = get_various_name(ndb)
    for n in ns:
        print n
    print make_csv_data(ndb)
