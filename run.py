import asyncio
import sys
import ctypes
import config
import main_bots.main as main
from aiogram import Bot, Dispatcher, F 
from main_bots.handler1 import router

async def run_as_admin():
    """START OF ADMINISTRATOR"""#us if you need
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

async def main_():
    try:
        bot = Bot(token=config.TOKEN)
        dp = Dispatcher()

        dp.include_router(router)
        
        await dp.start_polling(bot)
    except Exception as e:
        print(e)

if __name__=='__main__':
    try:
        asyncio.run(main.main_cycle())
        asyncio.run(main_())
    except KeyboardInterrupt:
        pass