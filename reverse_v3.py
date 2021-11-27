import time
from solana.rpc.api import Client
import base64
import asyncio
import aiohttp
import json


class TokenRating:
    def __init__(self):
        self.start_time = time.time()
        self.end_list = []
        self.solana_client = Client("https://api.mainnet-beta.solana.com")

    def read_config_file(self):
        projects_file = json.load(open('test.json', 'r'))
        for project in projects_file:
            candy_machine = project['candy machine']
            config = project['config']
            items_redeemed = project['items_redeemed']
            items_available = project['items_available']
            price = project['price']
            go_live_date = project['go_live_date']
            config_account_dict = {
                'project_name': 'project_name',
                'project_url': 'project_url',
                'candy machine': candy_machine,
                'config': config,
                'items_redeemed': items_redeemed,
                'items_available': items_available,
                'price': price,
                'go_live_date': go_live_date,
                'rarity_tokens': 'rarity_tokens'}
            self.node_request(config_account_dict)
        print("--- %s seconds ---" % (time.time() - self.start_time))

    def node_request(self, config_account_dict):
        uri_list = []
        response = self.solana_client.get_account_info(config_account_dict['config'], encoding="jsonParsed")
        decode_data = str(base64.b64decode(response['result']['value']['data'][0]))
        line_offset = 0  # смещение отступа
        while True:
            line_offset += 1
            #  извлечение 'arweave' ссылок
            uri = 'https://arweave.net/'.join(decode_data.split('https://arweave.net/')[line_offset:line_offset + 1])[:43]
            if not uri == '':
                uri_list.append(f'https://arweave.net/{uri}')
            else:
                break
        asyncio.run(self.arweave_request(uri_list, config_account_dict))

    async def main(self, session, url):
        async with session.get(url) as resp:
            json_data = await resp.json()
            return json_data

    async def arweave_request(self, uri_list, config_account_dict):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for line in uri_list:
                url = line
                tasks.append(asyncio.ensure_future(self.main(session, url)))
            #  получение атрибутов из 'arweave' ссылок
            request = await asyncio.gather(*tasks)
            project_name = request[0]['symbol']
            project_url = request[0]['external_url']
            config_account_dict['project_name'] = project_name
            config_account_dict['project_url'] = project_url
            with open(f'{project_name}.json', 'w') as outfile:  # запись атрибутов в  json файл
                json.dump(request, outfile, ensure_ascii=False, indent=4)
        self.rarity_tokens(config_account_dict)

    def rarity_tokens(self, config_account_dict):
        project_file = json.load(open(f'{config_account_dict["project_name"]}.json', 'r'))
        tokens_count = len(project_file)
        dic = {}
        for token in project_file:
            # подсчёт повторяющихся атрибутов
            repeating_attributes = {}
            type_list = []
            for attributes in token['attributes']:
                type_list.append(attributes['trait_type'])
            value_list = []
            for attributes in token['attributes']:
                for trait_type in type_list:
                    if trait_type == attributes['trait_type']:
                        value_list.append(attributes['value'])
        print(type_list)


if __name__ == '__main__':
    a = TokenRating()
    a.read_config_file()
