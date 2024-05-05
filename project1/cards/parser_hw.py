from requests_html import HTMLSession, HTML
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlsplit
import time
import re
import csv
import os
import random
from abc import ABC, abstractmethod
import json

class Parser(ABC):
    
    def __init__(self, **kwargs):
        self.pages = 2
        self.headers = None
        self.proxies = None
        self.scrolldown = None
        for key, value in kwargs.items(): # Создает атрибуты экземпляра, переданные при создании словарем, 
            setattr(self, key, value)     # переопределяет установленные выше по умолчанию
            
        self.session = HTMLSession(browser_args=["--no-sandbox", "--user-agent='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 YaBrowser/20.9.3.136 Yowser/2.5 Safari/537.36'", "--ignore-certificate-errors", "--headless"])
        self.report = [] # Хранит отчет о собранных данных
        self.make_site_info()



    def make_site_info(self):
        ''' Метод извлекает названиве сайта из полученного URL, 
        используемое для именования файлов и директорий,
        путь до директории, создает директорию'''
        
        split_url = urlsplit(self.url)
        self.site_name = f'{split_url.netloc.replace(".", "_")}'
        self.dir_path = f'{os.path.dirname(__file__)}/data/{self.site_name}/'
        if not os.path.exists(self.dir_path):
            os.makedirs(self.dir_path)
        self.base_url = f"{split_url.scheme}://{split_url.netloc}"
        
    
    def get_data(self):
        url = self.url.format(self.pages)
        self.response = self.session.get(url, headers=self.headers)
        if not self.response.status_code == 200:
            raise ValueError("GET", self.response.status_code)
       
       
    def render_js(self):
        self.response.html.render(wait=random.uniform(2, 4), scrolldown=self.scrolldown)
     
        
    def save_response(self, data):
        with open(f'{self.dir_path}{self.site_name}_{self.pages}.html', "w") as file:
            file.write(data)
            
            
    def save_csv(self, file_name, data):
        with open(f'{self.dir_path}{file_name}.csv', "a", newline='') as file:
            writer = csv.writer(file)
            writer.writerows([[i] for i in data])
            
            
    def save_json(self, data):
        with open(f'{self.dir_path}{self.site_name}.json', "a") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)    
            
    @abstractmethod
    def parse(self):
        pass
    
    @abstractmethod
    def __call__(self):
        pass       
    
    
    
class ProxyParserHTML(Parser):
    '''Парсер сразу выбирает нужных <tbody> по шаблону IP.
    Потом разделяет <tbody> на блоки <tr>, 
    каждый из которых содержит в себе только один IP.
    Далее через регулярные выражение извелекате порт и IP'''
    IP_PATTERN = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
    PORT_PATTERN = r'\b(?<![.])[0-9]{2,5}(?![.])'
    proxy_count_total = 0
    
    def get_data(self):
        super().get_data()
        self.render_js()        
        
    def is_ip(self, text):
        ip = re.search(self.IP_PATTERN, text)
        return ip.group(0) if ip else False   
        
    def parse(self):
        self.proxy_types = {'http': [], 'https': [], 'socks4': [], 'socks5': []}
        tbodys = self.response.html.find("tbody")
        tbody = [i for i in tbodys if self.is_ip(i.text)][-1]
        
        # Проверяет был ли найден блок, содержащий IP
        if tbody:
            tr = tbody.find("tr")
        else:
            print("tbody не найден")
            return
            
        for i in tr:
            ip = self.is_ip(i.text)
            if ip:
                port = re.search(self.PORT_PATTERN, i.text[i.text.index(ip) + len(ip):])
                port = port.group(0) if port else 000000
                
                for pr_type, _ in self.proxy_types.items():
                    if pr_type in i.text.lower():
                        self.proxy_types[pr_type].append(f'{ip}:{port}')
                        
        # Сохранение найденного
        result = []                               
        for file_name, prox in self.proxy_types.items():
            self.save_csv(file_name, prox)
            result.append(f'Получено {file_name} - {len(prox)}')
            ProxyParserHTML.proxy_count_total += len(prox)
        self.report.append(result)


    def __call__(self):
        try:
            for i in range(1, self.pages):
                self.pages = i
                self.get_data()
                if self.is_ip(self.response.html.text): # Проверяет есть ли на странице впринципе IP адрес
                    self.parse()
                    print(f"\033[38;2;255;0;0m\033[48;2;0;0;255m==>> Страница {i} объекта {self.site_name.upper()} обработана успешно.\033[0m")
                    print(self.report[-1], end="\n\n")
                else:
                    if self.report:
                        print(f"\033[92mEnd [Обработка объекта {self.site_name.upper()} завершена успешно]\033[0m\n")
                        [print(*i) for i in self.report]
                    else:
                        print(f'Erro! {self.name} --- данные не получены')                      
                    break
                
        except Exception as e:
            pass
            


