import base64
import base58
from solana.rpc.api import Client


class GetMeta:
    def __init__(self):
        sol_client = Client("https://api.mainnet-beta.solana.com")
        account = 'DBLJ2VKwKjSnAqPD6MbJQzWSmoEaCLzZ2kwNcDDQwgWv'  # 'DBLJ2VKwKjSnAqPD6MbJQzWSmoEaCLzZ2kwNcDDQwgWv' Cu9hWTmbPDBJn3YvqQMGnWsSv5JPd2JrF8ZenFoB6VG7
        response = sol_client.get_account_info(account, encoding="jsonParsed")
        self.candy_machine = {
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
            "bump": 1
            }
        self.decode_metadata(response)

    def decode_metadata(self, response):
        decode_data = base64.b64decode(response['result']['value']['data'][0])
        decode_data = decode_data.hex().rstrip('0')
        offset = 0
        for param in self.candy_machine:
            value = decode_data[offset:self.candy_machine[param] * 2 + offset]
            # Except options
            if self.candy_machine[param] == 1:
                if value == '00':
                    pass

                elif param == "token_mint":
                    self.candy_machine[param] = 32
                    offset = offset + 2
                    value = decode_data[offset:self.candy_machine[param] * 2 + offset]

                elif param == "go_live_date":
                    self.candy_machine[param] = 8
                    offset = offset+2
                    value = decode_data[offset:self.candy_machine[param] * 2 + offset]
                # Bump
                elif param == "bump":
                    value = int(bytes.fromhex(value).rstrip(b'0')[::-1].hex(), 16)

            # Public keys
            if self.candy_machine[param] == 32:
                value = base58.b58encode(bytes.fromhex(value))

            # Int values
            if self.candy_machine[param] == 8:
                # Except descriptor (not int)
                if param == 'descriptor':
                    value = base58.b58encode(bytes.fromhex(value))
                else:
                    value = int(bytes.fromhex(value).rstrip(b'0')[::-1].hex(), 16)

            # uuid
            if self.candy_machine[param] == 10:
                value = bytes.fromhex(value)[3:][1:].decode('UTF-8')

            offset = self.candy_machine[param]*2+offset
            self.candy_machine[param] = value
        print(self.candy_machine)


if __name__ == '__main__':
    a = GetMeta()
