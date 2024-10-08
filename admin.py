# Admin Tools for Friendly-Telegram UserBot.
# Copyright (C) 2020 @Fl1yd, @AtiksX.
# Translation to Ukrainian by @Murzetskyy
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# ======================================================================

import io, time
from .. import loader, utils, security
from PIL import Image
from telethon.errors import ChatAdminRequiredError, UserAdminInvalidError, PhotoCropSizeSmallError
from telethon.tl.types import ChatAdminRights, ChatBannedRights
from telethon.tl.functions.channels import EditAdminRequest, EditBannedRequest, EditPhotoRequest
from telethon.tl.functions.messages import EditChatAdminRequest

# ================== КОНСТАНТЫ ========================

DEMOTE_RIGHTS = ChatAdminRights(post_messages=None,
                                add_admins=None,
                                invite_users=None,
                                change_info=None,
                                ban_users=None,
                                delete_messages=None,
                                pin_messages=None,
                                edit_messages=None)

UNMUTE_RIGHTS = ChatBannedRights(until_date=None,
                                 view_messages=None,
                                 send_messages=False,
                                 send_media=False,
                                 send_stickers=False,
                                 send_gifs=False,
                                 send_games=False,
                                 send_inline=False,
                                 embed_links=False)

BANNED_RIGHTS = ChatBannedRights(until_date=None,
                                 view_messages=True,
                                 send_messages=True,
                                 send_media=True,
                                 send_stickers=True,
                                 send_gifs=True,
                                 send_games=True,
                                 send_inline=True,
                                 embed_links=True)

UNBAN_RIGHTS = ChatBannedRights(until_date=None,
                                view_messages=None,
                                send_messages=None,
                                send_media=None,
                                send_stickers=None,
                                send_gifs=None,
                                send_games=None,
                                send_inline=None,
                                embed_links=None)

# =====================================================