class ProxyParserAPI(ProxyParserHTML):
    '''Парсер IP по API'''
    
    # Наследует метод get_data первого родителя, 
    # т.к. второй родитель используе метод render. 
    # Он тут не работает
    def get_data(self): 
        super(ProxyParserHTML, self).get_data()

        
    def parse(self):
        self.proxy_types = {'http': [], 'https': [], 'socks4': [], 'socks5': []}

        for el in self.response.json():
            if el['http'] == '1':
                self.proxy_types['http'].append(f"{el['ip']}:{el['port']}")
                
            if el.get('https') and el['https'] == '1':
                self.proxy_types['https'].append(f"{el['ip']}:{el['port']}")
                
            if el['socks4'] == '1':
                self.proxy_types['socks4'].append(f"{el['ip']}:{el['port']}")
                
            if el['socks5'] == '1':
                self.proxy_types['socks5'].append(f"{el['ip']}:{el['port']}")
                
                
        for file_name, prox in self.proxy_types.items():
            self.save_csv(file_name, prox)
        ProxyParserHTML.proxy_count_total += len(prox)
                                
        


class WildberriesParser(Parser):
    '''Парсит Wildberries только по HTML.
    Медод render модуля requests-html на этом сайте не работает.
    Для исполнения JS используется selenium.
    '''
    
    def get_data(self):
        url = self.url.format(self.pages)
        chrome_options = Options()
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_argument("--headless")
        chrome_options.add_experimental_option("prefs", prefs)
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        time.sleep(4)
        self.response = HTML(html=driver.page_source)
        # with open("/home/jahoroshi4y/Документы/Courses/courses/tms/parsing/requests_html/data/www_wildberries_by_2.html") as file:
        #     html = file.read()
        # self.response = HTML(html=html)
        

    def parse(self):
        self.result = []
        product_card = self.response.find("#route-content .catalog__content .product-snippet")

        for card in product_card:
            try:
                product_list = {}
                product_list["brand"] = card.find(".product-card__brand")[0].text.strip()
                product_list["name"] = card.find(".product-card__name")[0].text.strip()
                product_list["price"] = card.find(".product-card__price .price__lower")[0].text.strip()
                product_list["link"] = f'{self.base_url}{card.find(".product-card__link")[0].attrs["href"]}'
                product_list["image"] = card.find("img")[0].attrs['src']
                self.result.append(product_list)
            except IndexError as e:
                pass
            
        self.report.append(f'[Из  старницы {self.pages} сайта {self.site_name} получено {len(self.result)} позиций.]')

    
    def __call__(self):
        for i in range(1, self.pages):
            self.pages = i
            self.get_data()
            self.save_response(self.response.html)
            self.parse()
            print(self.report[-1], end='\n\n')
        self.save_json(self.result)


def main():
    # Задачи для массового парсинга прокси с применением поиска по регулярным выражениям и HTML
    tasks = [{'url': "https://advanced.name/ru/freeproxy?page={}", 'pages': 10}, 
             {'url': 'https://spys.one/proxies/', 'headers': {'Referer': 'https://spys.one/'}}, 
             {'url': "https://hidemy.io/en/proxy-list/"},
             {'url': "https://geonode.com/free-proxy-list", 'scrolldown': 10},
             {'url': "https://free-proxy-list.net/", 'scrolldown': 10},
             {'url': "https://www.proxynova.com/proxy-server-list/country-cn/"},
             {'url': "https://fineproxy.org/ru/free-proxy/"},
             {'url': "https://www.freeproxy.world/?type=&anonymity=&country=&speed=&port=&page={}", 'pages': 10},
             {'url': "https://vpnoverview.com/privacy/anonymous-browsing/free-proxy-servers/"}]
    
    print("\033[1;33;41m>>== Парсер для прокси запущен ==<<\033[0m", '\n')
    for url in tasks:
        obj = ProxyParserHTML(**url)
        obj()
        
    # Парсинг прокси по API    
    tasks = [{'url': "https://fineproxy.org/wp-content/themes/fineproxyorg/proxy-list.php?0.20522686081524832", 'headers': {'Referer': 'https://fineproxy.org/'}}]
    
    print("\033[1;33;41m>>== Парсер для прокси по API запущен ==<<\033[0m", '\n')
    for url in tasks:
        obj = ProxyParserAPI(**url)
        obj()

    print("\n\033[91mВсего получено прокси\033[0m", f'{ProxyParserHTML.proxy_count_total}', "\n")

    # Парсинг товаров из Wildberries
    tasks = [{'url': 'https://www.wildberries.by/catalog?search=%D0%BA%D0%BB%D0%B0%D0%B2%D0%B8%D0%B0%D1%82%D1%83%D1%80%D0%B0&tail-location=SNT&page={}', 'pages': 4}]
    
    print("\033[1;33;41m>>== Парсер Wieldbirries запущен ==<<\033[0m", '\n')
    for url in tasks:
        obj = WildberriesParser(**url)
        obj()
        
        

if __name__ == "__main__":
    main()