import dotenv, telebot, os, importlib;
from glob import glob;
from pathlib import Path;

from telebot import types;
env = dotenv.dotenv_values('.env');

client = telebot.TeleBot( env['TG_TOKEN'] );

def load_handlers( client ):
    handler_files = glob('handlers/*.py', recursive=True);

    for file_path in handler_files:
        module_path = f"handlers.{Path(file_path).stem}"
        try:
            module = importlib.import_module(module_path);
            if hasattr(module, 'register_handler'):
                module.register_handler(client);
                print(f'сколько? пять гривен? а дешевле есть? {module_path}');
        
        except Exception as e:
            print(f'окак {module_path} -> {str(e)}')

if __name__ == '__main__':
    load_handlers( client );
    client.infinity_polling();