from stanford_corenlp_pywrapper import CoreNLP
from util import dt
import unidecode
from nltk.corpus import stopwords
import urllib2


class kawata_corenlp_handler:

    def __init__(self):
        # self.proc = CoreNLP(configdict={'annotators': 'tokenize, ssplit, pos, lemma, ner, depparse'}, corenlp_jars=["/usr/local/lib/stanford-corenlp-full-2015-12-09/*"])
        self.proc = CoreNLP(configdict={'annotators': 'tokenize, ssplit, pos, lemma, ner, depparse'}, corenlp_jars=["/CORENLPDIRECTORY/stanford-corenlp-full-2015-12-09/*", "/Users/akira/stanford-corenlp-full-2015-12-09/sutime"])

    def __join_text_date(self, text, date):
        '''
        Join text and date.
        '''
        date_s = dt.date2str(date)
        return '[<date>{0}</date>]\n{1}'.format(date_s, text)

    def get_words(self, text, date):
        n_text = unidecode.unidecode(text)
        joint_text = self.__join_text_date(n_text, date)
        joint_text = n_text

        p = self.proc.parse_doc(joint_text)["sentences"][0]
        # print p
        words = list()
        words = zip(p["ner"], p["tokens"], p["ner"])
        stop = stopwords.words("english")
        words = filter(lambda x: x[1] not in stop, words)
        words = map(lambda x: (x[0], x[1].lower(), x[2]), words)
        # I cannot understand what is most suitable in above line.
        ws = list()
        w = ("", "", "")
        for v in words:
            if v[0] != 'O' and v[0] == w[0]:
                w = (w[0], w[1] + " " + v[1], w[2])
            else:
                ws.append(w)
                w = v
        if w[0] != "":
            ws.append(w)
        words = ws

        return words[1:]

# def get_words_2(self,text,date):
#     n_text = unidecode.unidecode(text)
#     joint_text = self.__join_text_date(n_text, date)
#     joint_text = n_text
#
#     req = urllib2.Request('http://www.voidspace.org.uk')
#     response = urllib2.urlopen(req)
#     the_page = response.read()
#

if __name__ == '__main__':
    kch = kawata_corenlp_handler()
    print 'kch = kawata_corenlp_handler()'
    p = kch.get_words(u"I lived in New York in 2016",
                      dt.str2date(u"2016-02-12"))
    p = kch.get_words(u"I lived in New York in 206/09/18",
                      dt.str2date(u"2016-02-12"))
    print p
