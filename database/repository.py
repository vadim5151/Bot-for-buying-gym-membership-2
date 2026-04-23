from database.requests_bd import *



class PriceRepository:
    async def get_all_prices(self):
        return await collection_price.find(filter={}).to_list()


    async def get_by_month(self, month):
        return await collection_price.find_one(filter={'month': month})

    
    async def delete_one(self, month, amount):
        res = await collection_price.delete_one(filter={'month': month, 'price': amount})
        return res


    async def update_one(self, old_month, old_amount, new_month, new_amount):
        res = await collection_price.update_one(filter={'month': old_month, 'price': old_amount}, 
                                update={'$set':{'month': new_month, 'price': new_amount}})
        return res
        

    async def insert_one(self, month, amount):
        res = await collection_price.insert_one({'month': month, 'price': amount})
        return res


class PurchasesRepository:
    async def get_by_user_id(self, tg_id):
        return await collection_purchases.find(filter={'tg_id': tg_id}).to_list()
    

    async def update_membership(self, tg_id, date_purchase, expiration_date):
        res = await collection_purchases.update_one(filter={'tg_id': tg_id}, 
                                          update={'$set': {'purchase_date': date_purchase, 
                                                           'expiration_date': expiration_date}})
        return res
    

    async def find_one_by_id(self, tg_id):
        return await collection_purchases.find_one(filter={'tg_id': tg_id})


    async def find_by_date(self, from_date, to_date):
        return await collection_purchases.find(filter={'purchase_date': {'$gte':from_date, '$lte':to_date}}).to_list()
    

    async def insert_purchase(self, tg_id, month, amount, date, expiration_date):
        res = await collection_purchases.insert_one({
            "tg_id": tg_id,
            "month": month,
            "amount": amount,
            "purchase_date": date,
            "expiration_date": expiration_date
        })

        return res
    

class UserRepository:
    async def find_one_by_id(self, tg_id):
        return await collection_users.find_one(filter={'tg_id': tg_id})


    async def insert_one(self, user):
        res = await collection_users.insert_one(user)
        return res
    
    
    async def update_fio(self, tg_id, fio):
        res = await collection_users.update_one(filter={'tg_id': tg_id}, 
                                      update={'$set':{'full_name': fio}})
        return res


    async def update_date_of_birth(self, tg_id, date_of_birth):
        res = await collection_users.update_one(filter={'tg_id': tg_id},
                                        update={'$set':{'date_of_birth': date_of_birth}})
        return res
        


    async def update_notification(self, tg_id, action, days):
        res = await collection_users.update_one(filter={'tg_id': tg_id}, update={f'${action}': {'notification_days_period': days}})
        return res


class NotificationRepository:
    async def find_one(self):
        return await collection_notification.find_one(filter={})


class TempMessageRepository:
    async def insert_one(self, tg_id):
        await collection_temp_message_ids.insert_one({'tg_id': tg_id, 'temp_message_ids': []})


    async def add_temp_message_id(self, tg_id, temp_message_id):
        await collection_temp_message_ids.update_one(filter={'tg_id': tg_id},  update={'$push': {'temp_message_ids': temp_message_id}})


    async def get_temp_message_ids(self, tg_id):
        res = await collection_temp_message_ids.find_one(filter={'tg_id':tg_id})
        return res['temp_message_ids']
    

    async def delete_temp_messages(self, tg_id, chat_id, bot):
        temp_messages = await self.get_temp_message_ids(tg_id)
        
        await collection_temp_message_ids.update_one(filter={'tg_id': tg_id}, update={'$set':{'temp_message_ids': []}})

        for temp_message in temp_messages:
            await bot.delete_message(chat_id, temp_message)


    