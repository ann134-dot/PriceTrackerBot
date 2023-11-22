from aiogram import Bot
from utils.dbconnect import RequestDB
from utils.requests_product import get_product


async def check_min_price(request: RequestDB):

    min_prod_info = {}

    for key in await request.get_all_products():
        products = get_product(key)
        for product in products:
            if await request.get_min_price(key) > product['unitPrice']:
                await request.update_min_value(key, product['unitPrice'])
                min_prod_info[key] = product

    return min_prod_info


async def send_message_cron(bot: Bot, request: RequestDB):
    min_prod_price = await check_min_price(request)
    if min_prod_price:
        # print(min_prod_price)
        for product_name, product in min_prod_price.items():
            for id in await request.get_id_by_product(product_name):
                # print(id, product_name)
                await bot.send_message(chat_id=id, text=f'''Price for {product_name} has dropped. Current minimum price for the product:
                        \ntitle: {product["title"]} 
                        \nunitPrice: {product["unitPrice"]} 
                        \nunitSalePrice: {product["unitSalePrice"]} 
                        \npriceFormatted: {product["priceFormatted"]} 
                        \n shopLink: {product["shopLink"]} 
                        '''
                        )
    else:
        # delete later
        await bot.send_message(chat_id=1877070048, text='No update')
