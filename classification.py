# -*- coding: utf-8 -*-
import argparse
import numpy
from sklearn import tree, cross_validation
from util import db
from util import pb


def get_score(clf, train_features, train_labels):
    X_train, X_test, y_train, y_test = cross_validation.train_test_split(train_features, train_labels, test_size=0.5, random_state=0)
    clf.fit(X_train, y_train)
    score = clf.score(X_test, y_test)
    return score


if __name__ == '__main__':
    # Parse args
    ap = argparse.ArgumentParser(
        description='Input true data set.')

    ap.add_argument('db_file_name',
        help='SQLite3 DB file name')

    args = ap.parse_args()
    print 'DB: {0}'.format(args.db_file_name)
    print '-' * 40

    # Connect to DB file
    dh = db.DbHandler(args.db_file_name)
    dh.create_table_classifiedset()

    # Training
    print 'Getting data'
    true_lis = dh.get_true_lis()
    train_features = numpy.array([list(t[1:4]) for t in true_lis])
    train_labels = numpy.array([t[4] for t in true_lis])

    # Classification
    print 'Training'
    max_score = 0.0
    best_clf = None
    for i in range(100):
        clf = tree.DecisionTreeClassifier()
        X_train, X_test, y_train, y_test = cross_validation.train_test_split(train_features, train_labels, test_size=0.5, random_state=0)
        clf.fit(X_train, y_train)
        score = clf.score(X_test, y_test)
        if score >= max_score:
            max_score = score
            best_clf = clf

    print 'Classification'
    cur, maxval = dh.select_count_all_refscore()
    pbar = pb.create_pbar(maxval).start()
    for r_id, rel_date, rel_obj, rel_noun, n_rel_date, n_rel_obj, n_rel_noun in cur:
        c = best_clf.predict(numpy.array([n_rel_date, n_rel_obj, n_rel_noun]))[0]
        dh.insert_classifiedset(r_id, int(c))
        pbar.update(pbar.currval + 1)
    pbar.finish()

    # Validation
    mean_lis = list()
    std_lis = list()
    clf = tree.DecisionTreeClassifier()
    for i in range(100):
        scores = cross_validation.cross_val_score(clf, train_features, train_labels, cv=5)
        mean_lis.append(scores.mean())
        std_lis.append(scores.std() * 2)
    print sum(mean_lis) / float(len(mean_lis))
    print sum(std_lis) / float(len(std_lis))

    print 'Done'
