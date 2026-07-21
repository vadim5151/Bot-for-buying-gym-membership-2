import pymongo
from configs.db_config import db_alerts_uri, db_users_uri


pymongo.MongoClient(db_alerts_uri)['bgm_alerts']['User_waiting_alerts'].create_index([('tg_id', 1)], unique=True)
pymongo.MongoClient(db_users_uri)['bgm_users']['Users'].create_index([('tg_id', 1)])
