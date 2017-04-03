#-*- encoding: utf-8 -*-
import datetime
# from util import dt
# from util import db


threemonth = datetime.timedelta(days=92)


class TF_IDF:

    def __init__(self, get_data_func, begin, end):
        # Connect to DB and create table
        threemonth = datetime.timedelta(days=92)
        self.word_list = dict()
        self.periods = list()
        self.get_data_func = get_data_func

        print "__init__", begin, end

        # Set all_words
        b = begin
        e = end
        self.all_words = dict()
        while b < e:
            ee = b + threemonth
            p = get_data_func(b, b + threemonth)
            ds = sorted(map(lambda w: (w[0], p.count(w)), list(
                set(p))), key=lambda x: x[1], reverse=True)
            for d in ds:
                if d[0] in self.all_words.keys():
                    self.all_words[d[0]] += d[1]
                else:
                    self.all_words[d[0]] = d[1]
            b += threemonth

        # filter all_words by the conditoin of frequency is more than 4.
        self.freq_all_words = dict()
        for w in self.all_words.keys():
            if self.all_words[w] > 4:
                self.freq_all_words[w] = self.all_words[w]

        # Set period_words
        b = begin
        e = end
        fset = set(self.freq_all_words.keys())
        self.period_words = dict()
        self.period_words[(begin, end)] = self.all_words
        while b < e:
            ee = b + threemonth
            p = get_data_func(b, b + threemonth)
            ds = sorted(map(lambda w: (w[0], p.count(w)), list(
                set(p))), key=lambda x: x[1], reverse=True)
            self.period_words[(b, ee)] = dict()
            for d in ds:
                if not d[0] in fset:
                    continue
                if d[0] in self.period_words[(b, ee)].keys():
                    self.period_words[(b, ee)][d[0]] += d[1]
                else:
                    self.period_words[(b, ee)][d[0]] = d[1]
            b += threemonth

        # Set tf_idf_vectors
        self.tf_idf_vectors = dict()
        b = begin
        e = end
        while b < e:
            ee = b + threemonth
            self.periods.append((b, ee))
            self.tf_idf_vectors[(b, ee)] = self.get_tf_idf_vector(b, ee)
            b += threemonth

        # Set tf_idf_all
        self.tf_idf_all = self.get_tf_idf_vector(begin, end)

    def get_period_word(self, begin, end):
        if (begin, end) in self.period_words:
            return self.period_words[(begin, end)]

        fset = set(self.freq_all_words.keys())
        p = self.get_data_func(begin, end)
        ds = sorted(map(lambda w: (w[0], p.count(w)), list(
            set(p))), key=lambda x: x[1], reverse=True)
        self.period_words[(begin, end)] = dict()
        for d in ds:
            if not d[0] in fset:
                continue
            if d[0] in self.period_words[(begin, end)].keys():
                self.period_words[(begin, end)][d[0]] += d[1]
            else:
                self.period_words[(begin, end)][d[0]] = d[1]
        return self.period_words[(begin, end)]
        # r = dict()
        # b = begin
        # e = end
        # self.period_words[(b, b + threemonth)] = dict()
        # while b < e:
            # for k in self.period_words[(b, b + threemonth)].keys():
                # if k in r:
                    # r[k] += self.period_words[(b, b + threemonth)][k]
                # else:
                    # r[k] = self.period_words[(b, b + threemonth)][k]
            # b += threemonth
        # return r

    def add_dict(d1, d2):
        r = d1
        for k in d2.keys():
            if k in r:
                r[k] += d2[k]
            else:
                r[k] = d2[k]
        return r

    def get_tf_idf_average_vector(self, begin, end):
        r = dict()
        n = 0.0
        ps = filter(lambda x: begin <= x[0] and x[1] < end, self.periods)
        for p in ps:
            r = self.add_dict(r, self.tf_idf_vectors[p])
            n += 1.0
        for k in r.keys():
            r[k] /= n
        return r

    def get_tf_idf_vector(self, begin, end):
        # print "tf_idf_vector",begin,end
        if (begin, end) in self.tf_idf_vectors:
            return self.tf_idf_vectors[(begin, end)]
        ws = filter(lambda x: self.all_words[x] > 4, self.all_words.keys())
        v = dict()
        for w in ws:
            tf = 0
            if w in self.get_period_word(begin, end):
                tf = float(self.get_period_word(begin, end)[
                           w]) / float(self.freq_all_words[w])
            idf = 0
            if len(filter(lambda x: w in x, self.period_words.values())) > 0:
                idf = float((end - begin).total_seconds() // threemonth.total_seconds()) / \
                    len(filter(lambda x: w in x, self.period_words.values()))
            v[w] = tf * idf
        self.tf_idf_vectors[(begin, end)] = v
        return v


def show_tf_idf_dict(d):
    e = dict()
    for (k, v) in d.items():
        if not v < 0.001:
            e[k] = v
    return e
