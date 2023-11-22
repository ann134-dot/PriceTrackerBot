import asyncpg

class RequestDB:
    def __init__(self, connector: asyncpg.pool.Pool):
        self.connector = connector

    async def add_data(self, user_id, user_request):
        
        query = f" insert into products " \
                    f"values('{user_id}', '{user_request}')  on conflict do nothing;"
        
        await self.connector.execute(query)

        
    
    async def get_user_data(self, user_id):
        query = f"select product from products where user_id = {user_id};"
        
        rows =  await self.connector.fetch(query)
        rows = [row['product'] for row in rows]
        return rows

    async def is_user_product_data(self, user_id, product):
        query = f"select user_id, product from products where user_id = {user_id} and product = '{product}';"
        
        row =  await self.connector.fetch(query)

        return True if dict(row) else False

    async def get_all_data(self):
        query = f"select user_id, product from products;"
        
        rows =  await self.connector.fetch(query)
        rows = [dict(row) for row in rows]  
        return rows   
    
    async def get_all_products(self):
        query = f"select distinct product from products;"
        
        rows =  await self.connector.fetch(query)
        rows = [row['product'] for row in rows]  
        return rows   
    
    async def get_id_by_product(self, product):
        query = f"select user_id from products where product = '{product}';"
        
        rows =  await self.connector.fetch(query)
        rows = [row['user_id'] for row in rows]  
        return rows  

    async def get_products_by_id(self, id):
        query = f"select product from products where user_id = '{id}';"
        
        rows =  await self.connector.fetch(query)
        rows = [row['product'] for row in rows]  
        return rows    
    
    async def delete_user_product(self, product, user_id):
        query = f"delete from products where user_id ={user_id} and product = '{product}'"
         
        if user_id in await self.get_id_by_product(product):
            await self.connector.execute(query)      
            return True
        else:
            return False


    async def get_min_price(self, product):
        query = f"select min_price from min_price where product = '{product}';"
        row = await self.connector.fetchrow(query)
        return row['min_price'] if row else None

    async def add_min_price(self, product, price):
        query = f" insert into min_price " \
                    f"values('{product}', '{price}')  on conflict do nothing;"
        
        await self.connector.execute(query)

    async def update_min_value(self, product, price):
        query = f"UPDATE min_price " \
                    f"SET min_price = {price} WHERE product = '{product}';"
        
        await self.connector.execute(query)