@loader.tds
class AdminToolsMod(loader.Module):
    """Администрирование чата"""
    strings = {'name': 'AdminTools',
               'no_reply': '<b>Немає реплаю на картинку/стікер.</b>',
               'not_pic': '<b>Це не картинка/стікер</b>',
               'wait': '<b>Хвилиночку...</b>',
               'pic_so_small': '<b>Картинка занадто маленька, спробуйте іншу.</b>',
               'pic_changed': '<b>Ава чату змінена.</b>',
               'promote_none': '<b>Нікому давати адмінку.</b>',
               'who': '<b>Хто це?</b>',
               'not_admin': '<b>Я адмін тут чи ні?</b>',
               'promoted': '<b>{} отримав адмінку.\nРанг: {}</b>',
               'wtf_is_it': '<b>ЩЗХ?</b>',
               'this_isn`t_a_chat': '<b>Це не чат!</b>',
               'demote_none': '<b>Нікому не треба знімати адмінку.</b>',
               'demoted': '<b>З {} було знято адмінку .</b>',
               'pinning': '<b>Закріплюю...</b>',
               'pin_none': '<b>Реплай на повідомлення для закріплення.</b>',
               'unpinning': '<b>Відкріплюю...</b>',
               'unpin_none': '<b>Нічого відкріпляти.</b>',
               'no_rights': '<b>В мене нема на це прав!b>',
               'pinned': '<b>Закріплено!</b>',
               'unpinned': '<b>Відкріплено!</b>',
               'can`t_kick': '<b>Не можу вигнати користувача.</b>',
               'kicking': '<b>Кик...</b>',
               'kick_none': '<b>Некого кикать.</b>',
               'kicked': '<b>{} кикнутий(-а) з чату.</b>',
               'kicked_for_reason': '<b>{} кикнутий(-а) из чату.\nПричина: {}.</b>',
               'banning': '<b>Бан...</b>',
               'banned': '<b>{} забанений(-а) в чаті.</b>',
               'banned_for_reason': '<b>{} забанений(-а) у чаті.\nПричина: {}</b>', 
               'ban_none': '<b>Нікому показувати банхамер.</b>',
               'unban_none': '<b>Нікого знімати бан.</b>',
               'unbanned': '<b>{} більше не в бані.</b>',
               'mute_none': '<b>Некому давать мут.</b>',
               'muted': '<b>{} теперь в муті на </b>',
               'no_args': '<b>Невірно вказані аргументи.</b>',
               'unmute_none': '<b>Нікого знімати мут.</b>',
               'unmuted': '<b>З {} знято мут.</b>',
               'no_reply': '<b>Нема реплаю.</b>',
               'deleting': '<b>Видалення...</b>',
               'no_args_or_reply':'<b>Нема аргументів або реплая.</b>',
               'deleted': '<b>Всі повідомлення від {} видалені.</b>',
               'del_u_search': '<b>Пошук видаленних аккаунтів...</b>',
               'del_u_kicking': '<b>Кик видаленних аккаунтів...\nОх~, я можу це зробити?!</b>'}


    async def ecpcmd(self, message):
        """Команда .ecp змінює аву чату.\nВикористання: .ecp <реплай на картинку/стікер>."""
        if message.chat:
            try:
                reply = await message.get_reply_message()
                
                chat = await message.get_chat()
                if not chat.admin_rights and not chat.creator:
                    return await utils.answer(message, self.strings('not_admin', message))
                
                if reply:
                    pic = await check_media(message, reply)
                    if not pic:
                        return await utils.answer(message, self.strings('not_pic', message))
                else:
                    return await utils.answer(message, self.strings('no_reply', message))
                
                await utils.answer(message, self.strings('wait', message))
                
                what = resizepic(pic)
                if what:
                    try:
                        await message.client(EditPhotoRequest(message.chat_id, await message.client.upload_file(what)))
                    except PhotoCropSizeSmallError:
                        return await utils.answer(message, self.strings('pic_so_small', message))
                await utils.answer(message, self.strings('pic_changed', message))
            except ChatAdminRequiredError:
                return await utils.answer(message, self.strings('no_rights', message))
        else:
            return await utils.answer(message, self.strings('this_isn`t_a_chat', message))


    async def promotecmd(self, message):
        """Команда .promote дає адмінку.\nВикористання: .promote <@ або реплай> <ранг>."""
        if message.chat:
            try:
                args = utils.get_args_raw(message).split(' ')
                reply = await message.get_reply_message()
                rank = 'одмэн'
                
                chat = await message.get_chat()
                adm_rights = chat.admin_rights 
                if not adm_rights and not chat.creator:
                    return await utils.answer(message, self.strings('not_admin', message))
                
                if reply:
                    args = utils.get_args_raw(message)
                    if args: rank = args
                    else: rank = rank
                    user = await message.client.get_entity(reply.sender_id)
                else:
                    user = await message.client.get_entity(args[0] if not args[0].isnumeric() else int(args[0]))
                    if len(args) == 1:
                        rank = rank
                    elif len(args) >= 2:
                        rank = utils.get_args_raw(message).split(' ', 1)[1]
                try:
                    await message.client(EditAdminRequest(message.chat_id, user.id, ChatAdminRights(add_admins=False, invite_users=adm_rights.invite_users,
                                                                                                    change_info=False, ban_users=adm_rights.ban_users,
                                                                                                    delete_messages=adm_rights.delete_messages, pin_messages=adm_rights.pin_messages), rank))
                except ChatAdminRequiredError:
                    return await utils.answer(message, self.strings('no_rights', message))
                else:
                    return await utils.answer(message, self.strings('promoted', message).format(user.first_name, rank))
            except ValueError:
                return await utils.answer(message, self.strings('no_args', message))
        else:
            return await utils.answer(message, self.strings('this_isn`t_a_chat', message))


    async def demotecmd(self, message):
        """Команда .demote знімає адмінку у користувача.\nВикористання: .demote <@ або реплай>."""
        if not message.is_private:
            try:
                reply = await message.get_reply_message()
                
                chat = await message.get_chat()
                if not chat.admin_rights and not chat.creator:
                    return await utils.answer(message, self.strings('not_admin', message))
                
                if reply:
                    user = await message.client.get_entity(reply.sender_id)
                else:
                    args = utils.get_args_raw(message)
                    if not args:
                        return await utils.answer(message, self.strings('demote_none', message))
                    user = await message.client.get_entity(args if not args.isnumeric() else int(args))
                
                try:
                    if message.is_channel:
                        await message.client(EditAdminRequest(message.chat_id, user.id, DEMOTE_RIGHTS, ""))
                    else:
                        await message.client(EditChatAdminRequest(message.chat_id, user.id, False))
                except ChatAdminRequiredError:
                    return await utils.answer(message, self.strings('no_rights', message))
                else:
                    return await utils.answer(message, self.strings('demoted', message).format(user.first_name))
            except ValueError:
                return await utils.answer(message, self.strings('no_args'))
        else:
            return await utils.answer(message, self.strings('this_isn`t_a_chat', message))


    async def pincmd(self, message):
        """Команда .pin закріплює повідомленя у чаті.\nВикористання: .pin <реплай>."""
        if not message.is_private:
            reply = await message.get_reply_message()
            if not reply:
                return await utils.answer(message, self.strings('pin_none', message))
            
            await utils.answer(message, self.strings('pinning', message))
            try:
                await message.client.pin_message(message.chat, message=reply.id, notify=False)
            except ChatAdminRequiredError:
                return await utils.answer(message, self.strings('no_rights', message))
            await utils.answer(message, self.strings('pinned', message))
        else:
            await utils.answer(message, self.strings('this_isn`t_a_chat', message))


    async def unpincmd(self, message):
        """Команда .unpin открепляет закрепленное сообщение в чате.\nВикористання: .unpin."""
        if not message.is_private:
            await utils.answer(message, self.strings('unpinning', message))
            
            try:
                await message.client.pin_message(message.chat, message=None, notify=None)
            except ChatAdminRequiredError:
                return await utils.answer(message, self.strings('no_rights', message))
            await utils.answer(message, self.strings('unpinned', message))
        else:
            await utils.answer(message, self.strings('this_isn`t_a_chat', message))


    async def kickcmd(self, message):
        """Команда .kick кікає користувача.\nВикористання: .kick <@ або реплай>."""
        if not message.is_private:
            try:
                args = utils.get_args_raw(message).split(' ')
                reason = utils.get_args_raw(message)
                reply = await message.get_reply_message()
                
                chat = await message.get_chat()
                if not chat.admin_rights and not chat.creator:
                    return await utils.answer(message, self.strings('not_admin', message))
                else:
                    if chat.admin_rights.ban_users == False:
                        return await utils.answer(message, self.strings('no_rights', message))
                
                if reply:
                    user = await message.client.get_entity(reply.sender_id)
                    args = utils.get_args_raw(message)
                    if args:
                        reason = args
                else:
                    user = await message.client.get_entity(args[0] if not args[0].isnumeric() else int(args[0]))
                    if args:
                        if len(args) == 1:
                            args = utils.get_args_raw(message)
                            user = await message.client.get_entity(args if not args.isnumeric() else int(args))
                            reason = False
                        elif len(args) >= 2:
                            reason = utils.get_args_raw(message).split(' ', 1)[1]
                
                await utils.answer(message, self.strings('kicking', message))
                try:
                    await message.client.kick_participant(message.chat_id, user.id)
                except UserAdminInvalidError:
                    return await utils.answer(message, self.strings('no_rights', message))
                if not reason:
                    return await utils.answer(message, self.strings('kicked', message).format(user.first_name))
                if reason:
                    return await utils.answer(message, self.strings('kicked_for_reason', message).format(user.first_name, reason))
                
                return await utils.answer(message, self.strings('kicked', message).format(user.first_name))
            except ValueError:
                return await utils.answer(message, self.strings('no_args', message))
        else:
            return await utils.answer(message, self.strings('this_isn`t_a_chat', message))


    async def bancmd(self, message):
        """Команда .ban показує банхамер користувачу.\nВикористання: .ban <@ або реплай>."""
        if not message.is_private:
            try:
                args = utils.get_args_raw(message).split(' ')
                reason = utils.get_args_raw(message)
                reply = await message.get_reply_message()
                
                chat = await message.get_chat()
                if not chat.admin_rights and not chat.creator:
                    return await utils.answer(message, self.strings('not_admin', message))
                else:
                    if chat.admin_rights.ban_users == False:
                        return await utils.answer(message, self.strings('no_rights', message))
                
                if reply:
                    user = await message.client.get_entity(reply.sender_id)
                    args = utils.get_args_raw(message)
                    if args:
                        reason = args
                else:
                    user = await message.client.get_entity(args[0] if not args[0].isnumeric() else int(args[0]))
                    if args:
                        if len(args) == 1:
                            args = utils.get_args_raw(message)
                            user = await message.client.get_entity(args if not args.isnumeric() else int(args))
                            reason = False
                        elif len(args) >= 2:
                            reason = utils.get_args_raw(message).split(' ', 1)[1]
                try:
                    await utils.answer(message, self.strings('banning', message))
                    await message.client(EditBannedRequest(message.chat_id, user.id, ChatBannedRights(until_date=None, view_messages=True)))
                except UserAdminInvalidError:
                    return await utils.answer(message, self.strings('no_rights', message))
                if not reason:
                    return await utils.answer(message, self.strings('banned', message).format(user.first_name))
                if reason:
                    return await utils.answer(message, self.strings('banned_for_reason', message).format(user.first_name, reason))
                return await utils.answer(message, self.strings('banned', message).format(user.first_name))
            except ValueError:
                return await utils.answer(message, self.strings('no_args', message))
        else:
            return await utils.answer(message, self.strings('this_isn`t_a_chat', message))


    async def unbancmd(self, message):
        """Команда .unban для разбану користувача.\nВикористання: .unban <@ або реплай>."""
        if not message.is_private:
            try:
                reply = await message.get_reply_message() 
                
                chat = await message.get_chat()
                if not chat.admin_rights and not chat.creator:
                    return await utils.answer(message, self.strings('not_admin', message))
                else:
                    if chat.admin_rights.ban_users == False:
                        return await utils.answer(message, self.strings('no_rights', message))
                
                if reply:
                    user = await message.client.get_entity(reply.sender_id)
                else:
                    args = utils.get_args_raw(message)
                    if not args:
                        return await utils.answer(message, self.strings('unban_none', message))
                    user = await message.client.get_entity(args if not args.isnumeric() else int(args))
                await message.client(EditBannedRequest(message.chat_id, user.id, ChatBannedRights(until_date=None, view_messages=False)))
                
                return await utils.answer(message, self.strings('unbanned', message).format(user.first_name))
            except ValueError:
                return await utils.answer(message, self.strings('no_args', message))
        else:
            return await utils.answer(message, self.strings('this_isn`t_a_chat', message))


    async def mutecmd(self, message):
        """Команда .mute дає мут користувачу.\nВикористання: .mute <@ або реплай> <час (1m, 1h, 1d)>; нічого."""
        if not message.is_private:
            args = utils.get_args_raw(message).split()
            reply = await message.get_reply_message()
            timee = False

            try:
                if reply:
                        user = await message.client.get_entity(reply.sender_id)
                        args = utils.get_args_raw(message)
                        if args:
                            timee = args
                else:
                    user = await message.client.get_entity(args[0] if not args[0].isnumeric() else int(args[0]))
                    if args:
                        if len(args) == 1:
                            args = utils.get_args_raw(message)
                            user = await message.client.get_entity(args if not args.isnumeric() else int(args))
                            timee = False
                        elif len(args) >= 2:
                            timee = utils.get_args_raw(message).split(' ', 1)[1]
            except ValueError:
                return await utils.answer(message, self.strings('no_args', message))

            if timee:
                n = ''
                t = ''

                for _ in timee:
                    if _.isdigit():
                        n += _
                    else:
                        t += _

                text = f"<b>{n}"

                if t == "m":
                    n = int(n) * 60
                    text += " мин.</b>"
                
                elif t == "h":
                    n = int(n) * 3600
                    text += " час.</b>"

                elif t == "d":
                    n = int(n) * 86400
                    text += " дн.</b>"
                
                else:
                    return await utils.answer(message, self.strings('no_args', message))

                try:
                    tm = ChatBannedRights(until_date=time.time() + int(n), send_messages=True)
                    await message.client(EditBannedRequest(message.chat_id, user.id, tm))
                    return await utils.answer(message, self.strings('muted', message).format(user.first_name) + text)
                except UserAdminInvalidError:
                    return await utils.answer(message, self.strings('no_rights', message))                
            else:
                try:
                    tm = ChatBannedRights(until_date=True, send_messages=True)
                    await message.client(EditBannedRequest(message.chat_id, user.id, tm))
                    return await message.edit('<b>{} отримав мут.</b>'.format(user.first_name))
                except UserAdminInvalidError:
                    return await utils.answer(message, self.strings('no_rights', message))
        else:
            await utils.answer(message, self.strings('this_isn`t_a_chat', message))


    async def unmutecmd(self, message):
        """Команда .unmute для зняття муту у користувача.\nВикористання: .unmute <@ або реплай>."""
        if not message.is_private:
            try:
                reply = await message.get_reply_message() 
                
                chat = await message.get_chat()
                if not chat.admin_rights and not chat.creator:
                    return await utils.answer(message, self.strings('not_admin', message))
                else:
                    if chat.admin_rights.ban_users == False:
                        return await utils.answer(message, self.strings('no_rights', message))
                
                if reply:
                    user = await message.client.get_entity(reply.sender_id)
                else:
                    args = utils.get_args_raw(message)
                    if not args:
                        return await utils.answer(message, self.strings('unmute_none', message))
                    user = await message.client.get_entity(args if not args.isnumeric() else int(args))
                await message.client(EditBannedRequest(message.chat_id, user.id, UNMUTE_RIGHTS))
                
                return await utils.answer(message, self.strings('unmuted', message).format(user.first_name))
            except ValueError:
                return await utils.answer(message, self.strings('no_args', message))
        else:
            return await utils.answer(message, self.strings('this_isn`t_a_chat', message))


    async def delallmsgscmd(self, message):
        """Команда .delallmsgs видаляє усі повідомлення від користувача.\nВикористання: .delallmsgs <@ або реплай>."""
        if not message.is_private:
            chat = await message.get_chat()
            if not chat.admin_rights and not chat.creator:
                return await message.edit("<b>Я не адмін тут.</b>")
            else:
                if chat.admin_rights.delete_messages == False:
                    return await message.edit("<b>У меня нема потрібних прав.</b>")

        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        if not args and not reply:
            return await utils.answer(message, self.strings('no_args_or_reply', message))

        await utils.answer(message, self.strings('deleting', message))

        if args:
            user = await message.client.get_entity(args)
        if reply:
            user = await message.client.get_entity(reply.sender_id)

        await message.client(DeleteUserHistoryRequest(message.to_id, user.id))
        await message.client.send_message(message.to_id, self.strings('deleted', message).format(user.first_name))
        await message.delete() 


    async def deluserscmd(self, message):
        """Команда .delusers показує список видалених акаунтів у чаті.\nВикористання: .delusers <clean>."""
        if message.is_private:
            return await utils.answer(message, self.strings('this_isn`t_a_chat', message))

        con = utils.get_args_raw(message)
        del_u = 0
        del_status = '<b>Нема видалених акаунтів, чат очищено.</b>'

        if con != "clean":
            await utils.answer(message, self.strings('del_u_search', message))
            async for user in message.client.iter_participants(message.chat_id):
                if user.deleted:
                    del_u += 1
            if del_u == 1:
                del_status = f"<b>Знайшов {del_u} видалений акаунт в чаті, для видалення напишіть </b><code>.delusers clean</code><b>.</b>"
            if del_u > 0:
                del_status = f"<b>Знайдено {del_u} видалених акаунтів в чаті, для видалення напишіть </b><code>.delusers clean</code><b>.</b>"
            return await message.edit(del_status)

        chat = await message.get_chat()
        if not chat.admin_rights and not chat.creator:
            return await utils.answer(message, self.strings('not_admin', message))
        else:
            if chat.admin_rights.ban_users == False:
                return await utils.answer(message, self.strings('no_rights', message))

        await utils.answer(message, self.strings('del_u_kicking', message))
        del_u = 0
        del_a = 0
        async for user in message.client.iter_participants(message.chat_id):
            if user.deleted:
                try:
                    await message.client(EditBannedRequest(message.chat_id, user.id, BANNED_RIGHTS))
                except UserAdminInvalidError:
                    del_u -= 1
                    del_a += 1
                await message.client(EditBannedRequest(message.chat_id, user.id, UNBAN_RIGHTS))
                del_u += 1
        if del_u == 1:
            del_status = f"<b>Кікнутий {del_u} видалений акаунт.</b>"
        if del_u > 0:
            del_status = f"<b>Кікнуто {del_u} видалених акаунтів.</b>"

        if del_a == 1:
            del_status = f"<b>Кикнут {del_u} видалений акаунт.\n" \
                            f"{del_a} видалений акаунт адміна не кикнут.</b>"
        if del_a > 0:
            del_status = f"<b>Кикнуто {del_u} видалених акаунтів.\n" \
                            f"{del_a} видалений акаунти адмінів не кикнуты.</b>"
        await message.edit(del_status)


def resizepic(reply):
    im = Image.open(io.BytesIO(reply))
    w, h = im.size
    x = min(w, h)
    x_ = (w-x)//2
    y_ = (h-x)//2
    _x = x_ + x
    _y = y_ + x
    im = im.crop(( x_, y_, _x, _y ))
    out = io.BytesIO()
    out.name = "outsuder.png"
    im.save(out)
    return out.getvalue()

async def check_media(message, reply):
    if reply and reply.media:
        if reply.photo:
            data = reply.photo
        elif reply.video:
            data = reply.video
        elif reply.document:
            if reply.gif or reply.audio or reply.voice:
                return None
            data = reply.media.document
        else:
            return None
    else:
        return None
    if not data or data is None:
        return None
    else:
        data = await message.client.download_file(data, bytes)
        try:
            Image.open(io.BytesIO(data))
            return data
        except:
            return None
