#-*- encoding: utf-8 -*-
import os
import datetime
import exceptions
import re
import codecs
import xml.etree.ElementTree as ET

def call_heideltime(doc,date):
    ds = date.isoformat()
    with codecs.open('/home/akira/heideltime-standalone/input-heidel-wrapper.txt','w','utf-8') as f:
        f.write(doc)
    os.system('cd /home/akira/heideltime-standalone; java -jar de.unihd.dbs.heideltime.standalone.jar input-heidel-wrapper.txt -dct '+ds+' -t NEWS > output-heidel-wrapper.txt')
    with codecs.open('/home/akira/heideltime-standalone/output-heidel-wrapper.txt','r','utf-8') as f:
        d = f.read()
        return d
    raise OSError('I cannnot call heideltime.')


# Return list of tuple (tag,string,normalized date)
def doc_to_timex3(doc,date):
    xml = call_heideltime(doc,date)
    rs = re.findall(r'<TIMEX.*?TIMEX3>',xml)
    result = list()
    for r in rs:
        root = ET.fromstring(r)
        result.append(('HEIDEL_TIME',root.attrib['value'],root.text))
    print result
    return result


if __name__ == '__main__':
    s = 'Last summer, they met every Tuesday afternoon, from 1:00 pm to 3:00 pm.'
    tnow = datetime.datetime.now()
    print call_heideltime(s,tnow)
    print doc_to_timex3(s,tnow)
