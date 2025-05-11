import dotenv, github;
import base64, json;

from dataclasses import dataclass;
from typing import Dict, List, Optional

import concurrent.futures;

token = dotenv.get_key('.env', 'GH_TOKEN')
db_repo = 'EXBO-Studio/stalcraft-database';

def get_content(path):
    g = github.Github(token);
    repo = g.get_repo(db_repo);

    try:
        file = repo.get_contents(f'ru/{path}');

        if path.lower().endswith('.json'):
            return json.loads( base64.b64decode(file.content).decode('utf-8') )
        return file.download_url;
    except Exception as e:
        print(f'ебанное очко {path}: {str(e)}')
        return None;

@dataclass
class Item:
    item_data: str
    item_icon: str
    item_id: str
    name_ru: str
    name_en: str
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Item':

        parts = data['data'].split('/');
        id = parts[-1].split('.')[0];

        return cls(
            item_data=data['data'][1:],
            item_icon=data['icon'][1:],
            item_id=id,
            name_ru=data['name']['lines']['ru'],
            name_en=data['name']['lines']['en']
        )
    
    def get_data(self):
        content = get_content(self.item_data)
        blocks = content['infoBlocks']

        return {
            "id": content['id'],
            "category": content['category'],
            "class": blocks[0]['elements'][0]['value']['lines']['ru'],
        }
    
    def get_image(self):
        return get_content(self.item_icon);

class ItemDatabase:

    def __init__(self):
        self._items: Dict[str, Item] = {}

    def load_items(self, path: str = "listing.json") -> None:
        json = get_content(path);

        if isinstance(json, list):
            for item in json:
                _item = Item.from_dict(item)
                self._items[ _item.item_id ] = _item
        else:
            raise ValueError("Неверный формат данных. Ожидается список предметов.")
        
    def get_item(self, id: str) -> Optional[Item]:
        return self._items.get(id)
    
    def search_items(self, term: str, lang: str = None) -> List[Item]:
        results = [];
        term = term.lower();

        for item in self._items.values():
            if (lang == 'ru' and term in item.name_ru.lower()) or (lang == 'en' and term in item.name_en.lower()) or (term in item.name_ru.lower() or term in item.name_en.lower()):
                results.append(item);

        return results;

if __name__ == "__main__":
    items = ItemDatabase()
    items.load_items()

    item = items.get_item('9mmq');
    print(item.get_data())