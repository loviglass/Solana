import time
from solana.rpc.api import Client
import base64
import asyncio
import aiohttp
import json


class TokenRating:
    def __init__(self):
        self.start_time = time.time()
        self.sol_client = Client("https://api.mainnet-beta.solana.com")
        self.end_list = []

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
                'project_name': None,
                'project_url': None,
                'candy machine': candy_machine,
                'config': config,
                'items_redeemed': items_redeemed,
                'items_available': items_available,
                'price': price,
                'go_live_date': go_live_date,
                'rarity_tokens': None}
            self.node_request(config_account_dict)
        with open(f'nft_projects.json', 'w') as outfile:  # запись атрибутов в  json файл
            json.dump(self.end_list, outfile, ensure_ascii=False, indent=4)
        print("--- %s seconds ---" % (time.time() - self.start_time))

    def node_request(self, config_account_dict):
        uri_list = []
        response = self.sol_client.get_account_info(config_account_dict['config'], encoding="jsonParsed")
        # print(response)
        decode_data = str(base64.b64decode(response['result']['value']['data'][0]))
        line_offset = 0  # смещение отступа
        while True:
            line_offset += 1
            #  извлечение ссылок
            uri = 'https://arweave.net/'.join(decode_data.split('https://arweave.net/')
                                              [line_offset:line_offset + 1])[:43]
            if not uri == '':
                uri_list.append(f'https://arweave.net/{uri}')
            else:
                break
        asyncio.run(self.url_request(uri_list, config_account_dict))

    async def main(self, session, url):
        async with session.get(url) as resp:
            json_data = await resp.json()
            return json_data

    async def url_request(self, uri_list, config_account_dict):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for line in uri_list:
                tasks.append(asyncio.ensure_future(self.main(session=session, url=line)))
            #  получение атрибутов из ссылок
            request = await asyncio.gather(*tasks)
            project_name = request[0]['symbol']
            project_url = request[0]['external_url']
            config_account_dict['project_name'] = project_name
            config_account_dict['project_url'] = project_url
            with open(f'{project_name}.json', 'w') as outfile:  # запись атрибутов в  json файл
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
            if attribute_count == 0:
                return
            for attributes in token['attributes']:
                for trait_type in proc_dic:
                    if attributes['trait_type'] == trait_type:
                        for key in proc_dic[trait_type]:
                            if attributes['value'] == key:
                                rarity = proc_dic[trait_type][key]
                                lis.append(rarity)
            rarity_tokens[f'{token["name"]}(index={token_index})'] = "%.2f" % (sum(lis)/attribute_count)  # '%.2f' %
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
        self.end_list.append(config_account_dict)
        print(config_account_dict)


if __name__ == '__main__':
    a = TokenRating()
    a.read_config_file()