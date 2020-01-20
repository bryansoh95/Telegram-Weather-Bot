import json
import requests
import time
import urllib

TOKEN = '<apiKey>'
URL = 'https://api.telegram.org/bot{}/'.format(TOKEN)

def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content

def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js

def get_updates(offset = None):
    url = URL + "getUpdates?timeout=100"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js

def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)

def send_message(text, chat_id, reply_markup = None):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)

def handle_updates(updates):
    for update in updates["result"]:
        texts = update["message"]["text"]
        chat = update["message"]["chat"]["id"]
        api_url = "https://api.openweathermap.org/data/2.5/weather"
        r = requests.post(url = api_url, params = {'q':texts, 'APPID':'<apiKey>', 'units':'metric'})
        if r.status_code == 200:
            response = json.loads(r.content)
            weather = response['weather'][0]['main']
            if weather == 'Clouds':
                weather = 'Cloudy'
            temp = response['main']['temp']
            send_message('For ' + texts + ', the current weather is ' + str(weather) + ' and the temperature is ' + str(temp) + ' degrees celsius.', chat)
        else: 
            send_message('Please enter a valid location.', chat)

def main():
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            handle_updates(updates)
        time.sleep(0.5)

if __name__ == '__main__':
    main()