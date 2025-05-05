# -*- coding: utf-8 -*-

# Module author: @ftgmodulesbyfl1yd
# Ukrainian translate by @Murzetskyy
# Modified for delete-only filter by ChatGPT

from .. import loader, utils


@loader.tds
class FiltersMod(loader.Module):
    """Filters module (удаляет сообщения по ключевым словам)"""

    strings = {"name": "Filters"}

    async def client_ready(self, client, db):
        self.db = db

    async def filtercmd(self, message):
        """Додає фільтр в список. Використання: .filter ключ [у відповіді]"""
        filters = self.db.get("Filters", "filters", {})
        key = utils.get_args_raw(message).lower()
        reply = await message.get_reply_message()
        chatid = str(message.chat_id)

        if not key and not reply:
            return await message.edit("<b>Нема аргументів або відповіді.</b>")

        if chatid not in filters:
            filters.setdefault(chatid, {})

        if key in filters[chatid]:
            return await message.edit("<b>Такий фільтр слів вже існує.</b>")

        # Просто сохраняем ключ, без привязки к сообщению
        filters[chatid].setdefault(key, True)
        self.db.set("Filters", "filters", filters)
        await message.edit(f'<b>Фільтр "{key}" збережено!</b>')

    async def stopcmd(self, message):
        """Видаляє фільтр зі списку. Використання: .stop ключ"""
        filters = self.db.get("Filters", "filters", {})
        args = utils.get_args_raw(message)
        chatid = str(message.chat_id)

        if chatid not in filters:
            return await message.edit("<b>Нема фільтрів в цьому чаті.</b>")

        if not args:
            return await message.edit("<b>Нема аргументів.</b>")

        try:
            filters[chatid].pop(args)
            self.db.set("Filters", "filters", filters)
            await message.edit(f'<b>Фільтр "{args}" видаленно з списку фільтрів чату!</b>')
        except KeyError:
            return await message.edit(f'<b>Нема "{args}" такого фільтру.</b>')

    async def stopallcmd(self, message):
        """Очищає список фільтрів для чату"""
        filters = self.db.get("Filters", "filters", {})
        chatid = str(message.chat_id)

        if chatid not in filters:
            return await message.edit("<b>Нема фільтрів в цьому чаті.</b>")

        filters.pop(chatid)
        self.db.set("Filters", "filters", filters)
        await message.edit("<b>Усі фільтри були видалені з списку фільтрів цього чату!</b>")

    async def filterscmd(self, message):
        """Показує збережені фільтри"""
        filters = self.db.get("Filters", "filters", {})
        chatid = str(message.chat_id)

        if chatid not in filters:
            return await message.edit("<b>Нема фільтрів в цьому чаті.</b>")

        msg = ""
        for _ in filters[chatid]:
            msg += f"<b>• {_}</b>\n"
        await message.edit(
            f"<b>Список фільтрів в цьому чаті: {len(filters[chatid])}\n\n{msg}</b>"
        )

    async def watcher(self, message):
        try:
            filters = self.db.get("Filters", "filters", {})
            chatid = str(message.chat_id)
            m = message.text.lower()
            if chatid not in filters:
                return

            for _ in filters[chatid]:
                if len(_.split()) == 1:
                    if _ in m.split():
                        await message.delete()
                        break
                else:
                    if _ in m:
                        await message.delete()
                        break
        except Exception as e:
            print(f"Watcher error: {e}")
