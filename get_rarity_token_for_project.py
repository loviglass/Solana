import time
import json
import base64
import aiohttp
import asyncio


class TokenRating:
    def __init__(self):
        self.start_time = time.time()
        self.start_file = 'test.txt'
        self.config_account_list = []
        self.uri_list = []
        self.trait_list = []
        self.trait_dic = {}
        self.json_dump = 'config_account_dump.json'
        self.request_list = []

    def read_file(self):
        print(f'reading a "{self.start_file}"')
        file = open(self.start_file, "r")
        for line in file.readlines():
            config_account = 'config'.join(line.split('items_redeemed')[:1])[-45:][:-1]
            self.config_account_list.append(config_account)
            break
        print(f'found {len(self.config_account_list)} accounts')

    async def getting_attribute_links(self):
        print('getting account links')
        async with aiohttp.ClientSession(json_serialize=json.dumps) as session:
            for line in self.config_account_list:
                url = 'https://api.mainnet-beta.solana.com'
                payload = {"jsonrpc": "2.0", "id": 1, "method": "getAccountInfo", "params": [line, {"encoding": "jsonParsed"}]}
                async with session.post(url, json=payload) as resp:
                    response = await resp.json()
                    data = response['result']['value']['data'][0]
                    data = str(base64.b64decode(data))
                    index = 0
                    while True:
                        index += 1
                        uri = 'https://arweave.net/'.join(data.split('https://arweave.net/')[index:index + 1])[:43]
                        if not uri == '':
                            self.uri_list.append(f'https://arweave.net/{uri}')
                        else:
                            break

    async def main(self, session, url):
        async with session.get(url) as resp:
            json_data = await resp.json()
            return json_data

    async def get_attributes(self):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for line in self.uri_list:
                url = line
                tasks.append(asyncio.ensure_future(self.main(session, url)))
            request = await asyncio.gather(*tasks)
            for line in request:
                self.request_list.append(line)
            with open(f'dump {line["symbol"]}.json', 'w') as outfile:
                json.dump(self.request_list, outfile, ensure_ascii=False, indent=4)

    def rarity(self):
        compare_dict = {}
        type_dict = {}
        type_list = []
        sorted_dict = {}
        rarity_tokens = []
        rarity_list = []
        for line in self.request_list:
            project = line['symbol']
        print(f'Project: {project}')
        json_file = open(f'dump {project}.json', 'r')
        json_file = json.load(json_file)
        count = len(json_file)
        for token_info in json_file:
            for attributes in token_info['attributes']:
                type_dict[attributes['trait_type']] = None
                compare_dict[json.dumps(attributes)] = compare_dict.get(json.dumps(attributes), 0) + 1
                doubles = {element: count for element, count in compare_dict.items() if count > 0}

        sorted_values = sorted(doubles.values())
        for i in sorted_values:
            for k in doubles.keys():
                if doubles[k] == i:
                    sorted_dict[k] = doubles[k]
                    break

        for key in sorted_dict:
            key = json.loads(key)
            type_list.append(key["trait_type"])

        for types in set(type_list):
            for elem in sorted_dict.items():
                type = json.loads(elem[0])['trait_type']
                value = json.loads(elem[0])['value']
                proc = (elem[1] / count) * 100
                if proc <= 4:
                    if types == type:
                        rarity_attributes = {'value': value, 'trait_type': type, 'rarity': proc}
                        rarity_list.append(rarity_attributes)
                        break

        json_file = open(f'dump {project}.json', 'r')
        for token_info in json.load(json_file):
            for attribute in token_info['attributes']:
                for line in rarity_list:
                    atr = {"value": line['value'], "trait_type": line['trait_type']}
                    if attribute == atr:
                        rarity_tokens.append({token_info['name']: line['rarity']})

        for line in rarity_tokens:
            print(line)

        print(f'найдено {count} токенов')
        print(f'{len(rarity_tokens)} редких токенов')
        print("--- %s seconds ---" % (time.time() - self.start_time))


if __name__ == '__main__':
    a = TokenRating()
    a.read_file()
    asyncio.run(a.getting_attribute_links())
    asyncio.run(a.get_attributes())
    a.rarity()