import time
import random
import aiohttp
import asyncio
import requests
import pycountry
from unidecode import unidecode
from datetime import datetime
from bs4 import BeautifulSoup


async def get_player_data(session, name, url, headers):
    async with session.get(f'{ url }/clubs', headers=headers, timeout=7200) as response:
        resp = await response.text()
        soup = BeautifulSoup(resp, "html.parser")

        dt_elements = soup.find_all("dt", class_="info-header")
        dd_elements = soup.find_all("dd", class_="info-data marginBottom10")

        first_arena_box = soup.find("div", class_="player-experience")
        try:
            arena_name_link = first_arena_box.find("a", class_="arenaName")
            command = arena_name_link.get_text(strip=True) if arena_name_link else ""

            seasons_div = first_arena_box.find("div", class_="seasons")
            seasons = seasons_div.get_text(strip=True)
            seasons_parts = seasons.split(" - ")
            seasons = seasons_parts[-1].replace("/", "/20")
            if seasons == 'still':
                seasons = '2023/2024'

        except AttributeError:
            command = ""
            seasons = ""

        data_dict = {}
        for dt_element, dd_element in zip(dt_elements, dd_elements):
            dt_text = dt_element.get_text(strip=True)
            dd_text = dd_element.get_text(strip=True)
            data_dict[dt_text] = dd_text

        position = data_dict.get("Position") if data_dict.get("Position") is not None else ""
        if position == 'Middle-blocker':
            position = 'Middle blocker'
        birthdate = datetime.strptime(data_dict.get("Birthdate"), "%Y-%m-%d").strftime("%d.%m.%Y") if data_dict.get("Birthdate") is not None else ""
        height = data_dict.get("Height").replace('cm', ' cm') if data_dict.get("Height") is not None else ""
        spike = data_dict.get("Spike").replace('cm', ' cm') if data_dict.get("Spike") is not None else ""
        block = data_dict.get("Block").replace('cm', ' cm') if data_dict.get("Block") is not None else ""
        county_full = data_dict.get("Nationality").split(",")[0] if data_dict.get("Nationality") is not None else ""
        if county_full == 'Europe':
            county = 'EU'
        elif county_full == 'Kazakstan':
            county = 'KAZ'
        elif county_full == 'Cape Verde':
            county = 'CPV'
        elif county_full == 'Chinese Taipei':
            county = 'CHN'
        elif county_full == 'Macau':
            county = 'MAC'
        elif county_full == 'Scotland':
            county = 'GBR'
        elif county_full == 'Palestinian Territory':
            county = 'PSE'
        elif county_full is None or county_full == 'Anonymous Proxy':
            county = ""
        else:
            county = pycountry.countries.search_fuzzy(county_full)[0].alpha_3

        variables = [unidecode(name).replace('@', 'a'), position, command, seasons, county, birthdate, height, spike, block]
        filtered_variables = [var for var in variables]
        filtered_variables.insert(0, "")

        result_string = ",".join(str(var) for var in filtered_variables)

        return result_string


async def main():
    start = time.time()

    headers = {'Cookie': 'uc=RU; _ga=GA1.1.1749305977.1692124618; lang=en; kohanasession=2515a560bd1789afc1ac15240db02afa; _ga_77494GJD4T=GS1.1.1692129318.2.1.1692129319.59.0.0; kohanasession_data=c2Vzc2lvbl9pZHxzOjMyOiIyNTE1YTU2MGJkMTc4OWFmYzFhYzE1MjQwZGIwMmFmYSI7dG90YWxfaGl0c3xpOjI5O19rZl9mbGFzaF98YTowOnt9dXNlcl9hZ2VudHxzOjEwMToiTW96aWxsYS81LjAgKFgxMTsgTGludXggeDg2XzY0KSBBcHBsZVdlYktpdC81MzcuMzYgKEtIVE1MLCBsaWtlIEdlY2tvKSBDaHJvbWUvMTE1LjAuMC4wIFNhZmFyaS81MzcuMzYiO2lwX2FkZHJlc3N8czoxNDoiODkuMTA5LjIwNi4xMDAiO2xhc3RfYWN0aXZpdHl8aToxNjkyMTI5MzE4O29ubGluZV91aWR8czozMjoiZjExNGNjNDY5NGY1ZWRiYmVhMjNkOGI5ZjUwMDNiZmIiO3BsYXllcl9mb3JtX018YToxMjp7czo0OiJuYW1lIjtzOjA6IiI7czo4OiJwb3NpdGlvbiI7czoxOiIwIjtzOjc6ImNvdW50cnkiO3M6MDoiIjtzOjQ6ImhhbmQiO3M6MDoiIjtzOjEwOiJvcmRlclZhbHVlIjtzOjg6ImFkZF9kYXRlIjtzOjE0OiJvcmRlckRpcmVjdGlvbiI7czo0OiJkZXNjIjtzOjEyOiJzaG93X3dhaXRpbmciO3M6MDoiIjtzOjE4OiJvbmx5X3N0YWZmX21lbWJlcnMiO3M6MDoiIjtzOjc6InRhYk5hbWUiO3M6MDoiIjtzOjQ6InBhZ2UiO3M6MToiNiI7czo0OiJzaXplIjtpOjMwO3M6MTI6Im9ubHlfcGxheWVycyI7YjoxO30%3D'}
    url = 'https://volleybox.net/ru/ajax/get_players'
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.content, "html.parser")
    # Находим все элементы с классом "item_box"
    item_elements = soup.find_all('a', class_='item_box')

    # Создаем пустой список для хранения словарей
    result_list = []

    # Обходим каждый элемент
    for item in item_elements:
        name_element = item.find('span', class_='title tooltip_item')
        link_element = item
        name = name_element.get_text()
        url = link_element['href']
        result_list.append({'name': name, 'url': url})

    resp = None
    item_elements = None

    async with aiohttp.ClientSession() as session:
        players_tasks = []
        
        # for x in range(1000):
        #     players_tasks.append(asyncio.ensure_future(get_player_data(session, result_list[x]['name'], result_list[x]['url'], headers)))

        for item in result_list:
            players_tasks.append(asyncio.ensure_future(get_player_data(session, item['name'], item['url'], headers)))

        players_data = await asyncio.gather(*players_tasks)

    with open("data.txt", "w") as file:
        for string in players_data:
            file.write(string + "\n")  # Записываем строку в файл и добавляем символ новой строки
            
    end = time.time()
    print('Время выполнения:', time.strftime("%H:%M:%S", time.gmtime(end - start)))

if __name__ == '__main__':
    asyncio.run(main())
