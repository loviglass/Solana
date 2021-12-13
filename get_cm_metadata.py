import base64
import base58
from solana.rpc.api import Client
from datetime import datetime


class GetMeta:
    def __init__(self):
        sol_client = Client("https://api.mainnet-beta.solana.com")
        account = 'Cu9hWTmbPDBJn3YvqQMGnWsSv5JPd2JrF8ZenFoB6VG7'
        response = sol_client.get_account_info(account, encoding="jsonParsed")
        self.candy_machine = {
            "authority": None,
            "wallet": None,
            "token_mint": None,
            "config": None,
            "data": {
                "uuid": None,
                "price": None,
                "items_available": None,
                "go_live_date": None
                    },
            "items_redeemed": None,
            "bump": None
            }
        self.decode_metadata(response)

    def decode_metadata(self, response):
        decode_data = base64.b64decode(response['result']['value']['data'][0])
        descriptor = base58.b58encode(decode_data[:8])
        authority = base58.b58encode(decode_data[8:40])
        wallet = base58.b58encode(decode_data[40:40+32])
        mint_index = base58.b58encode(decode_data[40+32:40+32+1])
        if mint_index == b'1':
            config = base58.b58encode(decode_data[40+32+1:40+32+1+32])
            token_mint = None
        else:
            token_mint = base58.b58encode(decode_data[40+32+1:40+32+1+32])

        stand_data = decode_data[40+32+1+32:40+32+1+32+44]

        bump = int(stand_data[-1:].hex(), 16)
        items_redeemed = int(bytes.fromhex(stand_data[-9:-1].hex().rstrip('0'))[::-1].hex(), 16)
        go_live_date = int(bytes.fromhex(stand_data[-9-8:-9].hex().rstrip('0'))[::-1].hex(), 16)
        go_live_date = datetime.utcfromtimestamp(go_live_date).strftime('%d-%m-%Y %H:%M:%S')
        items_available = int(bytes.fromhex(stand_data[-9-9-8:-9-9].hex().rstrip('0'))[::-1].hex(), 16)
        price = int(bytes.fromhex(stand_data[-9-9-8-8:-9-9-8].hex().rstrip('0'))[::-1].hex(), 16)
        uuid = stand_data[:-9-9-8-8][3:][1:].decode('UTF-8')

        self.candy_machine["authority"] = authority
        self.candy_machine["wallet"] = wallet
        self.candy_machine["token_mint"] = token_mint
        self.candy_machine["config"] = config
        self.candy_machine["data"]["uuid"] = uuid
        self.candy_machine["data"]["price"] = price
        self.candy_machine["data"]["items_available"] = items_available
        self.candy_machine["data"]["go_live_date"] = go_live_date
        self.candy_machine["items_redeemed"] = items_redeemed
        self.candy_machine["bump"] = bump

        print(self.candy_machine)


if __name__ == '__main__':
    a = GetMeta()
