from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from utils.dbconnect import RequestDB
from utils.requests_product import get_product
import re

router = Router()

@router.message(Command('start'))
async def get_start(msg: Message):
    await msg.answer(f"Hello, {msg.from_user.first_name}! Send /track {{product_name}} to track the cheapest price of a product on kaspi. We'll notify you if the price drops off")



@router.message(Command('track')) #, flags={"long_operation": "upload_video_note"}
async def track(msg: Message, request: RequestDB):
    try:
        # Split the message text to extract the argument
        command, argument = msg.text.split(' ', 1)
    except ValueError:
        # Handle the case where no argument is provided
        await msg.reply('You didn\'t provide an argument. Please use the command like this: /track your_argument')
        return
    try:
        argument = re.sub(' +', ' ', argument).lower()
        if await request.is_user_product_data(msg.from_user.id, argument):
            await msg.answer('The product already in your tracking list')
            return
        
        products = get_product(argument)
        if not products:
            await msg.reply('Cannot find the product')
            return
        
        await request.add_data(msg.from_user.id, argument)
        await msg.answer(f'{argument} is added for tracking')
        
        min_price_db = await request.get_min_price(argument)

        min_price_db = min_price_db if min_price_db else 100000000000
        min_price = min_price_db
        min_prod= {}
        # print(min_price)

        for product in products:
            if min_price >= product['unitPrice']:
                min_price = product['unitPrice']
                min_prod = product
        # print('dd3')
        if min_price != min_price_db:
            await request.add_min_price(argument, min_price)

        # print(min_prod)
        await msg.answer(
                    f'''We'll notify you if the minimum price for the product will change. Current minimum price for the product:
                        \ntitle: {min_prod["title"]} 
                        \nunitPrice: {min_prod["unitPrice"]} 
                        \nunitSalePrice: {min_prod["unitSalePrice"]} 
                        \npriceFormatted: {min_prod["priceFormatted"]} 
                        \n shopLink: {min_prod["shopLink"]} 
                        '''
        )

    except Exception as e:
        await msg.reply('Something is wrong. Try again')
        print(e)



# for debugging
@router.message(Command('get_all'))
async def get_all_product(msg: Message, request: RequestDB):
    strings = ''
    products = await request.get_all_products()

    for product in products:
        ids = await request.get_id_by_product(product)
        strings+= f"\n{product}: {ids}"
    
    await msg.answer(
            f''' All products:
            {strings}
            '''
    )

@router.message(Command('get_list'))
async def get_user_prod_list(msg: Message, request: RequestDB):
    strings = ''
    products = await request.get_products_by_id(msg.from_user.id)
    if products:
        for product_name in products:
            strings+= f'\n{product_name}'
        await msg.answer(
                f''' All products of {msg.from_user.full_name}:
                {strings}
                '''
        )
    else:
        await msg.answer('You dont have any tracking products')
    

@router.message(Command('delete'))
async def delete_product(msg:Message, request: RequestDB):
    try:
        # Split the message text to extract the argument
        command, argument = msg.text.split(' ', 1)
    except ValueError:
        # Handle the case where no argument is provided
        await msg.reply('You didn\'t provide an argument. Please use the command like this: /delete your_argument')
        return
    try:
        argument = re.sub(' +', ' ', argument).lower()

        if await request.delete_user_product(argument, msg.from_user.id):
            await msg.answer('deleted')
        else:
            await msg.answer('you dont have the product in your tracking list')
        
    except Exception as e:
        await msg.reply('Something is wrong. Try again')
        print(e)
