from database.sessions import collection_users



class UserRepository:
    async def get_all(self):
        return await collection_users.find(filter={}).to_list()
    
    
    async def find_one_by_id(self, tg_id):
        return await collection_users.find_one(filter={'tg_id': tg_id})


    async def insert_one(self, user):
        res = await collection_users.insert_one(user)
        return res
    
    
    async def update_fio(self, tg_id, fio):
        res = await collection_users.update_one(
            filter={'tg_id': tg_id}, 
            update={'$set':{'full_name': fio}}
        )
        return res


    async def update_date_of_birth(self, tg_id, date_of_birth):
        res = await collection_users.update_one(
            filter={'tg_id': tg_id},
            update={'$set':{'date_of_birth': date_of_birth}}
        )
        return res
        

    async def update_notification(self, tg_id, action, days):
        res = await collection_users.update_one(
            filter={'tg_id': tg_id}, 
            update={f'${action}': {'notification_days_period': days}}
        )
        return res


    async def get_all(self):
        return await collection_users.find(filter={}).to_list()
    

    async def get_by_user_id(self, tg_id):
        return await collection_users.find(filter={'tg_id': tg_id}).to_list()
    

    async def update_membership(self, tg_id, purchase_date, expiration_date, month, amount):
        res = await collection_users.update_one(
            filter={'tg_id': tg_id}, 
            update={
                '$set':{   
                    'last_purchase_date': purchase_date, 
                    'expiration_date': expiration_date
                },
                '$push':{
                    'history':{
                        'month': month,
                        'amount': amount,
                        'purchase_date': purchase_date
                    }
                }
            }
        )
        return res
    

    async def find_one_by_id(self, tg_id):
        return await collection_users.find_one(filter={'tg_id': tg_id})


    async def find_by_date(self, from_date, to_date)->list[dict]:
        users_purchases = await collection_users.find().to_list()
        purchases = []
        for user_purchase in users_purchases:
            for purchase in user_purchase['history']:
                if from_date <= purchase['purchase_date'] <= to_date:
                    purchases.append(purchase)
        return purchases
    

    async def add_temp_message_id(self, tg_id, temp_message_id):
        await collection_users.update_one(
            filter={'tg_id': tg_id},  
            update={'$push': {'temp_message_ids': temp_message_id}}
        )


    async def get_temp_message_ids(self, tg_id):
        res = await collection_users.find_one(filter={'tg_id':tg_id})
        return res['temp_message_ids']
    

    async def delete_temp_messages(self, tg_id, chat_id, bot):
        temp_messages = await self.get_temp_message_ids(tg_id)
        await collection_users.update_one(
            filter={'tg_id': tg_id}, 
            update={'$set':{'temp_message_ids': []}}
        )
        for temp_message in temp_messages:
            await bot.delete_message(chat_id, temp_message)

