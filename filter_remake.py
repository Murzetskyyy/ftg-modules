# -*- coding: utf-8 -*-

# Original module author: @ftgmodulesbyfl1yd
# Ukrainian translate by @Murzetskyy

from .. import loader, utils
import re

@loader.tds
class FiltersMod(loader.Module):
    """Фільтрує повідомлення за ключовими словами"""

    strings = {"name": "Filters"}

    async def client_ready(self, client, db):
        self.db = db

    def normalize_text(self, text):
        """Знижує регістр, прибирає пунктуацію та замінює латиницю на кирилицю"""
        replace_map = {
            'а': 'а', 'a': 'а', 'A': 'а', '@': 'а',
            'е': 'е', 'ё': 'е', 'e': 'е', 'E': 'е',
            'о': 'о', '0': 'о', 'O': 'о',
            'с': 'с', 'c': 'с', 'C': 'с',
            'р': 'р', 'p': 'р', 'P': 'р',
            'у': 'у', 'y': 'у', 'Y': 'у',
            'к': 'к', 'k': 'к', 'K': 'к', 'ꚍ': 'к',
            'х': 'х', 'x': 'х', 'X': 'х',
            'т': 'т', 't': 'т', 'T': 'т', 'τ': 'т',
            'н': 'н', 'h': 'н', 'H': 'н',
            'в': 'в', 'b': 'в', 'B': 'в',
            'м': 'м', 'm': 'м', 'M': 'м',
            'п': 'п', 'n': 'п', 'π': 'п',
            'и': 'и', 'u': 'и', 'ι': 'и',
            'л': 'л', 'l': 'л', 'L': 'л',
            'г': 'г', 'r': 'г', 'R': 'г',
            'д': 'д', 'ð': 'д',
            'з': 'з', '3': 'з',
            'ч': 'ч', '4': 'ч',
            'б': 'б', '6': 'б',
            'я': 'я', 'q': 'я',
        }

        text = text.lower()
        text = re.sub(r"[^\w\s]", "", text)
        return "".join(replace_map.get(c, c) for c in text)

    async def filtercmd(self, message):
        """Додає фільтр у список. Використання: .filter ключ [у відповіді]"""
        filters = self.db.get("Filters", "filters", {})
        key = utils.get_args_raw(message).lower()
        reply = await message.get_reply_message()
        chatid = str(message.chat_id)

        if not key and not reply:
            return await message.edit("Немає аргументів або відповіді.")

        if not key and reply:
            key = reply.raw_text.lower()

        key = self.normalize_text(key)

        if chatid not in filters:
            filters.setdefault(chatid, {})

        if key in filters[chatid]:
            return await message.edit("Такий фільтр вже існує.")

        filters[chatid][key] = True
        self.db.set("Filters", "filters", filters)
        await message.edit(f'Фільтр "{key}" додано.')

    async def stopcmd(self, message):
        """Видаляє фільтр зі списку. Використання: .stop ключ"""
        filters = self.db.get("Filters", "filters", {})
        args = utils.get_args_raw(message)
        chatid = str(message.chat_id)

        if chatid not in filters:
            return await message.edit("У цьому чаті немає фільтрів.")

        if not args:
            return await message.edit("Не вказано ключ фільтру.")

        key = self.normalize_text(args)

        if key not in filters[chatid]:
            return await message.edit(f'Фільтр "{args}" не знайдено.')

        filters[chatid].pop(key)
        self.db.set("Filters", "filters", filters)
        await message.edit(f'Фільтр "{args}"
