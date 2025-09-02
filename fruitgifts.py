def main2():
    import telebot, sqlite3, math
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice
    connection = sqlite3.connect(r"D:\vscode\vs\Fruit Gift\Fruit.db")
    cursor = connection.cursor()


    import threading
    import time
    import logging
    logging.basicConfig(
        level=logging.INFO,   
        format='%(asctime)s | %(levelname)s | %(message)s'
    )

    depcommission = 0.98




    cursor.execute('''CREATE TABLE IF NOT EXISTS Users (
        id INTEGER NOT NULL,
        username TEXT NOT NULL,
        balance INTEGER NOT NULL DEFAULT  0
        )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS Payments (
        id INTEGER NOT NULL,
        username TEXT NOT NULL,
        amount INTEGER NOT NULL,
        receipt TEXT NOT NULL
        )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS Settings (
        id INTEGER NOT NULL,
        maxprice INTEGER NOT NULL DEFAULT 1000,
        minprice INTEGER NOT NULL DEFAULT 100,
        maxsupply INTEGER NOT NULL DEFAULT 50000,
        state INTEGER NOT NULL DEFAULT 0
        )''')
    connection.commit()
    connection.close()

    user_states = {}
    token = ""
    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        try:
            connection = sqlite3.connect(r"D:\vscode\vs\Fruit Gift\Fruit.db")
            cursor = connection.cursor()
            user_id = message.from_user.id
            username = message.from_user.username or "None"
            logging.info(f"Старт от {user_id} | @{username}")
            bot.send_message(-1002812331751, f"Старт от {user_id} | @{username}")
            cursor.execute('SELECT 1 FROM Users WHERE id = ?', (user_id,))
            if not cursor.fetchone():
                cursor.execute('''
                    INSERT INTO Users (id, username, balance) 
                    VALUES (?, ?, ?)
                ''', (user_id, username, 0))
                connection.commit()
            connection.close()

            markup = InlineKeyboardMarkup()
            buybutton = InlineKeyboardButton("Пополнить баланс ⭐️", callback_data="buy_stars")
            giftsettingsbutton = InlineKeyboardButton("⚙️ Настройки автопокупки", callback_data="opensettings")
            profilebutton = InlineKeyboardButton("👤 Профиль", callback_data="openprofile")
            topbutton = InlineKeyboardButton("📊 Топ", callback_data="opentop")
            support_button = InlineKeyboardButton("Поддержка 🥷", url="https://t.me/m/O_p2YjunMGM6")
            channel_button = InlineKeyboardButton("Наш канал", url="https://t.me/Fruit_gift")
            markup.add(buybutton)
            markup.add(profilebutton,topbutton)
            markup.add(giftsettingsbutton)
            markup.add(support_button,channel_button)
            if message.chat.id in [1088445279,1241808217]:
                admin_button = InlineKeyboardButton("✖️Админка✖️", callback_data="openadmin")
                markup.add(admin_button)   
            bot.send_message(
                message.chat.id,
                f"⭐️ Добро пожаловать в бота по автозакупке подарков ⭐️\n\n<blockquote>Бот Может закупать только подарки для которых не требуется премиуми\nТакже в боте есть моментальный возврат звезд</blockquote>",
                reply_markup=markup, parse_mode="HTML"
            )
        except Exception as e:
            logging.error(f"Ошибка {e}")
            
    @bot.callback_query_handler(func=lambda call: call.data == "opensettings")
    def open_settings(call):
        try:
            connection = sqlite3.connect(r"D:\vscode\vs\Fruit Gift\Fruit.db")
            cursor = connection.cursor()
            id = call.from_user.id
            cursor.execute('SELECT 1 FROM Settings WHERE id = ?', (id,))
            if not cursor.fetchone():
                cursor.execute('INSERT INTO Settings (id) VALUES (?)', (id,))
                connection.commit()
            cursor.execute('SELECT id,maxprice,minprice,maxsupply,state FROM Settings WHERE id = ?', (id,))
            settings = cursor.fetchone()
            connection.close()
            markup = InlineKeyboardMarkup()
            switch_button = InlineKeyboardButton(f"{"🟢 Включить" if settings[4] == 0 else "🔴 Выключить"}", callback_data="switchstate")
            minprice_button = InlineKeyboardButton(f"⬇️Лимит МИН цены", callback_data="setminprice")
            maxprice_button = InlineKeyboardButton(f"⬆️Лимит МАКС цены", callback_data="setmaxprice")
            supplylimmit_button = InlineKeyboardButton(f"Лимит саплая 🧸", callback_data="setmaxsupply")
            mainmenubutton = InlineKeyboardButton("◀️ Назад", callback_data="openmain")
            markup.add(switch_button)
            markup.add(minprice_button,maxprice_button)
            markup.add(supplylimmit_button)
            markup.add(mainmenubutton)
            bot.edit_message_text(f"⚙️ Настройки автопокупки\nСтатус: {"🔴 Выключено" if settings[4] == 0 else "🟢 Включено"}\n\nЛимит Цены для покупки:\nОт {settings[2]} до {settings[1]}⭐️\n\n<blockquote>Проверяйте чтобы максимальная цена была меньше минимальной</blockquote>\n\nЛимит саплая: {settings[3]} 🧸", call.from_user.id, call.message.message_id, reply_markup=markup, parse_mode="HTML")
        except Exception as E:
            logging.error(E)

    PRICE_VALUES = [15, 25, 50, 75, 100, 150, 200, 250, 300, 350, 400, 500, 1000, 2000, 2500, 5000, 10000, 20000]
    SUPPLY_VALUES = [1000,2500,5000,10000,20000,40000,50000,100000,200000,500000,750000,1000000]

    @bot.callback_query_handler(func=lambda call: call.data in ["setmaxsupply"])
    def handle_price_setting(call):
        setting_type = "maxsupply"
        markup = supply_selection_markup(setting_type)
        bot.edit_message_text(f"Выберите значение для Максимального саплая 🧸:",
                            call.from_user.id, call.message.message_id, reply_markup=markup)

    def supply_selection_markup(setting_type):
        markup = InlineKeyboardMarkup()
        row = []
        for i, val in enumerate(SUPPLY_VALUES, start=1):
            row.append(InlineKeyboardButton(f"{str(val)}🧸", callback_data=f"setsupp:{setting_type}:{val}"))
            if i % 2 == 0:
                markup.add(*row)
                row = []
        if row:
            markup.add(*row)
        markup.add(InlineKeyboardButton("◀️ Назад", callback_data="opensettings"))
        return markup

    @bot.callback_query_handler(func=lambda call: call.data.startswith("setsupp:"))
    def set_price_value(call):
        try:
            parts = call.data.split(":")
            setting_type = parts[1]
            value = int(parts[2])
            user_id = call.from_user.id

            connection = sqlite3.connect(r"D:\vscode\vs\Fruit Gift\Fruit.db")
            cursor = connection.cursor()
            if setting_type in ["maxsupply"]:
                cursor.execute(f"UPDATE Settings SET {setting_type} = ? WHERE id = ?", (value, user_id))
                connection.commit()

            connection.close()

            open_settings(call)

        except Exception as e:
            logging.error(e)


    def price_selection_markup(setting_type):
        markup = InlineKeyboardMarkup()
        row = []
        for i, val in enumerate(PRICE_VALUES, start=1):
            row.append(InlineKeyboardButton(f"{str(val)}⭐️", callback_data=f"setprice:{setting_type}:{val}"))
            if i % 2 == 0:
                markup.add(*row)
                row = []
        if row:
            markup.add(*row)
        markup.add(InlineKeyboardButton("◀️ Назад", callback_data="opensettings"))
        return markup

    @bot.callback_query_handler(func=lambda call: call.data in ["setminprice", "setmaxprice"])
    def handle_price_setting(call):
        setting_type = "minprice" if call.data == "setminprice" else "maxprice"
        markup = price_selection_markup(setting_type)
        bot.edit_message_text(f"Выберите значение для {'Минимальной' if setting_type == 'minprice' else 'Максимальной'} цены:",
                            call.from_user.id, call.message.message_id, reply_markup=markup)


    @bot.callback_query_handler(func=lambda call: call.data.startswith("setprice:"))
    def set_price_value(call):
        try:
            parts = call.data.split(":")
            setting_type = parts[1]
            value = int(parts[2])
            user_id = call.from_user.id

            connection = sqlite3.connect(r"D:\vscode\vs\Fruit Gift\Fruit.db")
            cursor = connection.cursor()


            if setting_type in ["minprice", "maxprice"]:
                cursor.execute(f"UPDATE Settings SET {setting_type} = ? WHERE id = ?", (value, user_id))
                connection.commit()

            connection.close()

            open_settings(call)

        except Exception as e:
            logging.error(e)



    @bot.callback_query_handler(func=lambda call: call.data == "switchstate")
    def switch_state(call):
        try:
            connection = sqlite3.connect(r"D:\vscode\vs\Fruit Gift\Fruit.db")
            cursor = connection.cursor()
            user_id = call.from_user.id

            cursor.execute('SELECT state FROM Settings WHERE id = ?', (user_id,))
            result = cursor.fetchone()

            if result is not None:
                current_state = result[0]
                new_state = 0 if current_state == 1 else 1

                cursor.execute('UPDATE Settings SET state = ? WHERE id = ?', (new_state, user_id))
                connection.commit()

            connection.close()

            open_settings(call)

        except Exception as e:
            logging.error(e)
        
        
        
        
    @bot.callback_query_handler(func=lambda call: call.data == "opentop")
    def open_top(call):
        try:
            connection = sqlite3.connect(r"D:\vscode\vs\Fruit Gift\Fruit.db")
            cursor = connection.cursor()
            cursor.execute("""
                    SELECT username, balance 
                    FROM Users 
                    WHERE balance > 0 
                    ORDER BY balance DESC 
                    LIMIT 10
                """)
            top_users = cursor.fetchall()
            top_text = "🏆 Топ 10 пользователей по балансу:\n\n"
            for i, (username, balance) in enumerate(top_users, start=1):
                name_display = username if username else "Аноним"
                top_text += f"{i}. {name_display} — ⭐ {balance}\n"
            markup = InlineKeyboardMarkup()
            mainmenubutton = InlineKeyboardButton("◀️ Назад", callback_data="openmain")
            markup.add(mainmenubutton)
            connection.commit()
            connection.close()
        except Exception as E:
            logging.error(E)
        
        
        
        bot.edit_message_text(f"{top_text}", call.from_user.id, call.message.message_id, reply_markup=markup)



    @bot.message_handler(commands=['aref'])
    def zxc(message):
        if message.from_user.id in [1088445279,1241808217]:
            try:
                args = message.text.split()[1:]
                userid = args[0]
                tra = args[1]
                try:
                    bot.refund_star_payment(
                        user_id=userid,
                        telegram_payment_charge_id=tra
                    )
                except:
                    None
            except:
                bot.send_message(message.from_user.id, "/aref id tranz_id")
        else:
            bot.send_message(message.from_user.id, "нет доступа")





    def send_welcome(chat_id):
        markup = InlineKeyboardMarkup()
        buybutton = InlineKeyboardButton("Пополнить баланс ⭐️", callback_data="buy_stars")
        giftsettingsbutton = InlineKeyboardButton("⚙️ Настройки автопокупки", callback_data="opensettings")
        profilebutton = InlineKeyboardButton("👤 Профиль", callback_data="openprofile")
        topbutton = InlineKeyboardButton("📊 Топ", callback_data="opentop")
        support_button = InlineKeyboardButton("Поддержка 🥷", url="https://t.me/m/O_p2YjunMGM6")
        channel_button = InlineKeyboardButton("Наш канал", url="https://t.me/Fruit_gift")
        markup.add(buybutton)
        markup.add(profilebutton,topbutton)
        markup.add(giftsettingsbutton)
        markup.add(support_button,channel_button)
        if chat_id in [1088445279,1241808217]:
            admin_button = InlineKeyboardButton("✖️Админка✖️", callback_data="openadmin")
            markup.add(admin_button)   
        bot.send_message(
            chat_id,
            f"⭐️ Добро пожаловать в бота по автозакупке подарков ⭐️\n\n<blockquote>Бот Может закупать только подарки для которых не требуется премиуми\nТакже в боте есть моментальный возврат звезд</blockquote>",
            reply_markup=markup, parse_mode="HTML"
        )
        
        
    @bot.callback_query_handler(func=lambda call: call.data == "openmain")
    def open_main(call):
        bot.delete_message(call.from_user.id, call.message.message_id)
        markup = InlineKeyboardMarkup()
        buybutton = InlineKeyboardButton("Пополнить баланс ⭐️", callback_data="buy_stars")
        giftsettingsbutton = InlineKeyboardButton("⚙️ Настройки автопокупки", callback_data="opensettings")
        profilebutton = InlineKeyboardButton("👤 Профиль", callback_data="openprofile")
        topbutton = InlineKeyboardButton("📊 Топ", callback_data="opentop")
        support_button = InlineKeyboardButton("Поддержка 🥷", url="https://t.me/m/O_p2YjunMGM6")
        channel_button = InlineKeyboardButton("Наш канал", url="https://t.me/Fruit_gift")
        markup.add(buybutton)
        markup.add(profilebutton,topbutton)
        markup.add(giftsettingsbutton)
        markup.add(support_button,channel_button)
        if call.from_user.id in [1088445279,1241808217]:
            admin_button = InlineKeyboardButton("✖️Админка✖️", callback_data="openadmin")
            markup.add(admin_button)                                    
        bot.send_message(
            call.from_user.id,
            f"⭐️ Добро пожаловать в бота по автозакупке подарков ⭐️\n\n<blockquote>Бот Может закупать только подарки для которых не требуется премиуми\nТакже в боте есть моментальный возврат звезд</blockquote>",
            reply_markup=markup, parse_mode="HTML"
        )

    @bot.callback_query_handler(func=lambda call: call.data == "openadmin")
    def open_admin_panel(call):
        try:
            markup = InlineKeyboardMarkup()
            connection = sqlite3.connect(r"D:\vscode\vs\Fruit Gift\Fruit.db")
            cursor = connection.cursor()
            cursor.execute("SELECT SUM(balance) FROM Users")
            balance = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) from Users")
            users = cursor.fetchone()[0]
            mainmenubutton = InlineKeyboardButton("◀️ Назад", callback_data="openmain")
            refresh = InlineKeyboardButton("🔄 Обновить", callback_data="openadmin")
            markup.add(refresh)
            markup.add(mainmenubutton)
            try:
                bot.edit_message_text(f"```AdminPanel В разработке```\n\n`Общий баланс бота с пополнений:` {balance}⭐️\n\n`Общее количество пользователей:` {users}👥", call.from_user.id, call.message.message_id,reply_markup=markup,parse_mode="MarkDown")
            except:
                bot.answer_callback_query(call.id, "Ничего не изменилось")
        except Exception as E:
            logging.error(E)
    
    
    @bot.callback_query_handler(func=lambda call: call.data == "buy_stars")
    def ask_star_amount(call):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        markup = InlineKeyboardMarkup()
        link_button = InlineKeyboardButton("Купить звезды дешево 🌐", url="https://split.tg/?ref=UQCoEMuX_hT06LMPBuGzIIwhBxRGbUYdRZUXEqmhofPMrZQD")
        markup.add(link_button)
        mainmenubutton = InlineKeyboardButton("◀️ Назад", callback_data="openmain")
        markup.add(mainmenubutton)
        bot.send_message(call.message.chat.id, f"Сколько звёзд вы хотите пополнить? (целое число, минимум 25)\nКомиссия на пополнение 2%\nНет звезд? Купить их можно по кнопке ниже", reply_markup=markup)
        user_states[call.from_user.id] = 'waiting_for_star_amount'

    @bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "waiting_for_star_amount")
    def process_star_amount(message):
        try:
            count = int(message.text.strip())
            if count < 25 or count > 10000:
                raise ValueError
            else:
                user_states.pop(message.from_user.id, None)
                amount_in_units = count
                bot.send_invoice(
                    chat_id=message.chat.id,
                    title="Пополнение баланса",
                    description=f"Пополнение баланса на {count}⭐️",
                    invoice_payload=f"stars_{count}_{message.from_user.id}",
                    provider_token=None,
                    currency="XTR",
                    prices=[LabeledPrice(label=f"{count} звёзд", amount=amount_in_units)],
                    start_parameter="stars_payment",
                    need_phone_number=False,
                    need_email=False,
                    need_shipping_address=False,
                    is_flexible=False,
                )
        except ValueError:
            bot.send_message(message.chat.id, "Введите корректное целое число от 25 и до 10к.")
            return
    @bot.callback_query_handler(func=lambda call: call.data == "open_refund")
    def open_refund(call):
        connection = sqlite3.connect(r"D:\vscode\vs\Fruit Gift\Fruit.db")
        cursor = connection.cursor()
        id = call.from_user.id
        cursor.execute('SELECT amount,receipt FROM Payments WHERE id = ?', (id,))
        receipts = cursor.fetchall()
        markup = InlineKeyboardMarkup()
        receiptnum = 1
        for receipt in receipts:
            button = InlineKeyboardButton(f"{receipt[0]}⭐️ id: {receipt[1][:10]}", callback_data=f"refund_pay:{receipt[1][:10]}")
            markup.add(button)
        mainmenubutton = InlineKeyboardButton("◀️ Назад", callback_data="openprofile")
        markup.add(mainmenubutton)
        bot.edit_message_text(f"Для возврата звезд нужно оплатить 2% комиссию, бот вернет полную сумму пополения", call.from_user.id, call.message.message_id, reply_markup=markup)
        connection.commit()
        connection.close()
            
    @bot.callback_query_handler(func=lambda call: call.data.startswith("refund_pay:"))
    def handle_refund_payment(call):
        bot.delete_message(call.message.chat.id,call.message.message_id)
        short_id = call.data.split(":")[1]
        
        connection = sqlite3.connect(r"D:\vscode\vs\Fruit Gift\Fruit.db")
        cursor = connection.cursor()
        
        cursor.execute("SELECT amount, receipt FROM Payments WHERE receipt LIKE ?", (f"{short_id}%",))
        result = cursor.fetchone()
        if not result:
            bot.answer_callback_query(call.id, "Ошибка: чек не найден.")
            return
        
        amount, receipt = result
        commission_amount = int(amount * (1 - depcommission)) if int(amount * (1 - depcommission)) > 1 else 1

        bot.send_invoice(
            chat_id=call.message.chat.id,
            title="Возврат средств",
            description=f"Комиссия за возврат {amount}⭐️",
            invoice_payload=f"refund_{receipt}_{call.from_user.id}",
            provider_token=None,
            currency="XTR",
            prices=[LabeledPrice(label="Комиссия 2%", amount=commission_amount)],
            start_parameter="refund_commission",
            need_phone_number=False,
            need_email=False,
            need_shipping_address=False,
            is_flexible=False,
        )
        connection.commit()
        connection.close()

    @bot.pre_checkout_query_handler(func=lambda query: True)
    def checkout(pre_checkout_query):
        bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
            

    @bot.callback_query_handler(func=lambda call: call.data == "openprofile")
    def open_profile(call):
        connection = sqlite3.connect(r"D:\vscode\vs\Fruit Gift\Fruit.db")
        cursor = connection.cursor()
        id = call.from_user.id
        cursor.execute('SELECT balance FROM Users WHERE id = ?', (id,))
        userbalance = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM Payments WHERE id = ?', (id,))
        userdeps = cursor.fetchone()[0]
        
        markup = InlineKeyboardMarkup()
        refundbutton = InlineKeyboardButton("🔄 Возврат звёзд", callback_data="open_refund")
        mainmenubutton = InlineKeyboardButton("◀️ Назад", callback_data="openmain")
        markup.add(refundbutton)
        markup.add(mainmenubutton)
        bot.edit_message_text(f"Профиль {f"@{call.from_user.username}" if call.from_user.username else call.from_user.id}\nБаланс - {userbalance}  ⭐️\nАктивных пополнений - {userdeps}", call.from_user.id, call.message.message_id, reply_markup=markup)
        connection.commit()
        connection.close()
        
        
        
        
    @bot.callback_query_handler(func=lambda call: call.data == "ref_stars")
    def ref_stars(call):
        connection = sqlite3.connect(r"D:\vscode\vs\Fruit Gift\Fruit.db")
        cursor = connection.cursor()
        id = call.from_user.id
        cursor.execute('SELECT amount, receipt FROM Payments WHERE id = ?', (id,))
        result = cursor.fetchall()
        for res in result:
            bot.refund_star_payment(
                user_id=call.message.chat.id,
                telegram_payment_charge_id=res[1]
            )
            cursor.execute('DELETE FROM Payments WHERE receipt = ?', (res[1],))
            cursor.execute('''UPDATE Users SET balance = balance - ? WHERE id = ?''', (int(res[0] * depcommission),id))
        connection.commit()
        connection.close()
        




    @bot.pre_checkout_query_handler(func=lambda query: True)
    def process_pre_checkout(pre_checkout_query):
        try:
            bot.answer_pre_checkout_query(
                pre_checkout_query.id,
                ok=True,
                error_message="Произошла ошибка при обработке платежа"
            )
        except Exception as e:
            logging.error(f"Pre-checkout error: {e}")

    @bot.message_handler(content_types=['successful_payment'])
    def handle_successful_payment(message):
        payload = message.successful_payment.invoice_payload
        user_id = message.from_user.id
        amount = message.successful_payment.total_amount
        tranzid = message.successful_payment.telegram_payment_charge_id
        username = message.from_user.username or "None"

        connection = sqlite3.connect(r"D:\vscode\vs\Fruit Gift\Fruit.db")
        cursor = connection.cursor()

        if payload.startswith("refund_"):
            parts = payload.split("_")
            if len(parts) < 3:
                bot.send_message(message.chat.id, "Ошибка: неверный формат payload.")
                return

            receipt_id = "_".join(parts[1:-1])
            user_id_from_payload = parts[-1]

            try:
                cursor.execute('SELECT amount FROM Payments WHERE receipt = ?', (receipt_id,))
                row = cursor.fetchone()
                if row:
                    refund_amount = row[0]

                    bot.refund_star_payment(user_id=user_id, telegram_payment_charge_id=receipt_id)

                    cursor.execute('DELETE FROM Payments WHERE receipt = ?', (receipt_id,))
                    cursor.execute('''UPDATE Users SET balance = balance - ? WHERE id = ?''', (int(refund_amount * depcommission), user_id))
                    bot.send_message(message.chat.id, "✅ Звёзды успешно возвращены!")
                    send_welcome(user_id)
                    logging.info(f"Возврат {refund_amount} ⭐️ для {user_id} | чек: {receipt_id}")
                    bot.send_message(-1002812331751, f"Возврат {refund_amount} ⭐️ для {user_id} | чек: {receipt_id}")
                else:
                    bot.send_message(message.chat.id, "Ошибка: запись не найдена.")
            except Exception as e:
                bot.send_message(message.chat.id, f"Ошибка при возврате: {str(e)}")
        else:
            try:
                cursor.execute('''INSERT INTO Payments (id, username, amount, receipt) VALUES (?, ?, ?, ?)''',(user_id, username, amount, tranzid))
                cursor.execute('''UPDATE Users SET balance = balance + ? WHERE id = ?''', (int(amount * depcommission), user_id))
                bot.send_message(message.chat.id, f"✅ Платеж на {amount}⭐️ успешно получен!")
                send_welcome(user_id)
                logging.info(f"Пополнение {amount} ⭐️ от {user_id} | @{username} | чек: {tranzid}")
                bot.send_message(-1002812331751, f"Пополнение {amount} ⭐️ от {user_id} | @{username} | чек: {tranzid}")
            except Exception as e:
                bot.send_message(message.chat.id, f"Ошибка обработки платежа: {str(e)}")

        connection.commit()
        connection.close()

    import threading
    import time
    import sqlite3
    import logging
    import requests

    _processed_gifts = set()

    def safe_request(func, *args, retries=3, delay=3, **kwargs):
        for attempt in range(retries):
            try:
                return func(*args, **kwargs)
            except requests.exceptions.RequestException as e:
                logging.warning(f"[safe_request] Ошибка сети: {e} (попытка {attempt + 1}/{retries})")
                time.sleep(delay)
        raise Exception("Не удалось выполнить запрос после нескольких попыток")

    def gift_worker():
        logging.info("✨ Gift worker запущен")
        while True:
            try:
                available = safe_request(bot.get_available_gifts)
                new_gifts = [g for g in available.gifts if g.id not in _processed_gifts and g.total_count is not None]
                if not new_gifts:
                    time.sleep(5)
                    continue

                new_gifts.sort(key=lambda g: g.star_count, reverse=True)
                for gift in new_gifts:
                    _processed_gifts.add(gift.id)
                    logging.info(f"Новый gift {gift.id}: price={gift.star_count}, supply={gift.total_count}")

                bot_stars = safe_request(bot.get_my_star_balance).amount
                min_price = min(g.star_count for g in new_gifts)

                with sqlite3.connect(r"D:\vscode\vs\Fruit Gift\Fruit.db") as conn:
                    cur = conn.cursor()
                    cur.execute("""
                        SELECT U.id, U.balance, S.minprice, S.maxprice, S.maxsupply
                        FROM Users U
                        JOIN Settings S ON U.id = S.id
                        WHERE S.state = 1 AND U.balance >= ?
                        ORDER BY U.balance DESC
                    """, (min_price,))
                    users = cur.fetchall()

                for user_id, balance, minp, maxp, maxs in users:
                    logging.info(f"→ Пользователь {user_id}: balance={balance}, range=[{minp}…{maxp}], maxsupply={maxs}")
                    user_gifts = [g for g in new_gifts if minp <= g.star_count <= maxp and g.total_count <= maxs]
                    if not user_gifts:
                        continue

                    with sqlite3.connect(r"D:\vscode\vs\Fruit Gift\Fruit.db") as conn:
                        cur = conn.cursor()
                        cur.execute("SELECT balance FROM Users WHERE id = ?", (user_id,))
                        balance = cur.fetchone()[0]

                        for gift in user_gifts:
                            max_by_user = balance // gift.star_count
                            max_by_supply = gift.total_count
                            max_count = min(max_by_user, max_by_supply, bot_stars // gift.star_count)

                            if max_count <= 0:
                                continue

                            logging.info(f"   — отправляем {max_count}×gift({gift.id}) пользователю {user_id}")
                            for _ in range(max_count):
                                try:
                                    safe_request(bot.send_gift, user_id=user_id, gift_id=gift.id, pay_for_upgrade=False)
                                except Exception as e:
                                    logging.exception(f"Ошибка send_gift: user={user_id}, gift={gift.id}")
                                else:
                                    balance -= gift.star_count
                                    bot_stars -= gift.star_count
                                    gift.total_count -= 1
                                    cur.execute("UPDATE Users SET balance = ? WHERE id = ?", (balance, user_id))
                                    conn.commit()

                            if balance < min_price or bot_stars < min_price:
                                break

            except Exception:
                logging.exception("‼ Ошибка в gift_worker")

            time.sleep(5)
    
    
    def run_gift_worker_forever():
        while True:
            try:
                gift_worker()
            except Exception:
                logging.exception("💥 gift_worker упал, перезапуск через 5 сек")
                time.sleep(5)

    def start_worker():
        threading.Thread(target=run_gift_worker_forever, daemon=True).start()

    start_worker()
    
    
    

    @bot.callback_query_handler(func=lambda call: True)
    def handle_errors(call):
        bot.answer_callback_query(call.id, "Бот еще в разработке, ждите обновлений.")
    if __name__ == '__main__':
        logging.info("Бот запущен...")
        bot.polling(none_stop=True)
while True:
    try:
        main2()
    except:

        main2()
