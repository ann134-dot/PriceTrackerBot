from aiogram import Bot, Dispatcher
import asyncio, aiomysql
from middleware.db_session_middleware import DbSessionMiddleware
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from handlers.handlers import router
from handlers import apsched
from utils.dbconnect import RequestDB
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.DEBUG)

load_dotenv()
bot = Bot(token=os.environ.get('TOKEN')) #  Testv2PythonBot
dp = Dispatcher()
dp.include_router(router)
scheduler = AsyncIOScheduler()


# @dp.message(Command('start'))
# async def get_start(msg: Message, bot: Bot, counter: str): 
#     await bot.send_message(msg.from_user.id, f"Hi, your id: {msg.from_user.id} from bot")
#     await msg.answer(f"Hi, your id: {msg.from_user.id}, Counter: {counter}")


# @dp.message(Command('store')) #, flags={"long_operation": "upload_video_note"}
# async def get_start(msg: Message, request: RequestDB):
#     await asyncio.sleep(5)
#     try:
#         # Split the message text to extract the argument
#         command, argument = msg.text.split(' ', 1)
#         await msg.reply(f'You provided the argument: {argument}')
#         await request.add_data(msg.from_user.id, argument)
#     except ValueError:
#         # Handle the case where no argument is provided
#         await msg.reply('You didn\'t provide an argument. Please use the command like this: /product_signup your_argument')

#     await request.add_data(msg.from_user.id, argument)

async def wrapper_sch_db(pool):
    async with pool.acquire() as connection:
        request = RequestDB(connection)
        await apsched.send_message_cron(bot, request)
        # await apsched.check_min_price(request)


async def start():
    db_params = {
        "host": "hakkio4332.mysql.pythonanywhere-services.com",
        "port": 3306,
        "user": "hakkio4332",
        "password": os.environ.get("DB_PASS"),
        "db": "hakkio4332$default",
        "autocommit": True,
    }

    pool = await aiomysql.create_pool(**db_params)
    dp.update.middleware.register(DbSessionMiddleware(pool))
    
    # await wrapper_sch_db(pool)
    scheduler.add_job(wrapper_sch_db, trigger='interval', seconds=60, kwargs={'pool': pool})
    # scheduler.add_job(apsched.send_message_cron, trigger='cron', hour=datetime.now().hour, minute=datetime.now().minute+1,
    #                 start_date=datetime.now(), kwargs={'bot': bot})

    scheduler.start()

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(start())