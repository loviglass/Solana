import json

file = open('new.txt', 'r')
lis = []
for line in file.readlines():
    candy_machine = ''.join(line.split(' config')[:1])[-44:]
    config = 'config: '.join(line.split(' items_redeemed')[:1])[-44:]

    items_redeemed = ''.join(line.split('items_redeemed: ')[1:])
    items_redeemed = ''.join(items_redeemed.split(',')[:1])

    price = ''.join(line.split('price: ')[1:])
    price = ''.join(price.split(' ')[:1])

    items_available = ''.join(line.split('items_available: ')[1:])
    items_available = ''.join(items_available.split(' ')[:1])

    go_live_date = ''.join(line.split('go_live_date: ')[1:])

    print(line)

    dic = {'candy machine': candy_machine,
           'config': config,
           'items_redeemed': items_redeemed,
           'price': price,
           'items_available': items_available,
           'go_live_date': go_live_date}
    lis.append(dic)

with open('new.json', 'w') as outfile:
    json.dump(lis, outfile, ensure_ascii=False, indent=4)

