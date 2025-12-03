from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from objects.items import ItemDatabase;
from pymongo import MongoClient;

import dotenv, io, requests, seaborn, pandas;
import matplotlib.pyplot as plot;

from datetime import datetime;
from PIL import Image, ImageDraw, ImageFont;

env = dotenv.dotenv_values('.env');

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
            client.reply_to(msg, '?')
        except Exception as e:
            client.reply_to(msg, f'ошибка: {str(e)}')

    @client.callback_query_handler(func=lambda call: call.data.startswith('auction_'))
    def handle_search(call):
        selected_item = items.get_item( call.data.replace('auction_', '') );
        try:
            item_data = selected_item.get_data()
            # auction = api.auction(region='RU');
            # item_lots = auction.get_item_lots(selected_item.item_id, order='desc', sort='buyout_price', limit=10, additional=True);
            # item_history = auction.get_item_history(selected_item.item_id, additional=True);

            # print(item_history)

            try:
                client.delete_message(call.message.chat.id, call.message.message_id)
            except Exception as e:
                print(f'{str(e)}')

        except Exception as e:
            client.send_message(call.message.chat.id, f'ошибка: {str(e)}') 
