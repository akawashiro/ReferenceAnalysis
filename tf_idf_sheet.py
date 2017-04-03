#-*- encoding: utf-8 -*-
import datetime
import math
import copy
from util import dt
from util import db
import get_entity_count
import tf_idf
import duration_event

column_entropy = 27

BEGIN_DATE = datetime.date(1987, 1, 1)
END_DATE = datetime.date(2007, 6, 20)


def make_tf_idf_sheet(ndb):
    # Connect to DB and create table
    dh = db.DbHandler(ndb)
    # begin_event_date = dh.get_info_dic()['event_begin_date']
    # begin_event_date = dt.str2date(begin_event_date)
    begin_event_date = BEGIN_DATE
    end_date = dh.get_info_dic()['end_date']
    end_date = dt.str2date(end_date)

    def make_out_data(get_data_func):
        ti = tf_idf.TF_IDF(get_data_func, begin_event_date, end_date)

        threemonth = datetime.timedelta(days=92)
        dout = ["period"]

        dout.append("tf_idf_one_to_before_one_cosine_sim")
        dout.append("tf_idf_one_to_all_cosine_sim")
        dout.append("tf_idf_one_to_all_before_cosine_sim")
        dout.append("tf_idf_one_to_all_future_cosine_sim")
        dout.append("tf_idf_one_to_first_three_mounth_sim")
        dout.append("tf_idf_one_to_peak_three_mounth_sim")
        dout.append("tf_idf_one_to_duration_sim")

        dout = [dout]

        b = begin_event_date
        e = end_date
        peak_mention = get_entity_count.peak_period_mention(ndb)
        peak_begin = 0
        peak_end = 0
        while b < e:
            if b <= peak_mention and peak_mention <= b + threemonth:
                peak_begin = b
                peak_end = b + threemonth
            b += threemonth

        b = begin_event_date
        e = end_date
        dur = duration_event.get_duration(ndb)
        while b < e:
            print "tf_idf_sheet-second-loop", b
            do = [dt.date2str(b)]

            now_tiv = ti.get_tf_idf_vector(b, b + threemonth)

            # tf_idf_one_to_before_one_cosine_sim
            if not b == begin_event_date:
                do.append(cosine_sim(
                    now_tiv, ti.get_tf_idf_vector(b - threemonth, b)))
            else:
                do.append(0)

            # tf_idf_one_to_all_cosine_sim
            do.append(cosine_sim(now_tiv, ti.tf_idf_all))

            # tf_idf_one_to_all_before_cosine_sim
            c = cosine_sim(
                now_tiv, ti.get_tf_idf_vector(begin_event_date, b))
            print "tf_idf_one_to_all_before_cosine_sim = ", c, begin_event_date, b
            print "now_tiv = "
            print tf_idf.show_tf_idf_dict(now_tiv)
            print "ti.get_tf_idf_vector(begin_event_date, b) = "
            print tf_idf.show_tf_idf_dict(ti.get_tf_idf_vector(begin_event_date, b))
            print c
            if not b == begin_event_date:
                do.append(cosine_sim(
                    now_tiv, ti.get_tf_idf_vector(begin_event_date, b)))
            else:
                do.append(0)

            # tf_idf_one_to_all_future_cosine_sim
            c = cosine_sim(
                now_tiv, ti.get_tf_idf_vector(b + threemonth, e))
            print "tf_idf_one_to_all_future_cosine_sim = ", c, b + threemonth, e
            print "now_tiv = "
            print tf_idf.show_tf_idf_dict(now_tiv)
            print "ti.get_tf_idf_vector(b + threemonth, e) = "
            print tf_idf.show_tf_idf_dict(ti.get_tf_idf_vector(begin_event_date, b))
            print c
            # print c
            do.append(cosine_sim(
                now_tiv, ti.get_tf_idf_vector(b + threemonth, e)))

            # tf_idf_one_to_first_three_mounth_sim
            do.append(cosine_sim(now_tiv, ti.get_tf_idf_vector(
                begin_event_date, begin_event_date + threemonth)))

            # tf_idf_one_to_peak_three_mounth_sim
            do.append(cosine_sim(
                now_tiv, ti.get_tf_idf_vector(peak_begin, peak_end)))

            # tf_idf_one_to_duration_sim
            do.append(cosine_sim(
                now_tiv, ti.get_tf_idf_vector(dur[0], dur[1])))

            dout.append(do)

            b += threemonth

        return dout

    data = make_out_data(lambda b, e: dh.get_ent_all_tag(b, e, 1000000000))
    return data


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
