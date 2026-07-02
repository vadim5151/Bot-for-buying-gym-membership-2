from database.sessions import collection_user_waiting_alerts



class WaitingAlertsRepository:
    async def find_one_by_id(self, tg_id):
        return await collection_user_waiting_alerts.find_one(filter={'tg_id': tg_id})


    async def insert_one(self, tg_id, days_left):
        await collection_user_waiting_alerts.insert_one({'tg_id': tg_id, 'days_left': days_left})

    
    async def update_one(self, tg_id, days_left):
        await collection_user_waiting_alerts.update_one(
            filter={'tg_id': tg_id}, 
            update={'$set': {'days_left': days_left}}
        )