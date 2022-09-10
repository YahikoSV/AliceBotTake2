# -*- coding: utf-8 -*-
'''
For Adding Starting Data in Sheets
'''
from googleapiclient.discovery import build
from google.oauth2 import service_account

scope = ['https://www.googleapis.com/auth/spreadsheets']
service_account_file = 'keys.json'

creds = None
creds = service_account.Credentials.from_service_account_file(
    service_account_file, scopes=scope)


# The ID and range of a sample spreadsheet.
spreadsheet_id = '1O5p7dS2maCsuEnFQyyF7q65BQeKdNwGdvisAnZK8zig'
service = build('sheets', 'v4', credentials=creds)

# Call the Sheets API
sheet_used = 'Sample'




classIndex = 1
mainLink = 'https://shadowverse-portal.com/cards?'
linkLang = 'lang=ja'
latestCardSetNum = 10024
linkClan = f'clan%5B%5D={classIndex}'
linkCardSets = [f'card_set%5B%5D={str(latestCardSetNum)}'
                ,f'card_set%5B%5D={str(latestCardSetNum - 1)}'
                ,f'card_set%5B%5D={str(latestCardSetNum - 2)}'                
                ,f'card_set%5B%5D={str(latestCardSetNum - 3)}'                
                ]
CardOffset = 0
linkCardSetsKey = "&"
linkCardSetsJoined = linkCardSetsKey.join(linkCardSets) 
fullLink = f'{mainLink}{linkLang}&{linkClan}&{linkCardSetsJoined}'


dict_classes = {
    0 : 'ニュートラル'
    ,1 : 'エルフ'
    ,2 : 'ロイヤル'
    ,3 : 'ウィッチ'
    ,4 : 'ドラゴン'
    ,5 : 'ネクロマンサー'
    ,6 : 'ヴァンパイア'
    ,7 : 'ビショップ'
    ,8 : 'ネメシス'
    }

dict_colors = {
    0 : [120,120,120]
    ,1 : [107,173,83]
    ,2 : [255,188,1]
    ,3 : [45,110,227]
    ,4 : [236,125,14]
    ,5 : [109,82,168]
    ,6 : [194,82,60]
    ,7 : [210,165,40]
    ,8 : [58,138,206]  
    }

dict_rarities = {
     1 : 'ブロンズ'
    ,2 : 'シルバー'
    ,3 : 'ゴールド'
    ,4 : 'レジェンド'
    }

dict_cardList = {
    }




### 1.) Add Sheet and Colors
requestList = []
for index in range(0,len(dict_classes)):
    
    requestSingle = {
      "addSheet": {
        "properties": {
          "title": dict_classes[index],
          "tabColor": {
            "red": dict_colors[index][0]/255,
            "green": dict_colors[index][1]/255,
            "blue": dict_colors[index][2]/255
          }
        }
      }
    }
    
    requestList.append(requestSingle)

batch_update_spreadsheet_request_body = {
    # A list of updates to apply to the spreadsheet.
    # Requests will be applied in the order they are specified.
    # If any request is not valid, no requests will be applied.
    'requests': requestList,  # TODO: Update placeholder value.

    # TODO: Add desired entries to the request body.
}

request = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=batch_update_spreadsheet_request_body)
response = request.execute()






### 2.) Add Headers per Sheet
valueHeaders = [['ナンバー','カード名','レアリティ','カードパック','平均','平均pick枚数']]

dataList = []
for index in range(0,len(dict_classes)):
    
    dataSingle = {
        'range': f'{dict_classes[index]}!A1:F1',
        'values': valueHeaders
    }
    dataList.append(dataSingle)


body = {
    'valueInputOption': "USER_ENTERED",
    'data': dataList,
}
result = service.spreadsheets().values().batchUpdate(
    spreadsheetId=spreadsheet_id, body=body).execute()
print('{0} cells updated.'.format(result.get('totalUpdatedCells')))





### 3.) Compile Card Names
import requests
from bs4 import BeautifulSoup as bs

import pandas as pd
cardTallyList  = pd.DataFrame(columns=['IndexNum', 'CardName'])


def GetT2RarityNum(index,cardRarityNum):
    if index != 0 and cardRarityNum == '4': #Legend, Non-Neutral
        t2RarityNum = 4
    elif index == 0 and cardRarityNum == '4': #Legend Neutral
        t2RarityNum = 4
    elif index != 0 and cardRarityNum == '3': #Gold, Non-Neutral
        t2RarityNum = 4
    elif index != 0 and cardRarityNum == '2': #Silver, Non-Neutral
        t2RarityNum = 3
    elif index != 0 and cardRarityNum == '1': #Bronze, Non-Neutral
        t2RarityNum = 2
    elif index == 0 and cardRarityNum == '3': #Gold, Neutral
        t2RarityNum = 1
    elif index == 0 and cardRarityNum == '2': #Silver, Neutral
        t2RarityNum = 1
    elif index == 0 and cardRarityNum == '1': #Bronze, Neutral
        t2RarityNum = 1  
    else:
        t2RarityNum = 0
    return t2RarityNum

