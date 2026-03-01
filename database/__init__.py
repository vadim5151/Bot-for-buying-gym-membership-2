import pymongo

pymongo.MongoClient('localhost', port=27017)['Bot_for_buying_gym_membership']['User_waiting_alerts'].create_index([('tg_id', 1)], unique=True)
