#-*- encoding: utf-8 -*-
import argparse
import csv
from util import wk
from util import txt

if __name__ == '__main__':
    # Parse args
    ap = argparse.ArgumentParser(
        description='Get variant names.')

    ap.add_argument('--event_name', help='event name')
    args = ap.parse_args()

    # Fetch page body
    page = wk.get_page(args.event_name)
    title = page['title']
    titles = [title] + wk.get_redirects(args.event_name)
    queries = map(txt.remove_year, titles)
    queries = txt.reduce_similar_names(queries)
    queries = list(set(queries))
    queries = map(lambda x: [x], queries)

    with open("various_name_sheet/variant_name_" + args.event_name.replace(" ", "") + ".csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(queries)
        f.close()

    print queries

    print 'Done'
