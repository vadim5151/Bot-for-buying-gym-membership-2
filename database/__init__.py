import pymongo
from configs.db_config import db_alerts_uri


pymongo.MongoClient(db_alerts_uri)['bgm_alerts']['User_waiting_alerts'].create_index([('tg_id', 1)], unique=True)

