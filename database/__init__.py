import pymongo
from configs.db_config import db_uri


pymongo.MongoClient(db_uri)['Bot_for_buying_gym_membership']['User_waiting_alerts'].create_index([('tg_id', 1)], unique=True)

