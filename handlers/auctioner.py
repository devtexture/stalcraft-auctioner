from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from objects.items import ItemDatabase;
from pymongo import MongoClient;

import dotenv, io, requests, seaborn, pandas;
import matplotlib.pyplot as plot;

from datetime import datetime;
from pyscx import Server, API
from pyscx.token import Token, TokenType
from PIL import Image, ImageDraw, ImageFont;

env = dotenv.dotenv_values('.env');

app_token = Token(
    value=env["DEMO_TOKEN_APP"],
    type=TokenType.APPLICATION,
)
user_token = Token(
    value=env["DEMO_TOKEN_USER"],
    type=TokenType.USER,
)

api = API(server=Server.DEMO, tokens=[user_token, app_token])

mongo = MongoClient('mongodb://localhost:27017/');
items = ItemDatabase();
items.load_items();

def register_handler(client):
    @client.message_handler(commands=['auction'])
    def command(msg: Message):
        try:
            search_term = msg.text.split()[1];
            results = items.search_items(search_term);

            keyboard = InlineKeyboardMarkup()
            for result in results:
                keyboard.add( InlineKeyboardButton(text=result.name_ru, callback_data=f'auction_{result.item_id}') )

            client.send_message(msg.chat.id, f'Найдено {len(results)} совпадений.', reply_markup=keyboard)
        
        except IndexError:
            client.reply_to(msg, 'а дешевле есть?')
        except Exception as e:
            client.reply_to(msg, f'говна наверни олух: {str(e)}')

    def get_lowest(lots):
        return lots[0].buyout_price;

    def get_mean(history):
        means = [];
        for lot in history:
            price = lot.price;

            if lot.amount > 1:
                price = price / lot.amount;
            
            means.append(price)

        return round(sum(means) / len(means));

    @client.callback_query_handler(func=lambda call: call.data.startswith('auction_'))
    def handle_search(call):
        selected_item = items.get_item( call.data.replace('auction_', '') );
        try:
            auction = api.auction(region='RU');
            item_lots = auction.get_item_lots(selected_item.item_id, order='desc', sort='buyout_price', limit=10);
            item_history = auction.get_item_history(selected_item.item_id);

            print(item_history)

            prices = {
                'Самая низкая на данный момент': get_lowest(item_lots),
                'Средняя цена за 20 продаж': get_mean(item_history),
            }

            try:
                client.delete_message(call.message.chat.id, call.message.message_id)
            except Exception as e:
                print(f'{str(e)}')
                
            image = Image.new('RGB', (1600, 900), color=(20, 18, 16))
            d = ImageDraw.Draw(image)
            try:
                font = ImageFont.truetype('SourceCodePro-Medium.ttf', size=32);
            except:
                font = None  # если не найден

            x, y = 10, 10
            # Рисуем текст
            d.text((x, y), selected_item.name_ru, fill="white", font=font)
                
            response = requests.get(selected_item.get_image())
            item_icon = Image.open(io.BytesIO(response.content)).convert('RGBA')

            y = y + 40
            image.paste(item_icon, (x, y), item_icon)  # Координаты (x, y)
            x = x + item_icon.width + 10;

            for name, price in prices.items():
                d.text((x, y), f'{name}: {price}', fill="white", font=font)
                y = y + 32

            x = x - item_icon.width - 10;
            y = 50 + item_icon.height;

            graph_data = {
                "amount": [lot.amount for lot in item_history],
                "price": [lot.price for lot in item_history],
                "time": [lot.time for lot in item_history],
            }
            df = pandas.DataFrame(graph_data);
            df['hour'] = df['time'].dt.hour

            fig, ax= plot.subplots();
            fig.patch.set_alpha(0);
            seaborn.set_theme(rc={
                "axes.titlecolor": "white",
                "axes.labelcolor": "white",
                "xtick.color": "white",
                "ytick.color": "white",
                "axes.grid": False
            })

            plot.figure(figsize=(12, 6))
            seaborn.lineplot(
                data = df,
                x = "time",
                y = "price",
                marker = "8",
                color = "white",
                linewidth = 2,
                # ax=ax
            )

            plot.title("Динамика цен на аукционе", fontsize=16)
            plot.xlabel("Время", fontsize=12)
            plot.ylabel("Цена", fontsize=12)
            # plot.xticks(rotation=45)

            buffer = io.BytesIO()
            plot.savefig(buffer, format="png", bbox_inches="tight", dpi=100, transparent=True)
            buffer.seek(0)
            plot.close()

            graph = Image.open(buffer).convert('RGBA')
            image.paste(graph, (x, y), graph)


            # Сохраняем в буфер памяти
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)

            client.send_photo(call.message.chat.id, img_byte_arr, caption='окак')

        except Exception as e:
            client.send_message(call.message.chat.id, f'говна наверни олух: {str(e)}') 