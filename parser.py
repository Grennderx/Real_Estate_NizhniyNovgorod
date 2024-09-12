from bs4 import BeautifulSoup
import requests
import re
import time
import ftfy

st_accept = "text/html"
st_useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 YaBrowser/24.6.0.0 Safari/537.36'

headers = {
    "Accept": st_accept,
    "User-Agent": st_useragent
}

features = []  # признаки для квартир
# признаки: кол-во комнат, общая S, S кухни, жилая S, этаж, высота потолков, год постройки дома

# целевая переменная - prices
prices = []

# словарь признаков для правильного распределения в массиве признаков
features_dct = {'Общая площадь': 0, 'Жилая площадь': 1, 'Площадь кухни': 2, 'Этаж': 3, 'Год': 4, 'Дом': 5, 'Отделка': 6}
counter = 1
for i_link in range(1, 40):

    if i_link == 1:
        src = requests.get(
            "https://nn.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_type=flat&region=4885&room1=1&room2=1&room3=1&room4=1",
            headers).text
    else:
        src = requests.get(
            f"https://nn.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_type=flat&p={i_link}&region=4885&room1=1&room2=1&room3=1&room4=1",
            headers).text
    time.sleep(1)

    soup = BeautifulSoup(src, 'lxml')

    # ссылки на все квартиры
    links = soup.find_all(class_="_93444fe79c--link--VtWj6")
    time.sleep(3)

    # вытягиваем признаки для i-той квартиры
    for i in range(len(links)):
        time.sleep(2.5)

        src_feat = requests.get(links[i]['href'], headers).text
        # src_feat = requests.get('https://nn.cian.ru/sale/flat/304771984/', headers).text

        soup2 = BeautifulSoup(src_feat, 'lxml')

        # спарсивание названий характеристик
        feats = soup2.find_all(
            class_="a10a3f92e9--color_gray60_100--mYFjS a10a3f92e9--lineHeight_4u--E1SPG a10a3f92e9--fontWeight_normal--JEG_c a10a3f92e9--fontSize_12px--pY5Xn a10a3f92e9--display_block--KYb25 a10a3f92e9--text--e4SBY a10a3f92e9--text_letterSpacing__0--cQxU5")

        # возможно нужно как-то оптимизировать, пройтись отдельным циклом .replace(u'Год постройки', u'Год').replace(u'Год сдачи', u'Год')
        # !!!!!!

        # while feats is None:
        #     feats = soup2.find_all(
        #         class_="a10a3f92e9--color_gray60_100--mYFjS a10a3f92e9--lineHeight_4u--E1SPG a10a3f92e9--fontWeight_normal--JEG_c a10a3f92e9--fontSize_12px--pY5Xn a10a3f92e9--display_block--KYb25 a10a3f92e9--text--e4SBY a10a3f92e9--text_letterSpacing__0--cQxU5")
        #     time.sleep(0.3)

        feats = [feats[i].text for i in range(len(feats))]

        for f in range(len(feats)):
            if 'Год' in feats[f]:
                feats[f] = 'Год'
        #print(feats)

        # спарсивание цен
        price = soup2.find("div", class_=re.compile("amount--"))
        if price is None:
            prices.append(None)
        else:
            price = int(price.text[:-1].replace(u'\xa0', u''))
            prices.append(price)
        time.sleep(1)

        # спарсивание характеристик
        floor = soup2.find_all(
            class_="a10a3f92e9--color_black_100--Ephi7 a10a3f92e9--lineHeight_6u--cedXD a10a3f92e9--fontWeight_bold--BbhnX a10a3f92e9--fontSize_16px--QNYmt a10a3f92e9--display_block--KYb25 a10a3f92e9--text--e4SBY")

        # на случай неудачного спарсивания
        check = 0
        # while len(floor) == 0 and check < 10:
        #     floor = soup2.find_all(
        #          class_="a10a3f92e9--color_black_100--Ephi7 a10a3f92e9--lineHeight_6u--cedXD a10a3f92e9--fontWeight_bold--BbhnX a10a3f92e9--fontSize_16px--QNYmt a10a3f92e9--display_block--KYb25 a10a3f92e9--text--e4SBY")
        #     check += 1
        #     time.sleep(1)

        # вытягивание текста
        floor = [floor[i].text for i in range(len(floor))]
        #print(floor)

        feats = feats[:len(floor)]
        add_to_features = ['unknown' for _ in range(7)]

        for it in range(len(feats)):
            if feats[it] in features_dct:
                num = features_dct[feats[it]]
                add_to_features[num] = floor[it]

        for it in range(3):
            if add_to_features[it] != 'unknown':
                add_to_features[it] = add_to_features[it][:-2].replace(u'\xa0', u'').replace(u',', u'.')

        if add_to_features[3] != 'unknown':
            add_to_features[3] = add_to_features[3][0]

        if len(add_to_features[4]) != 4:
            for a in floor:
                if len(a) == 4 and ('2' == a[0] or '1' == a[0]):
                    add_to_features[4] = a

        features.append(add_to_features)

        #print(add_to_features)
        # print(f'{links[i]["href"]}  {price} Р   {floor}')
        print(counter)
        counter += 1

import pandas as pd
import numpy as np

df = pd.DataFrame(features)
df.columns = list(features_dct.keys())
df.insert(len(df.columns), 'prices', prices)
print(df)

df.to_csv('nn_cian_2.csv', sep=',', index=False)

# import sqlite3
# connection = sqlite3.connect('database_cian.db')
