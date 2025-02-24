from aiogram.types import KeyboardButton as kb, ReplyKeyboardMarkup, InlineKeyboardButton as ib, InlineKeyboardMarkup

main = ReplyKeyboardMarkup(keyboard=[
    [kb(text='Function'), kb(text='Deactivated')],
    [kb(text='More'), kb(text='More')]
])

start_create_bot = InlineKeyboardMarkup(inline_keyboard=[
    [ib(text='Off', callback_data='off'), ib(text='Reboot', callback_data='reboot'), ib(text='Console', callback_data='console')],
    [ib(text='Screenshot', callback_data='screen'), ib(text='Video', callback_data='video'), ib(text='Web cam', callback_data='wbc')],
    [ib(text='Open file', callback_data='load'), ib(text='Open link', callback_data='browser'), ib(text='Get info', callback_data='get_info')]
])

main.resize_keyboard=True