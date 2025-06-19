# -*- coding: utf-8 -*-

# Original module by @ftgmodulesbyfl1yd
# Modified and translated to ukrainian by @Murzetskyy
from .. import loader, utils
import re

@loader.tds
class FiltersMod(loader.Module):
    """Розширений фільтр слів (працює зі зашумленням, пунктуацією та посиланнями)"""

    strings = {"name": "Фільтри"}

    async def client_ready(self, client, db):
        self.db = db

    def normalize_text(self, text):
        """Нормалізує текст: знижує регістр, прибирає пунктуацію, замінює латиницю на кирилицю"""
        replace_map = {
            'а': 'а', 'a': 'а', 'A': 'а',
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
            'и': 'и', 'u': 'и', 'ι': 'и', 'ı': 'и',
            'л': 'л', 'l': 'л', 'L': 'л',
            'г': 'г', 'r': 'г', 'R': 'г',
            'д': 'д', 'ð': 'д',
            'з': 'з', '3': 'з',
            'ч': 'ч', '4': 'ч',
            'ж': 'ж',
            'б': 'б', '6': 'б',
            'я': 'я', 'q': 'я',
        }

        text = text.lower()
        text = re.sub(r"[^\w\s]", "", text)  # прибираємо пунктуацію
        return "".join(replace_map.get(c, c) for c in text)

    async def filtercmd(self, message):
        """Додає фільтр. Використання: .filter слово"""
        filters = self.db.get("Filters", "filters", {})
        key = utils.get_args_raw(message).lower()
        chatid = str(message.chat_id)

        if not key:
            return await message.edit("<b>Немає аргументу.</b>")

        if chatid not in filters:
            filters[chatid] = {}

        if key in filters[chatid]:
            return await message.edit("<b>Такий фільтр вже існує.</b>")

        filters[chatid][key] = True
        self.db.set("Filters", "filters", filters)
        await message.edit(f'<b>Фільтр "{key}" додано.</b>')

    async def stopcmd(self, message):
        """Видаляє фільтр. Використання: .stop слово"""
        filters = self.db.get("Filters", "filters", {})
        args = utils.get_args_raw(message)
        chatid = str(message.chat_id)

        if chatid not in filters or not args:
            return await message.edit("<b>Фільтр відсутній або аргумент не задано.</b>")

        if args in filters[chatid]:
            filters[chatid].pop(args)
            self.db.set("Filters", "filters", filters)
            await message.edit(f'<b>Фільтр "{args}" видалено.</b>')
        else:
            await message.edit(f'<b>Фільтр "{args}" не знайдено.</b>')

    async def stopallcmd(self, message):
        """Видаляє всі фільтри в чаті"""
        filters = self.db.get("Filters", "filters", {})
        chatid = str(message.chat_id)

        if chatid in filters:
            filters.pop(chatid)
            self.db.set("Filters", "filters", filters)
            await message.edit("<b>Усі фільтри видалено.</b>")
        else:
            await message.edit("<b>Фільтрів немає.</b>")

    async def filterscmd(self, message):
        """Показує список фільтрів"""
        filters = self.db.get("Filters", "filters", {})
        chatid = str(message.chat_id)

        if chatid not in filters or not filters[chatid]:
            return await message.edit("<b>Фільтри відсутні.</b>")

        msg = "\n".join([f"• {f}" for f in filters[chatid]])
        await message.edit(f"<b>Фільтри в цьому чаті ({len(filters[chatid])}):\n\n{msg}</b>")

    async def watcher(self, message):
        try:
            filters = self.db.get("Filters", "filters", {})
            chatid = str(message.chat_id)
            if chatid not in filters or not message:
                return

            # Отримання тексту повідомлення
            full_text = message.raw_text or ""
            norm_text = self.normalize_text(full_text)

            # Перевірка тексту в клікабельних посиланнях
            if hasattr(message, "entities") and message.entities:
                for ent in message.entities:
                    if ent.type == "text_link":
                        link_text = full_text[ent.offset: ent.offset + ent.length]
                        norm_text += " " + self.normalize_text(link_text)

            # Перевірка кожного фільтру
            for f in filters[chatid]:
                if self.normalize_text(f) in norm_text:
                    await message.delete()
                    break
        except Exception as e:
            print(f"[FiltersMod] Помилка у watcher: {e}")
