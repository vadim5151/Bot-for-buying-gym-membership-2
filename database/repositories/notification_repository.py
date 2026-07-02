from database.sessions import collection_notification



class NotificationRepository:
    async def delete_periods(self):
        return await collection_notification.delete_one(filter={})
    

    async def find_one(self):
        return await collection_notification.find_one(filter={})
    

    async def insert_one(self, days):
        return await collection_notification.insert_one({'notification_days_period': days})


    async def add_notification_days_period(self, day):
        return await collection_notification.update_one(
            filter={}, 
            update={'$push': {'notification_days_period': day}}
        )

