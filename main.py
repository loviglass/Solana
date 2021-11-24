# import time
from solana.rpc.api import Client
import base64
import asyncio
import aiohttp
import json


class TokenRating:
    def __init__(self):
        self.end_list = []

    @staticmethod
    def get_config_urls(config):
        uri_list = []
        solana_client = Client("https://api.mainnet-beta.solana.com")
        response = solana_client.get_account_info(config, encoding="jsonParsed")
        try:
            data = str(base64.b64decode(response['result']['value']['data'][0]))
            line_offset = 0  # смещение отступа
            while True:
                line_offset += 1
                #  извлечение 'arweave' ссылок
                uri = 'https://arweave.net/'.join(data.split('https://arweave.net/')[line_offset:line_offset + 1])[:43]
                if not uri == '':
                    uri_list.append(f'https://arweave.net/{uri}')
                else:
                    break
        except (TypeError, KeyError):
            print(f'TypeError/KeyError, response: {response}')
        return uri_list

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
            project_name = request[0]['symbol']
            project_url = request[0]['external_url']
            with open(f'{project_name}_tokens.json', 'w') as outfile:  # запись атрибутов в  json файл
                json.dump(request, outfile, ensure_ascii=False, indent=4)
        self.rarity(project_name, project_url)

    def rarity(self, name, url):
        duplicate_attributes = {}
        project_tokens = json.load(open(f'{name}_tokens.json', 'r'))
        tokens_count = len(project_tokens)
        rarity_tokens = []
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
                for attribute in token['attributes']:
                    for line in rarity_attributes:
                        rare_attribute = {"value": line['value'], "trait_type": line['trait_type']}
                        if rare_attribute == attribute:
                            rarity_tokens.append({'name': token['name'], 'rarity': line['rarity']})

                # сортировка токенов по редкости
                rarity_tokens = sorted(rarity_tokens, key=lambda k: k['rarity'])
                project_info = {
                    'project_name': name,
                    'project_url': url,
                    'candy machine': "candy machine",
                    'config': "config",
                    'items_redeemed': 'items_redeemed',
                    'items_available': 'items_available',
                    'price': 'price',
                    'go_live_date': 'go_live_date'[:-1],
                    'rarity_tokens': 'rarity_tokens'[-3:]
                }
        self.end_list.append(project_info)
        return self.end_list


if __name__ == '__main__':
    a = TokenRating()

    def read_config_accounts():
        projects_file = json.load(open('test.json', 'r'))
        for project in projects_file:
            config_account_dict = {
                                    'project_name': 'project_name',
                                    'project_url': 'project_url',
                                    'candy machine': project['candy machine'],
                                    'config': project['config'],
                                    'items_redeemed': project['items_redeemed'],
                                    'items_available': project['items_available'],
                                    'price': project['price'],
                                    'go_live_date': project['go_live_date'],
                                    'rarity_tokens': 'rarity_tokens'
                                   }
            print(asyncio.run(a.tokens_for_urls(a.get_config_urls(config_account_dict['config']))))


    read_config_accounts()
