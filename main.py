import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import yt_dlp

API_TOKEN = "7734936699:AAGo6x2oLfPSX71Om4PSGUFK7uykRsNHmP4"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Функция для загрузки видео через yt-dlp
def download_youtube_video(url):
    ydl_opts = {
        'format': 'mp4',
        'outtmpl': 'video.%(ext)s',  # Сохраняем видео как video.mp4
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply(f"Привет {message.from_user.full_name}! Отправь мне ссылку на видео YouTube, и я помогу скачать его.")

# Обработчик текстовых сообщений
@dp.message_handler(content_types=['text'])
async def handle_message(message: types.Message):
    url = message.text.strip()

    if not url.startswith("http"):
        await message.reply("Пожалуйста, отправьте корректную ссылку на видео YouTube.")
        return

    await message.answer("Подождите пока закончится загрузка видео")

    try:
        file_path = download_youtube_video(url)

        # Проверяем размер файла
        if os.path.getsize(file_path) > 50 * 1024 * 1024:  # Telegram ограничивает размер до 50 МБ
            await message.reply("Видео слишком большое для отправки через Telegram. Попробуйте другое.")
            os.remove(file_path)
            return

        # Отправляем видео
        with open(file_path, 'rb') as video:
            await message.reply_video(video, caption="Вот ваше видео!")
        
        # Удаляем файл после отправки
        os.remove(file_path)

    except Exception as e:
        await message.reply(f"Ошибка при загрузке видео: {e}")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
