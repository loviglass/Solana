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
        except KeyError:
            if response['error']:
                print(f'config: {config_account_dict["config"]} KeyError, response: {response}')
                return
        asyncio.run(self.arweave_request(uri_list, config_account_dict))

    async def main(self, session, url, uri_list, config_account_dict):
        try:
            async with session.get(url) as resp:
                json_data = await resp.json()
                return json_data
        except aiohttp:
            print('aiohttp.client_exceptions.ClientConnectorError, waiting 10s...')
            time.sleep(10)
            asyncio.run(self.arweave_request(uri_list, config_account_dict))

    async def arweave_request(self, uri_list, config_account_dict):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for line in uri_list:
                url = line
                tasks.append(asyncio.ensure_future(self.main(session, url, uri_list, config_account_dict)))
                #  получение атрибутов из 'arweave' ссылок
            request = await asyncio.gather(*tasks)
            try:
                project_name = request[0]['symbol']
                try:
                    project_url = request[0]['external_url']
                except KeyError:
                    print('KeyError')
                    project_url = 'no website'
                config_account_dict['project_name'] = project_name
                config_account_dict['project_url'] = project_url
                with open(f'{project_name}.json', 'w') as outfile:  # запись атрибутов в  json файл
                    json.dump(request, outfile, ensure_ascii=False, indent=4)
            except (TypeError, IndexError):
                print(f'TypeError, data: {request}')
                return
        self.rarity_rating(config_account_dict)

    @staticmethod
    def rarity_rating(config_account_dict):
        end_list = []
        duplicate_attributes = {}
        project_tokens = json.load(open(f'{config_account_dict["project_name"]}.json', 'r'))
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
                    try:
                        attribute_type = json.loads(key)["trait_type"]
                    except KeyError:
                        print('KeyError')
                        attribute_type = json.loads(key)["value"]
                    type_list.append(attribute_type)

                # подсчёт уникальности атрибутов
                rarity_attributes = []
                for attribute_type in set(type_list):
                    for attribute in sorted_attributes.items():
                        try:
                            types = json.loads(attribute[0])['trait_type']
                            value = json.loads(attribute[0])['value']
                            proc = 100 - (attribute[1] / tokens_count) * 100
                            # фильтрование уникальности (не менее 90%)
                            if proc >= 50:
                                if types == attribute_type:
                                    rarity_attributes.append(
                                        {'value': value, 'trait_type': attribute_type, 'rarity': proc})
                                    break
                        except KeyError:
                            value = json.loads(attribute[0])['value']
                            proc = 100 - (attribute[1] / tokens_count) * 100
                            # фильтрование уникальности
                            if proc == 0:
                                if value == attribute_type:
                                    token_dict = {'name': token['name'], 'rarity': 100}
                                    break
            try:
                rarity_tokens.append(token_dict)
            except UnboundLocalError:
                print('UnboundLocalError')
                pass

            # поиск редких атрибутов в списке всех токенов
            for attribute in token['attributes']:
                for line in rarity_attributes:
                    rare_attribute = {"value": line['value'], "trait_type": line['trait_type']}
                    if rare_attribute == attribute:
                        token_dict = {'name': token['name'], 'rarity': line['rarity']}
                        rarity_tokens.append(token_dict)

            #  сортировка токенов по редкости
            rarity_tokens = sorted(rarity_tokens, key=lambda k: k['rarity'])
            if len(rarity_tokens) >= 6:
                rarity_tokens = sorted(rarity_tokens, key=lambda k: k['rarity'])[-3:]
            project_info = {
                'project_name': config_account_dict["project_name"],
                'project_url': config_account_dict["project_url"],
                'candy machine': config_account_dict["candy machine"],
                'config': config_account_dict["config"],
                'items_redeemed': config_account_dict['items_redeemed'],
                'items_available': config_account_dict['items_available'],
                'price': config_account_dict['price'],
                'go_live_date': config_account_dict['go_live_date'][:-1],
                'rarity_tokens': rarity_tokens}
            if tokens_count == 0:
                project_info["rarity_tokens"] = 'no attributes'
            if tokens_count == 1:
                project_info["rarity_tokens"] = token['name']

        end_list.append(project_info)
        with open('nft_projects.json', 'w') as outfile:
            json.dump(end_list, outfile, ensure_ascii=False, indent=4)
        for line in end_list:
            print(line)


if __name__ == '__main__':
    a = TokenRating()
    a.read_config_file()
