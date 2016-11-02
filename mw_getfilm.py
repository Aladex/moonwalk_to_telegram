import requests
from bs4 import BeautifulSoup
import re


NS_URL = "http://moonwalk.cc/sessions/new_session"

def get_moonwalk_m3u(link, site_url):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:46.0) Gecko/20100101 Firefox/46.0',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Accept-Language': 'ru,ru-RU;q=0.8,en-US;q=0.5,en;q=0.3',
               'Accept-Encoding': 'gzip, deflate',
               'Referer': site_url}
    with requests.Session() as s:
        s.headers.update(headers)

        # Находим прямой линк на фильм
        film_url = BeautifulSoup(s.get(link, headers=headers).text,"html.parser").find('iframe').get('src')

        content = s.get(film_url, headers=headers)

        # Находим все данные для запроса прямого m3u

        post_data = {}

        tokens = re.findall('\(session_url, \{([\s\S\d\D]+)\}\)\.success', str(content.text))

        csrf_token = BeautifulSoup(content.text, "html.parser").find('meta', {"name": "csrf-token"})["content"]
        if len(tokens) > 0:
            for token in tokens[0].split(','):
                key = token.strip().split(": ")
                post_data[key[0]] = key[1].replace("'", "")
        post_data["ad_attr"] = 0

        s.headers.update({
            'Host': 'moonwalk.cc',
            'Accept': '*/*',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Data-Pool': 'Stream',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': film_url,
            'Connection': 'keep-alive',
            'X-CSRF-Token': csrf_token
        })

        get_json = s.post(NS_URL, data=post_data).json()
        m3u_link = get_json['mans']['manifest_m3u8']
        direct_links = s.get(m3u_link).text

        return direct_links


def mw_films():
    parsed_list = []
    r = requests.get(url="http://moonwalk.co/film.txt")
    r.encoding = "UTF-8"
    films = r.text.split("\n")
    for film in films:
        row_list = film.strip().split(";")
        if len(row_list) > 5:
            parsed_list.append(dict(zip(('name', 'year', 'kid', 'link', 'translate'),
                           (row_list[0],
                            row_list[1],
                            row_list[2],
                            re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                                       film)[0],
                            row_list[-2])
                           )
                       )
                  )
    return parsed_list
