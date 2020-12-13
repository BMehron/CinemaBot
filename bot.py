import aiohttp
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import bot_language
from response import Response

bot = Bot(token='1459766841:AAGddtLpCCbUqGYrhDNlgnBz_TfKUTyr6ZQ')
dp = Dispatcher(bot)
parser = Response()


@dp.message_handler(commands=['start'])
async def start_handle(message: types.Message):
    await message.answer(bot_language.START_MSG)


@dp.message_handler(commands=['help'])
async def help_handle(message: types.Message):
    await message.answer(bot_language.HELP_MSG)


@dp.message_handler(regexp=r"\/i\d+")
async def click_id_handle(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    watch_button = types.InlineKeyboardButton(text="Смотреть онлайн", callback_data="watch")
    keyboard.add(watch_button)

    async with aiohttp.ClientSession() as cur_session:
        await parser.response_id_query(cur_session, int(message['text'][2:]))
        response, photo = parser.description, parser.photo

    if photo is not None:
        await message.answer("[ ]({}) {}".format(photo, response),
                             parse_mode='markdown', reply_markup=keyboard)
    else:
        await message.answer(response, reply_markup=keyboard)


@dp.message_handler(content_types=["text"])
async def query_handle(message: types.Message):
    async with aiohttp.ClientSession() as cur_session:
        response = await parser.response_name_query(cur_session, message.text.lower())
        await message.answer(response)


@dp.callback_query_handler(lambda call: True)
async def click_button_handle(call: types.CallbackQuery):
    if call.message:
        keyboard = types.InlineKeyboardMarkup()
        if call.data == "watch":
            back_button = types.InlineKeyboardButton(text="Назад", callback_data="back")
            ivi_button = types.InlineKeyboardButton(text="💰 IVI", url=bot_language.LINK_IVI + parser.title)
            okko_button = types.InlineKeyboardButton(text="💰 OKKO", url=bot_language.LINK_OKKO + parser.title)
            kp_button = types.InlineKeyboardButton(text="💰 KINOPOISK", url=bot_language.LINK_KINOPOISK + parser.title)
            fs_button = types.InlineKeyboardButton(text="🆓 FS", url=bot_language.LINK_FS + parser.title)
            hd_button = types.InlineKeyboardButton(text="🆓 HDREZKA", url=bot_language.LINK_HDREZKA + parser.title)
            ba_button = types.InlineKeyboardButton(text="🆓 BASKINO", url=bot_language.LINK_BASKINO + parser.title)

            keyboard.add(back_button)
            keyboard.add(ivi_button, okko_button, kp_button)
            keyboard.add(fs_button, hd_button, ba_button)

            await call.message.edit_text(text=bot_language.WATCH_MSG, reply_markup=keyboard)
        if call.data == 'back':
            watch_button = types.InlineKeyboardButton(text="Смотреть онлайн", callback_data="watch")
            keyboard.add(watch_button)

            response, photo = parser.description, parser.photo

            if photo is not None:
                await call.message.edit_text("[ ]({}) {}".format(photo, response),
                                             parse_mode='markdown', reply_markup=keyboard)
            else:
                await call.message.answer(response, reply_markup=keyboard)


if __name__ == '__main__':
    executor.start_polling(dp)
