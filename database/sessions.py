from motor.motor_asyncio import AsyncIOMotorClient

from configs.db_config import db_alerts_uri, db_users_uri, db_common_uri



client_db_common = AsyncIOMotorClient(db_common_uri)
client_db_users = AsyncIOMotorClient(db_users_uri)
client_db_alerts = AsyncIOMotorClient(db_alerts_uri)

conn_db_common = client_db_common['bgm_common']
conn_db_users = client_db_users['bgm_users']
conn_db_alerts = client_db_alerts['bgm_alerts']

collection_users = conn_db_users['Users']
collection_price = conn_db_common['Price']
collection_notification = conn_db_common['Notifications']
collection_user_waiting_alerts = conn_db_alerts['User_waiting_alerts']


