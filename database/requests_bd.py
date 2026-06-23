import logging

from motor.motor_asyncio import AsyncIOMotorClient
import pymongo

from configs.db_config import db_uri



client = AsyncIOMotorClient(db_uri)

conn = client['Bot_for_buying_gym_membership']

collection_users = conn['Users']

collection_purchases = conn['Purchases']

collection_price = conn['Price']

collection_notification = conn['Notifications']

collection_user_waiting_alerts = conn['User_waiting_alerts']

collection_temp_message_ids = conn['Temp_message_ids']

