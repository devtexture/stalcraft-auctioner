import requests, json;

item_URL = 'https://stalcraftdb.net/api/items/{}';
item_lots_URL = item_URL + '/auction-lots?region={}&page={}';
item_history_URL = item_URL + '/auction-history?region={}';

def get_auction_history(item_id: str = None, region: str = "ru"):
    if not item_id or not isinstance(item_id, str):
        raise TypeError('Item ID must be a string')

    url = item_history_URL.format(item_id, region)
    try:
        response = requests.get(url)
        response.raise_for_status()

        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request failed for item {item_id}: {e}")
        return None
    except json.JSONDecodeError:
        print(f"Invalid JSON response for item {item_id}")
        return None

if __name__ == "__main__":
    try:
        history = get_auction_history('zyrm')
        if history:
            print(history)
    except Exception as e:
        print(f"Error: {e}")