'''
for card in valuesReceived:
    cardIndex = card[0]
    cardName = card[1]
    cardTallyList = cardTallyList.append({
                          'IndexNum' : cardIndex, 
                          'CardName' : cardName},
                         ignore_index = True
                        )
'''
    
for index in range(0,len(dict_classes)):
    print(dict_classes[index])
    classIndex = index
    linkClan = f'clan%5B%5D={classIndex}'
    fullLink = f'{mainLink}{linkLang}&{linkClan}&{linkCardSetsJoined}'

    link = fullLink
    source = requests.get(link).text
    soup = bs(source, 'lxml')
    
    count = 0 
    #cardList = []
    cardList = pd.DataFrame(columns=['CardName', 'CardClass', 'CardRarity', 'Cardt2RarityNum', 'CardSetNum', 'CardRarityNum', 'FlagNeutral'])
    flagIncrementNotMaxed = False
    while flagIncrementNotMaxed == False:
        
        linkCardOffset = '&card_offset=' + str(count) 
        
        link = fullLink + linkCardOffset
        source = requests.get(link).text
        soup = bs(source, 'lxml')
        cardHTML = soup.find_all('a', class_="el-card-detail")
    
        for card in cardHTML:
            
            if card['href'][-9] == '1':   #check if normal card from set release
                cardName = card.find('p', class_="el-card-detail-name").text
                cardClass = dict_classes[index]
                if card['href'][-6] == '0' and card['href'][-5] != '4':  # if nuetral card is not legendary
                    cardRarity = 'ニュートラル'
                else:
                    cardRarity = dict_rarities[int(card['href'][-5])]  #number for rarity/2pick-category code    
                cardSetNum = card['href'][-8:-6]  #number for cardset
                cardt2RarityNum = GetT2RarityNum(index,card['href'][-5])
                #cardList.append(f'{cardName} || {cardRarity} || {cardSetNum}')
                cardRarityNum = card['href'][-5]
                flagNeutral = 1 if cardRarity == 'ニュートラル' else 0
                cardList = cardList.append({
                                          'CardName'   : cardName, 
                                          'CardClass'  : cardClass,
                                          'CardRarity' : cardRarity,
                                          'Cardt2RarityNum' : cardt2RarityNum,
                                          'CardSetNum' : cardSetNum,
                                          'CardRarityNum' : cardRarityNum,
                                          'FlagNeutral' : cardt2RarityNum},
                                          ignore_index = True
                                            )            
            
        count = count + len(cardHTML)
        if len(cardHTML) != 12:
            flagIncrementNotMaxed = True
    
    
    dict_cardList[f'{dict_classes[classIndex]}'] = cardList


import pickle
def save_obj(obj, name):
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)
    
dict_basic = load_obj('BasicCards')



### 4.) Add Card Names
for index in range(1,len(dict_classes)):
    chosenClass = dict_cardList[dict_classes[index]]
    chosenNeutral = dict_cardList[dict_classes[0]]
    chosenBasicTemp = dict_basic[dict_classes[index]]
    chosenBasic = pd.DataFrame(columns=['CardName', 'CardClass', 'CardRarity','Cardt2RarityNum', 'CardSetNum','CardRarityNum', 'FlagNeutral'])
    for card in chosenBasicTemp:
        cardName = card
        cardClass = 'ニュートラル'
        cardRarity = 'ニュートラル'
        cardSetNum = '00'
        cardt2RarityNum = GetT2RarityNum(index,'1')
        cardRarityNum = '1'
        flagNeutral = 1 if cardRarity == 'ニュートラル' else 0
        chosenBasic = chosenBasic.append({
                                  'CardName'   : cardName, 
                                  'CardClass'  : cardClass,
                                  'CardRarity' : cardRarity,
                                  'CardSetNum' : cardSetNum,
                                  'Cardt2RarityNum' : cardt2RarityNum,
                                  'CardRarityNum' : cardRarityNum,
                                  'FlagNeutral' : cardt2RarityNum},
                                  ignore_index = True)

    classList = pd.concat([chosenClass, chosenNeutral, chosenBasic])                                   
    classList = classList.sort_values(['Cardt2RarityNum', 'CardSetNum', 'CardRarityNum' , 'FlagNeutral'], ascending=[False, False, False, False])
    classList = classList.reset_index(drop=True)
    
    values = []
    writeCardNum = 0
    for cardNum in range(0, len(classList)):
        writeCardNum += 1
        values.append([
            str(writeCardNum)
            ,classList['CardName'][cardNum]  #name
            ,classList['CardRarity'][cardNum]  #rarity
            ])
    
      
    data = [
        {
            'range': f'{dict_classes[index]}!A2:C{2+len(values)-1}',
            'values': values
        },
    
    ]
    body = {
        'valueInputOption': "USER_ENTERED",
        'data': data,
    }
    result = service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id, body=body).execute()
    print('{0} cells updated.'.format(result.get('totalUpdatedCells')))


