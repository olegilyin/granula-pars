import re

import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as Xml
import datetime


URL = 'https://lex1.ru/shop/'
HOST = 'https://lex1.ru' #URL[:-1]

MAX_PHOTO = 7
MAX_CATALOG_PART = 5
csv_headers = ['id', 'name', 'url', 'price', 'detail', 'folder1', 'folder2', 'article']
for i in range(MAX_PHOTO + 1):
    csv_headers.append('photo_' + str(i))
csv_strings = []

good_number = 1

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/87.0.4280.88 Safari/537.36',
    'accept': '*/*'}


def get_html(url, params=None):
    try:
        r = requests.get(url, headers=HEADERS, params=params)
        return r
    except:
        return ""

def get_html_text(URL):
    html = get_html(URL)
    if html.status_code == 200:
        return html.text
    else:
        return ''


def parse():
    html_text = get_html_text(URL)
    if len(html_text) > 0:
        get_content(html_text)

        dt_str = '_' + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

        file_csv_path = r'M:\Файлы в работе\lex-1_' + dt_str + '.csv'
        with open(file_csv_path, 'w', encoding="utf-8") as file_csv:
            headers_string = ""
            for head in csv_headers:
                headers_string += '"' + head + '";'
            str_csv = headers_string + '\n'
            for string_csv in csv_strings:
                str_csv += string_csv + '\n'
            # str_csv = str_csv.replace('\xbd', '-1/2')\
            #     .replace('\xeb', 'ё')\
            #     .replace('\xe1', 'а')\
            #     .replace('\xd7', 'x')\
            #     .replace('\xb3', '3')\
            #     .replace('\xd8', 'д.')\
            #     .replace('\u01fe', 'o')
            file_csv.write(str_csv)
    else:
        print("Error!")


def get_content(html_text):
    global good_number
    links_of_folder = get_links(html_text)
    for name_1st, names_2nd in links_of_folder.items():
        for name_2nd, link in names_2nd.items():
            get_goods_links(link, name_1st, name_2nd)



def get_goods_links(link, name_1st_folder_level, name_2nd_folder_level):
    global good_number
    html_text = get_html_text(link + '/?offset=10000')
    if html_text != '':
        soup = BeautifulSoup(html_text, 'html.parser')
        goods = soup.findAll('div', class_='itemListProductlex')
        for good in goods:
            a = good.find('a')
            if a:
                href = a.get('href')
                get_good(href, name_1st_folder_level, name_2nd_folder_level)

                good_number += 1


def get_good(link, name_1st_folder_level, name_2nd_folder_level):
    global good_number
    html_text = get_html_text(link)
    if html_text:
        soup = BeautifulSoup(html_text)

        h1 = soup.find('h1', class_='product_title_lex')
        name = h1.getText()
        print(str(good_number) + '.', name, link)

        price_text = ''
        price_tag = soup.find('span', class_='woocommerce-Price-amount amount')
        if price_tag:
            bdi = price_tag.find('bdi')
            if bdi:
                price_text = bdi.getText().replace('\u20bd', '').replace(' ', '')
                print('---', 'price:', price_text)

        attr_dict = {}
        attr_tag = soup.find('div', class_='shop_attributes_lex')
        if attr_tag:
            attribs = attr_tag.findAll('div', class_='lex-attributes')
            for attrib in attribs:
                attr_name_tag = attrib.find('div', class_='lex-attributes-label')
                if attr_name_tag:
                    attr_name = attr_name_tag.getText()
                    attr_value = ''

                    attr_value_tag = attrib.find('div', class_='lex-attributes-value')
                    if attr_value_tag:
                        attr_p = attr_value_tag.find('p')
                        if attr_p:
                            a = attr_p.find('a')
                            if a:
                                attr_value = a.getText()

                    print('--- ---', attr_name + ':', attr_value)
                    attr_dict[attr_name] = attr_value

        art_tag = soup.find('span', class_='sku')
        article = ''
        if art_tag:
            article = art_tag.getText()
            print('--- art', article)

        photos = []
        photo_tags = soup.findAll('div', class_='swiper-slide')
        for photo_tag in photo_tags:
            a = photo_tag.find('a', class_='product-fancybox')
            if a:
                img_tag = a.find('img')
                if img_tag:
                    photo = img_tag.get('src')
                    if photo:
                        print('-- photo --', photo)
                        photos.append(photo)

        descr_tag = soup.find('div', class_='description-product-content')
        descr = ''
        if descr_tag:
            p = descr_tag.find('p')
            if p:
                descr = p.getText()
                print('- descr -', descr)

        add_string_in_csv(name, article,  price_text, descr, link, name_1st_folder_level, name_2nd_folder_level, photos, attr_dict)


def add_string_in_csv(name, article, price, descr, link, name_1st_folder_level, name_2nd_folder_level, photos=[], attr_dict = {}):
    global csv_headers, good_number, csv_strings
    # csv_headers = ['id', 'name', 'url', 'price', 'detail']
    csv_dict = {'id': good_number, 'name': name, 'article': article, 'url': link, 'price': price, 'detail': '"' + descr + '"',
                'folder1': name_1st_folder_level, 'folder2': name_2nd_folder_level
                }

    counter = 1
    for photo in photos:
        if counter > MAX_PHOTO:
            break
        csv_dict['photo_' + str(counter)] = photo
        counter += 1

    for name, value in attr_dict.items():
        if name not in csv_headers:
            csv_headers.append(name)
        csv_dict[name] = value

    csv_strings.append(create_csv_string(csv_dict))


def create_csv_string(csv_dict={}):
    global csv_headers
    csv_string = ''
    for head in csv_headers:
        csv_string += ";" + str(csv_dict.get(head, ''))
    return csv_string.strip(';')

def get_links(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    item_div_folders = soup.findAll('div', class_='wrapper-nav-category-title')
    black_list = ['Новинки техники', 'Подарочный сертификат', 'Техника по акции']
    links = {}
    for item in item_div_folders:
        link = item.find('a')
        if link:
            name = link.get('title')
            if name in black_list:
                continue
            ul = item.findNext('ul')
            sub_folders = {}
            if ul:
                a_tags = ul.findAll('a')
                for a in a_tags:
                    sub_folders[a.getText().strip()] = a.get('href')
            links[name] = sub_folders

    return links


parse()
