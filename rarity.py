import time
from solana.rpc.api import Client
import base64
import asyncio
import aiohttp
import json
import re


class TokenRating:
    def __init__(self):
        self.start_time = time.time()
        self.end_list = []
        self.sol_client = Client("https://api.mainnet-beta.solana.com")

    def nft_projects(self):
        projects_file = json.load(open('test.json', 'r'))
        for project in projects_file:
            config_account_dict = {
                'project_name': 'no_name',
                'project_url': 'no_url',
                'candy machine': project['candy machine'],
                'config': project['config'],
                'items_redeemed': project['items_redeemed'],
                'items_available': project['items_available'],
                'price': project['price'],
                'go_live_date': project['go_live_date'],
                'rarity_tokens': 'no_tokens'}
            self.node_request(config_account_dict)
        with open(f'nft_projects.json', 'w') as outfile:  # запись атрибутов в  json файл
            json.dump(self.end_list, outfile, ensure_ascii=False, indent=4)
        print("--- %s seconds ---" % (time.time() - self.start_time))

    def node_request(self, config_account_dict):
        url_list = []
        response = self.sol_client.get_account_info(config_account_dict['config'], encoding="jsonParsed")
        try:
            decode_data = str(base64.b64decode(response['result']['value']['data'][0]))
        except KeyError:
            if response['error']:
                config_account_dict['error'] = response['error']
                self.end_list.append(config_account_dict)
                print(config_account_dict)
                return

        splitted_data = decode_data.split('https')

        for line in splitted_data:
            source = re.search('://(.+?)/', line)
            if source:
                founded = source.group(0)
                url = re.search(founded + '(.+?)' + r'\\', line)
                if url:
                    url = f'http{url.group(0)[:-1]}'
                    url_list.append(url)
        asyncio.run(self.response_worker(url_list, config_account_dict))

    @staticmethod
    async def url_request(self, session, url):
        async with session.get(url) as resp:
            json_data = await resp.json()
            return json_data

    async def response_worker(self, uri_list, config_account_dict):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for line in uri_list:
                tasks.append(asyncio.ensure_future(self.url_request(self, session=session, url=line)))
            #  получение атрибутов из ссылок
            try:
                request = await asyncio.gather(*tasks)
            except aiohttp.client_exceptions.ClientConnectorError:
                print(f'bad url = {line}')
                self.end_list.append(config_account_dict)
                return
            if not len(request[0]['symbol']) == 0:
                project_name = request[0]['symbol']
                config_account_dict['project_name'] = project_name
            try:
                project_url = request[0]['external_url']
                config_account_dict['project_url'] = project_url
            except KeyError:
                pass
            with open(f'{config_account_dict["project_name"]}.json', 'w') as outfile:  # запись атрибутов в  json файл
                json.dump(request, outfile, ensure_ascii=False, indent=4)
        self.sorting_values_for_types(config_account_dict)

    def sorting_values_for_types(self, config_account_dict):
        project_file = json.load(open(f'{config_account_dict["project_name"]}.json', 'r'))
        attribute_list = []
        for token in project_file:
            # подсчёт повторяющихся атрибутов
            type_list = []
            for attributes in token['attributes']:
                type_list.append(attributes['trait_type'])

        for attribute_type in type_list:
            value_list = []
            for token in project_file:
                for attributes in token['attributes']:
                    if attribute_type == attributes['trait_type']:
                        value_list.append(attributes['value'])
            trait_type_dic = {attribute_type: value_list}
            attribute_list.append(trait_type_dic)

        self.trait_types_doubles(attribute_list, config_account_dict)

    def trait_types_doubles(self, attribute_list, config_account_dict):
        result_dic = {}
        for attributes in attribute_list:
            for items in attributes.items():
                duplicate_attributes = {}
                for value in items[1]:
                    duplicate_attributes[json.dumps(value)] = duplicate_attributes.get(json.dumps(value), 0) + 1
                    duplicate_attributes = {element: count for element, count in duplicate_attributes.items() if
                                            count > 0}
                duplicate_values = {}
                for item in duplicate_attributes.items():
                    duplicate_values[json.loads(item[0])] = item[1]
            result_dic[items[0]] = duplicate_values

        self.rarity_tokens(result_dic, config_account_dict)

    #  @staticmethod
    def rarity_tokens(self, result_dic, config_account_dict):
        proc_dic = {}
        for trait_type in result_dic.items():
            type_count = 0
            dic = {}
            for item in trait_type[1].items():
                type_count = type_count + item[1]
            for item in trait_type[1].items():
                rarity = 100 - (item[1]/type_count)*100
                dic[item[0]] = rarity
                proc_dic[trait_type[0]] = dic
        project_file = json.load(open(f'{config_account_dict["project_name"]}.json', 'r'))
        rarity_tokens = {}
        token_index = 0
        for token in project_file:
            token_index += 1
            lis = []
            attribute_count = len(token['attributes'])
            if not attribute_count == 0:
                for attributes in token['attributes']:
                    for trait_type in proc_dic:
                        if attributes['trait_type'] == trait_type:
                            for key in proc_dic[trait_type]:
                                if attributes['value'] == key:
                                    rarity = proc_dic[trait_type][key]
                                    lis.append(rarity)
                rarity_tokens[str((token['name'], token_index))] = '%.2f' % (sum(lis)/attribute_count)
                sort_keys = sorted(rarity_tokens, key=rarity_tokens.__getitem__, reverse=True)
                sort_rarity_tokens = {}
                for token_name in sort_keys:
                    for key in rarity_tokens:
                        if token_name == key:
                            sort_rarity_tokens[token_name] = rarity_tokens[key]
                top_list = []
                top_rarity_tokens = {}
                for key in sort_rarity_tokens:
                    top_list.append(key)
                if len(top_list) >= 3:
                    top_list = top_list[:3]
                    for line in top_list:
                        for key in sort_rarity_tokens:
                            if line == key:
                                top_rarity_tokens[line] = sort_rarity_tokens[key]
                    config_account_dict['rarity_tokens'] = top_rarity_tokens
                else:
                    config_account_dict['rarity_tokens'] = top_list

        self.end_list.append(config_account_dict)
        print(config_account_dict)


if __name__ == '__main__':
    a = TokenRating()
    a.nft_projects()