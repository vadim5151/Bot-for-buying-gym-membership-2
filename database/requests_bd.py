from motor.motor_asyncio import AsyncIOMotorClient



client = AsyncIOMotorClient('localhost', port=27017)

conn = client['Bot_for_buying_gym_membership']

collection_users = conn['Users']

collection_purchases = conn['Purchases']

collection_price = conn['Price']

collection_notification = conn['Notifications']

collection_user_waiting_alerts = conn['User_waiting_alerts']

collection_temp_message_ids = conn['Temp_message_ids']

