# -*- coding: utf-8 -*-


# Original module author: @ftgmodulesbyfl1yd
# Ukrainian translate by @Murzetskyy


from .. import loader, utils
import re

@loader.tds
class FiltersMod(loader.Module):
    """Фільтрує повідомлення за ключовими словами, навіть якщо в тексті є пунктуація чи латиниця"""

    strings = {"name": "Фільтри"}

    async def client_ready(self, client, db):
        self.db = db

    def normalize_text(self, text):
        """Знижує регістр, прибирає пунктуацію, замінює латиницю на кирилицю"""
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
        text = re.sub(r"[^\w\s]", "", text)  # видалення пунктуації
        return "".join(replace_map.get(c, c) for c in text)

    async def filtercmd(self, message):
        """Додає фільтр. Використання: .filter слово"""
        filters = self.db.get("Filters", "filters", {})
        key = utils.get_args_raw(message).strip().lower()
        chatid = str(message.chat_id)

        if not key:
            return await message.edit("<b>Введи фільтр.</b>")

        if chatid not in filters:
            filters[chatid] = {}

        if key in filters[chatid]:
            return await message.edit("<b>Такий фільтр вже є.</b>")

        filters[chatid][key] = True
        self.db.set("Filters", "filters", filters)
        await message.edit(f'<b>✅ Фільтр "{key}" додано.</b>')

    async def stopcmd(self, message):
        """Видаляє фільтр. Використання: .stop слово"""
        filters = self.db.get("Filters", "filters", {})
        key = utils.get_args_raw(message).strip()
        chatid = str(message.chat_id)

        if chatid not in filters or not key:
            return await message.edit("<b>❌ Немає такого фільтру.</b>")

        if key in filters[chatid]:
            filters[chatid].pop(key)
            self.db.set("Filters", "filters", filters)
            await message.edit(f'<b>🗑 Фільтр "{key}" видалено.</b>')
        else:
            await message.edit(f'<b>❌ Фільтр "{key}" не знайдено.</b>')

    async def stopallcmd(self, message):
        """Видаляє усі фільтри з чату"""
        filters = self.db.get("Filters", "filters", {})
        chatid = str(message.chat_id)

        if chatid in filters:
            filters.pop(chatid)
            self.db.set("Filters", "filters", filters)
            await message.edit("<b>🧹 Усі фільтри видалено.</b>")
        else:
            await message.edit("<b>📭 У цьому чаті немає фільтрів.</b>")

    async def filterscmd(self, message):
        """Показує список фільтрів"""
        filters = self.db.get("Filters", "filters", {})
        chatid = str(message.chat_id)

        if chatid not in filters or not filters[chatid]:
            return await message.edit("<b>📭 Немає фільтрів.</b>")

        msg = "\n".join(f"• {k}" for k in filters[chatid])
        await message.edit(f"<b>📌 Фільтри:\n\n{msg}</b>")

    async def watcher(self, message):
        try:
            filters = self.db.get("Filters", "filters", {})
            chatid = str(message.chat_id)
            if chatid not in filters or not message or not message.raw_text:
                return

            text = self.normalize_text(message.raw_text)

            for f in filters[chatid]:
                norm_f = self.normalize_text(f)
                if norm_f in text:
                    await message.delete()
                    break
        except Exception as e:
            print(f"[FiltersMod] Watcher error: {e}")
