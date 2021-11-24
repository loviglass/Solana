import time
from solana.rpc.api import Client
import base64
import asyncio
import aiohttp
import json


class TokenRating:
    def __init__(self):
        self.start_time = time.time()   # начальная временная метка
        self.candy_machines = 'test.txt'  # файл с 'candy machine' и 'config' аккаунтами проектов
        self.config_account_dict = {}
        self.config_account_list = []  # список 'config' аккаунтов
        self.uri_list = []  # список 'arweave' ссылок 'config' аккаунта
        self.project_name = None
        self.project_url = None
        self.config_account = None
        self.candy_machine_account = None
        self.items_redeemed = None
        self.items_available = None
        self.price = None
        self.go_live_date = None
        self.rarity_tokens = []
        self.end_list = []

    def read_config_accounts(self):
        projects_file = json.load(open('test.json', 'r'))
        for project in projects_file:
            self.candy_machine_account = project['candy machine']  # 'candy machine'
            self.config_account = project['config']  # 'config' аккаунт
            self.items_redeemed = project['items_redeemed']
            self.items_available = project['items_available']
            self.price = project['price']
            self.go_live_date = project['go_live_date']
            self.config_account_dict = {
                                        'project_name': self.project_name,
                                        'project_url': self.project_url,
                                        'candy machine': self.candy_machine_account,
                                        'config': self.config_account,
                                        'items_redeemed': self.items_redeemed,
                                        'items_available': self.items_available,
                                        'price': self.price,
                                        'go_live_date': self.go_live_date,
                                        'rarity_tokens': self.rarity_tokens
                                        }
            self.config_account_list.append(self.config_account_dict)
        return self.config_account_list

    def config_account_urls(self, config_account_list):
        solana_client = Client("https://api.mainnet-beta.solana.com")
        for config_account in config_account_list:
            response = solana_client.get_account_info(config_account['config'], encoding="jsonParsed")  # получение 'data'
            try:
                data = str(base64.b64decode(response['result']['value']['data'][0]))
                line_offset = 0  # смещение отступа
                while True:
                    line_offset += 1
                    #  извлечение 'arweave' ссылок
                    uri = 'https://arweave.net/'.join(data.split('https://arweave.net/')[line_offset:line_offset + 1])[:43]
                    if not uri == '':
                        self.uri_list.append(f'https://arweave.net/{uri}')
                    else:
                        break
            except (TypeError, KeyError):
                print(f'TypeError/KeyError, response: {response}')
        print(len(self.uri_list))
        return self.uri_list

    @staticmethod
    async def main(session, url):
        try:
            async with session.get(url) as resp:
                json_data = await resp.json()
                return json_data
        except aiohttp.client_exceptions.ClientConnectorError:
            print('aiohttp.client_exceptions.ClientConnectorError')

    async def tokens_for_urls(self, uri_list):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for line in uri_list:
                url = line
                tasks.append(asyncio.ensure_future(self.main(session, url)))  # получение атрибутов из 'arweave' ссылок
                request = await asyncio.gather(*tasks)
                self.project_name = request[0]['symbol']
            with open(f'{self.project_name}_tokens.json', 'w') as outfile:  # запись атрибутов в  json файл
                json.dump(request, outfile, ensure_ascii=False, indent=4)
            print("--- %s seconds ---" % (time.time() - self.start_time))

    def read_project_tokens(self):
        duplicate_attributes = {}
        project_tokens = json.load(open(f'{self.project_name}_tokens.json', 'r'))
        tokens_count = len(project_tokens)

        for token in project_tokens:
            for attribute in token['attributes']:
                # подсчёт повторяющихся атрибутов
                duplicate_attributes[json.dumps(attribute)] = duplicate_attributes.get(json.dumps(attribute), 0) + 1
                duplicate_attributes = {element: count for element, count in duplicate_attributes.items() if count > 0}

            # сортировка атрибутов
            sorted_attributes = {}
            sorted_values = sorted(duplicate_attributes.values())
            for value in sorted_values:
                for attribute in duplicate_attributes.keys():
                    if duplicate_attributes[attribute] == value:
                        sorted_attributes[attribute] = duplicate_attributes[attribute]
                        break

            # определение всех возможных типов атрибутов
            type_list = []
            for key in sorted_attributes:
                attribute_type = json.loads(key)["trait_type"]
                type_list.append(attribute_type)

            # подсчёт уникальности атрибутов
            rarity_attributes = []
            for attribute_type in set(type_list):
                for attribute in sorted_attributes.items():
                    types = json.loads(attribute[0])['trait_type']
                    value = json.loads(attribute[0])['value']
                    proc = 100 - (attribute[1] / tokens_count) * 100
                    # фильтрование уникальности (не менее 90%)
                    if proc >= 90:
                        if types == attribute_type:
                            rarity_attributes.append({'value': value, 'trait_type': attribute_type, 'rarity': proc})
                            break

            # поиск редких атрибутов в списке всех токенов

            self.project_url = token['external_url']
            for attribute in token['attributes']:
                for line in rarity_attributes:
                    rare_attribute = {"value": line['value'], "trait_type": line['trait_type']}
                    if rare_attribute == attribute:
                        self.rarity_tokens.append({'name': token['name'], 'rarity': line['rarity']})

            # сортировка токенов по редкости и вывод топ 3
            self.rarity_tokens = sorted(self.rarity_tokens, key=lambda k: k['rarity'])[-3:]

            project_info = {
                            'project_name': self.project_name,
                            'project_url': self.project_url,
                            'candy machine': self.candy_machine_account,
                            'config': self.config_account,
                            'items_redeemed': self.items_redeemed,
                            'items_available': self.items_available,
                            'price': self.price,
                            'go_live_date': self.go_live_date,
                            'rarity_tokens': self.rarity_tokens
                            }
            self.end_list.append(project_info)

        for project in self.end_list:
            print(project)


if __name__ == '__main__':
    a = TokenRating()
    config_accounts = a.read_config_accounts()
    urls = a.config_account_urls(config_accounts)
    asyncio.run(a.tokens_for_urls(urls))
    a.read_project_tokens()
