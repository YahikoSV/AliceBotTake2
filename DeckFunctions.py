'''
For getting deck details
'''

import urllib.request
import json
import requests
from bs4 import BeautifulSoup as bs

def createlinkfromcode(deck_code, lang, mode, valid_input = False):
    sv_format = {'R':'3', 'U':'1','T':'2'}
    languages = ['en', 'ja', 'ko', 'zh-tw' , 'fr', 'it', 'de', 'es']
    
    deck_code_url = "https://shadowverse-portal.com/api/v1/deck/import?format=json&deck_code=" + deck_code + "&lang=en"
    with urllib.request.urlopen(deck_code_url) as response:
            source = response.read()            
    deck_json = json.loads(source)
    
    if len(deck_json['data']['errors']) != 0:
        response = "Deck code invalid or does not exist"
    elif mode.upper() not in sv_format:
        response = "Invalid deck format"
    elif lang.lower() not in languages:
        response = "Invalid language"
    else:      
        deck_hash = deck_json['data']['hash']
        #deck_hash = deck_hash.replace("1",str(sv_format[mode.upper()]),1)
        
        deck_list_url = "https://shadowverse-portal.com/deck/" + str(deck_hash) + "?lang=" + str(lang)
        response = deck_list_url
        valid_input = True
    return response, valid_input 


def decklist(link):
    source = requests.get(link).text
    soup = bs(source, 'lxml')
    
    card_name = soup.find_all('span', class_="el-card-list-info-name-text")
    card_qty = soup.find_all('p', class_="el-card-list-info-count")
    card_cost = soup.select('i[class*="icon-cost is-cost-"]')
    card_stats = soup.find_all('a', class_="el-icon-search is-small tooltipify")
    card_atk = [card['data-card-atk'] for card in card_stats]
    card_def = [card['data-card-life'] for card in card_stats]
    card_type = [card['data-card-char-type'] for card in card_stats]
    
    card_info = []
    for card in range (0,len(card_type)):
        if card_type[card] == '1': #follower
            card_info.append(f'{card_cost[card].text}pp {card_atk[card]}/{card_def[card]}')
        elif card_type[card] == '3': #amulet
            card_info.append(f'{card_cost[card].text}pp Amulet')
        elif card_type[card] == '4': #spell
            card_info.append(f'{card_cost[card].text}pp Spell')
    
    card_list = []
    for unique_card in range(0,len(card_name)):

        for copies in range(0,int(card_qty[unique_card].text[1])):
            card_list.append(f'{card_name[unique_card].text} ({card_info[unique_card]})')
    return card_list


def deckdetails(link):
    source = requests.get(link).text
    soup = bs(source, 'lxml')
    
    card_name = soup.find_all('span', class_="el-card-list-info-name-text")
    card_qty = soup.find_all('p', class_="el-card-list-info-count")
    
    card_list = []
    for unique_card in range(0,len(card_name)):
        card_list.append(f'{card_qty[unique_card].text} || {card_name[unique_card].text}')
    return card_list


