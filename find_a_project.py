import time
from solana.rpc.api import Client
import asyncio
from solana.rpc.async_api import AsyncClient
import base64
import base58


class FindAProject:
    def __init__(self):
        self.start_time = time.time()
        self.project_name = ''
        self.sol_client = Client("https://api.mainnet-beta.solana.com")
        self.projects_meta = []

    def get_candy_machines(self):
        candy_machines = []
        nft_cm_program = 'cndyAnrLdpjq1Ssp1z8xxDsB8dxe7u4HL5Nxi2K5WXZ'
        response = self.sol_client.get_program_accounts(nft_cm_program, encoding="jsonParsed", data_size=529)
        for account in response['result']:
            candy_machines.append(account)
        return candy_machines

    async def get_cm_data(self, candy_machines):
        data_list = []
        pubkey_list = []
        for account in candy_machines:
            pubkey_list.append(account['pubkey'])
        async with AsyncClient("https://api.mainnet-beta.solana.com") as client:
            for pubkey in pubkey_list:
                response = await client.get_account_info(pubkey)
                data = response['result']['value']['data'][0]
                print(data)
                data_list.append(data)
        print("--- %s seconds ---" % (time.time() - self.start_time))
        return data_list

    def decode_cm_data(self, data_list):
        print('test')
        for data in data_list:
            cm_struct = {
                "descriptor": 8,
                "authority": 32,
                "wallet": 32,
                "token_mint": 1,
                "config": 32,
                "uuid": 10,
                "price": 8,
                "items_available": 8,
                "go_live_date": 1,
                "items_redeemed": 8,
                "bump": 1}
            decode_data = base64.b64decode(data).hex().rstrip('0')
            offset = 0
            for param in cm_struct:
                value = decode_data[offset:cm_struct[param] * 2 + offset]
                # Except options
                if cm_struct[param] == 1:
                    if value == '00':
                        pass
                    elif param == "token_mint":
                        cm_struct[param] = 32
                        offset = offset + 2
                        value = decode_data[offset:cm_struct[param] * 2 + offset]
                    elif param == "go_live_date":
                        cm_struct[param] = 8
                        offset = offset + 2
                        value = decode_data[offset:cm_struct[param] * 2 + offset]
                    # Bump
                    elif param == "bump":
                        value = int(bytes.fromhex(value).rstrip(b'0')[::-1].hex(), 16)
                # Public keys
                if cm_struct[param] == 32:
                    value = base58.b58encode(bytes.fromhex(value))
                # Int values
                if cm_struct[param] == 8:
                    # Except descriptor (not int)
                    if param == 'descriptor':
                        value = base58.b58encode(bytes.fromhex(value))
                    else:
                        value = int(bytes.fromhex(value).rstrip(b'0')[::-1].hex(), 16)
                # uuid
                if cm_struct[param] == 10:
                    value = bytes.fromhex(value)[3:][1:].decode('UTF-8')
                offset = cm_struct[param] * 2 + offset
                cm_struct[param] = value

            timestamp = int(time.time())
            if int(cm_struct['go_live_date']) >= timestamp:
                self.projects_meta.append(cm_struct)
                print(cm_struct)
        return self.projects_meta


if __name__ == '__main__':
    a = FindAProject()
    cm = a.get_candy_machines()
    cm_data = asyncio.run(a.get_cm_data(cm))