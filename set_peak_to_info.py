import get_entity_count
from util import db
from util import dt


def set_peak(ndb):
    peak_mention = get_entity_count.peak_period_mention(ndb)
    dh = db.DbHandler(ndb)
    dh.insert_info('peak_mention', dt.date2str(peak_mention))
