from database.sessions import collection_price



class PriceRepository:
    async def get_all_prices(self):
        return await collection_price.find(filter={}).to_list()


    async def get_by_month(self, month):
        return await collection_price.find_one(filter={'month': month})

    
    async def delete_one(self, month, amount):
        res = await collection_price.delete_one(filter={'month': month, 'price': amount})
        return res


    async def update_one(self, old_month, old_amount, new_month, new_amount):
        res = await collection_price.update_one(
            filter={'month': old_month, 'price': old_amount}, 
            update={'$set':{'month': new_month, 'price': new_amount}}
        )
        return res
        

    async def insert_one(self, month, amount):
        res = await collection_price.insert_one({'month': month, 'price': amount})
        return res
