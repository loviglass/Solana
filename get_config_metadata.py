import base64
import base58
from solana.rpc.api import Client


class GetMeta:
    def __init__(self):
        sol_client = Client("https://api.mainnet-beta.solana.com")
        account = 'CaNoiCbcu71G6pEjTTnZQ662MHJz7uu4rwMxBaHt7NWa'  # 9FNBmGGb2cVHzM93F79xWGiB3jPGtTprF6aKmHrj1G5v
        response = sol_client.get_account_info(account, encoding="jsonParsed")
        self.candy_machine = {
            "descriptor": 8,
            "authority": 32,
            "uuid": str
            }
        self.decode_metadata(response)

    def decode_metadata(self, response):
        print(response)
        data = base64.b64decode(response['result']['value']['data'][0])
        print(data[220:1000])
        decode_data = data.hex().rstrip('0')
        print(decode_data[:500])
        test_authority = 'GenoS3ck8xbDvYEZ8RxMG3Ln2qcyoAN8CTeZuaWgAoEA'
        print(base58.b58decode(test_authority).hex())

        # 8
        descriptor = decode_data[:16]
        print(f'descriptor = {descriptor}')
        # 32
        authority = decode_data[16:64+16]
        print(f'hex = {authority}, authority = {base58.b58encode(bytes.fromhex(authority))}')
        # 10
        uuid = decode_data[64+16:64+16+20]
        print(f'hex = {uuid} uuid = {bytes.fromhex(uuid[8:])}')
        # 11
        symbol = decode_data[64+16+20:64+16+20+22]
        print(f'hex = {symbol} symbol = {bytes.fromhex(symbol[8:])}')
        # 9 (2)
        seller_fee_basis_points = decode_data[64+16+20+22:64+16+20+22+18]
        print(f'hex = {seller_fee_basis_points} seller_fee_basis_points = {int(seller_fee_basis_points.strip("0").rstrip("0")[::-1], 16)}')
        # 32
        creators = decode_data[64+16+20+22+18:64+16+20+22+18+64]
        print(f'hex = {creators} creators = {base58.b58encode(bytes.fromhex(creators))}')
        # 8
        max_supply = decode_data[64+16+20+22+18+64:64+16+20+22+18+64+16]
        print(f'hex = {max_supply} max_supply = {int(max_supply.rstrip("0")[::-1], 16)}')

        # 220 symbol
        is_mutable = None
        retain_authority = None
        max_number_of_lines = None
        # 255 symbol

        # 36
        name = data[255:291]
        print(f'hex = {name.hex()} name = {name[:17]}')
        # 63 symbol
        uri = data[291:291+63]
        print(f'hex = {uri.hex()} uri = {uri}')
        print(data[495:512])
        name_2 = data[354+141:354+141+17]
        print(name_2)
        uri_2 = data[354+141+17:354+141+17+63]
        print(uri_2)
        last = data[-3000:]
        print(last)

        f = open('config_data.txt', 'w')
        f.write(str(data))


if __name__ == '__main__':
    a = GetMeta()