# coding:utf-8
# references https://www.wikidata.org/wiki/Wikidata:List_of_properties/Generic
import json
import urllib2
import datetime


def get_begin_date(event_name):
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
        return tdatetime
    except:
        d = datetime.date(1900, 1, 1)
        return d


def main():
    print get_begin_date('Bosnian War')
    print get_begin_date('Berlin Wall')
    print get_begin_date('World War II')
    print get_begin_date('German reunification')

if __name__ == '__main__':
    main()
