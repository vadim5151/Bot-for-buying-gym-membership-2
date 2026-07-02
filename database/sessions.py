from motor.motor_asyncio import AsyncIOMotorClient

from configs.db_config import db_uri



client = AsyncIOMotorClient(db_uri)

conn = client['Bot_for_buying_gym_membership']

collection_users = conn['Users']

collection_price = conn['Price']

collection_notification = conn['Notifications']

collection_user_waiting_alerts = conn['User_waiting_alerts']


