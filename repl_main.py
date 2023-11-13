import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from datetime import datetime, timedelta
import requests
import urllib.parse


logging.basicConfig(level=logging.INFO)


file = 'headers'
header = {}
with open(file, 'r') as read:
    is_end = True
    curr_header = ''
    for line in read.readlines():
        line = line.strip()
        if line.startswith('POST') or line.startswith('GET'):
            header[line] = {}
            curr_header = line
            is_end = False
        elif not line:
            is_end = True
        elif not is_end:
            x = line.split(':', 1)
            # if x[0] == 'Cookie':
            #     continue
            try:
                header[curr_header][x[0]] = x[1].strip()
            except:
                print(x[0])


def get_product(product):
    product = urllib.parse.quote(product)

    with requests.session() as s:
        url = "https://kaspi.kz/shop/ab/tests/script-cookie?ui=DESKTOP&tg=none"
        response = s.get(url, headers=header['GET /shop/ab/tests/script-cookie?ui=DESKTOP&tg=none HTTP/1.1'])

        if response.status_code != 200:
            print(f"Failed to retrieve the page. \nURL: {url} \nStatus code: {response.status_code}")
            return None

        url = 'https://kaspi.kz/yml/product-view/pl/filters?text='+product+'&page=0&all=false&fl=true&ui=d&q=%3AavailableInZones%3AMagnum_ZONE1&i=-1&c=750000000'    
        response = s.get(url, headers=header['GET /yml/product-view/pl/filters?text=sony%20wh-1000xm&page=0&all=false&fl=true&ui=d&q=%3AavailableInZones%3AMagnum_ZONE1&i=-1&c=750000000 HTTP/1.1'])
        if response.status_code == 200:
            json_data = response.json()
            # print(len(json_data['data']['cards'])) #priceFormatted, unitPrice, unitSalePrice, title, shopLink, previewImages[0]['medium']
            # for data in json_data['data']['cards']:
            #     print(f'''title: {data["title"]} 
            #         \nunitPrice: {data["unitPrice"]} 
            #         \nunitSalePrice: {data["unitSalePrice"]} 
            #         \npriceFormatted: {data["priceFormatted"]} 
            #         \n shopLink: {data["shopLink"]} 
            #         \npreviewImages[0]["medium"] : {data["previewImages"][0]["medium"]}  
            #         ''')
            #     print(50*'-')
            return json_data['data']['cards']
        else:
            print(f"Failed to retrieve the page. \nURL: {url} \nStatus code: {response.status_code}")
            return None



bot = Bot(token='6984427087:AAHUvFXWan98qRsXwr23SCesM80_zzLe370') # remove later; Testv2PythonBot
dp = Dispatcher()
scheduler = AsyncIOScheduler()
temp_db_dict = {'wh1000xm4': [1877070048, 445332485, 504531671, 717401264], 'la roche':  [445332485, 504531671, 717401264]}
temp_db_min_price = {'wh1000xm4': 136712}
temp_db_user_prod = {1877070048: ['wh1000xm4']}

@dp.message(Command('start'))
async def get_start(msg: Message):
    await msg.answer(f"Hello, {msg.from_user.first_name}! Send /track {{product_name}} to track the cheapest price of a product on kaspi. We'll notify you if the price drops off")


@dp.message(Command('track')) #, flags={"long_operation": "upload_video_note"}
async def track(msg: Message):
    try:
        # Split the message text to extract the argument
        command, argument = msg.text.split(' ', 1)
    except ValueError:
        # Handle the case where no argument is provided
        await msg.reply('You didn\'t provide an argument. Please use the command like this: /track your_argument')
    
    try:
        if temp_db_dict.get(argument):
            if msg.from_user.id in temp_db_dict[argument]:
                await msg.reply('you are already tracking this product')
                return
            else:
                temp_db_dict[argument].append(msg.from_user.id)
        else:        
            temp_db_dict[argument] = [msg.from_user.id]
        
        await msg.answer(f'{argument} is added for tracking')
        
        products = get_product(argument)

        min_price = 100000000
        min_prod= {}

        for product in products:
            if min_price > product['unitPrice']:
                min_price = product['unitPrice']
                min_prod = product
        temp_db_min_price[argument] = min_price
        await msg.answer(
                    f'''We'll notify you if the minimum price for the product will change. Current minimum price for the product:
                        \ntitle: {min_prod["title"]} 
                        \nunitPrice: {min_prod["unitPrice"]} 
                        \nunitSalePrice: {min_prod["unitSalePrice"]} 
                        \npriceFormatted: {min_prod["priceFormatted"]} 
                        \n shopLink: {min_prod["shopLink"]} 
                        '''
        )
        if temp_db_user_prod.get(msg.from_user.id):
            temp_db_user_prod[msg.from_user.id].append(argument)
        else:
            temp_db_user_prod[msg.from_user.id] = [argument]

    except Exception as e:
        await msg.reply('Something is wrong. Try again')
        print(e)



def check_min_price():

    min_prod_info = {}

    for key in temp_db_dict.keys():
        products = get_product(key)
        for product in products:
            if temp_db_min_price[key] > product['unitPrice']:
                temp_db_min_price[key] = product['unitPrice']
                min_prod_info[key] = product
        
    return min_prod_info


async def send_message_cron(bot: Bot):

    min_prod_price = check_min_price()
    if min_prod_price:
        for product_name, product in min_prod_price.items():
            for id in temp_db_dict[product_name]:
                await bot.send_message(id, 
                        f'''Price for {product_name} has dropped. Current minimum price for the product:
                        \ntitle: {product["title"]} 
                        \nunitPrice: {product["unitPrice"]} 
                        \nunitSalePrice: {product["unitSalePrice"]} 
                        \npriceFormatted: {product["priceFormatted"]} 
                        \n shopLink: {product["shopLink"]} 
                        '''
                        )
    else:
        await bot.send_message(1877070048, 'No update')


# for debugging
@dp.message(Command('get_all'))
async def get_all_product(msg: Message):
    strings = ''
    for product_name, ids in temp_db_dict.items():
        strings+= f'\n{product_name}: {ids}'
    await msg.answer(
            f''' All products:
            {strings}
            '''
    )

@dp.message(Command('get_list'))
async def get_user_prod_list(msg: Message):
    strings = ''
    if temp_db_user_prod.get(msg.from_user.id):
        for product_name in temp_db_user_prod[msg.from_user.id]:
            strings+= f'\n{product_name}'
        await msg.answer(
                f''' All products of {msg.from_user.full_name}:
                {strings}
                '''
        )
    else:
        await msg.answer('You dont have any tracking products')
    

@dp.message(Command('delete'))
async def delete_product(msg:Message):
    try:
        # Split the message text to extract the argument
        command, argument = msg.text.split(' ', 1)
    except ValueError:
        # Handle the case where no argument is provided
        await msg.reply('You didn\'t provide an argument. Please use the command like this: /delete your_argument')
       
    if argument in temp_db_dict and  msg.from_user.id in temp_db_dict.get(argument):
        temp_db_dict[argument].remove(msg.from_user.id)
        temp_db_user_prod[msg.from_user.id].remove(argument)

        await msg.answer('deleted')
    else:
        await msg.answer('you dont have the product in your tracking list')


async def start():

    # scheduler.add_job(send_message_cron, trigger='cron', hour=datetime.now().hour, minute=datetime.now().minute+1,
    #                 start_date=datetime.now(), kwargs={'bot': bot})
    # scheduler.add_job(send_message_cron, trigger='interval', minutes=40, kwargs={'bot': bot})
    scheduler.start()
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(start())