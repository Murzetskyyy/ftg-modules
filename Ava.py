from telethon import functions, types
from .. import loader, utils
import io
from PIL import Image

def register(cb): cb(AvaMod())

class AvaMod(loader.Module):
    """Встановлення/видалення аватарок через команди"""
    strings = {'name': 'Ava'}

    def __init__(self):
        self.name = self.strings['name']

    async def client_ready(self, client, db): pass

    async def avacmd(self, message):
        'Встановити аватарку <reply to image>'
        reply = await message.get_reply_message()
        if not reply or not reply.media:
            return await message.edit("❌ Відповідай на фото.")

        await message.edit("📥 Завантажуємо та обрізаємо фото...")
        file = await make_square(reply)

        uploaded = await message.client.upload_file(file)

        await message.edit("🖼 Ставимо аватарку...")
        await message.client(
            functions.photos.UploadProfilePhotoRequest(
                file=uploaded
            )
        )
        await message.edit("✅ Аватарку встановлено!")

    async def delavacmd(self, message):
        'Видалити активну аватарку'
        ava = await message.client.get_profile_photos('me', limit=1)
        if ava:
            await message.edit("🗑 Видаляємо першу аватарку...")
            await message.client(functions.photos.DeletePhotosRequest(ava))
            await message.edit("✅ Перша аватарка видалена.")
        else:
            await message.edit("😶 У тебе немає аватарок.")

    async def delavascmd(self, message):
        'Видалити усі аватарки'
        ava = await message.client.get_profile_photos('me')
        if ava:
            await message.edit("🗑 Видаляємо всі аватарки...")
            await message.client(functions.photos.DeletePhotosRequest(ava))
            await message.edit("✅ Усі аватарки видалені.")
        else:
            await message.edit("😶 У тебе немає аватарок.")

async def make_square(msg):
    """Обрезает фото до квадрата (центрирует)"""
    image = Image.open(io.BytesIO(await msg.download_media(bytes)))
    width, height = image.size

    # Центрированная обрезка
    min_dim = min(width, height)
    left = (width - min_dim) // 2
    top = (height - min_dim) // 2
    image = image.crop((left, top, left + min_dim, top + min_dim)).convert("RGB")

    output = io.BytesIO()
    image.save(output, format='JPEG', quality=100)
    output.seek(0)
    return output
