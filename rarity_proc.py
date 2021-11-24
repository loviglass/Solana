import json


def rarity():
    compare_dict = {}
    type_dict = {}
    type_list = []
    sorted_dict = {}
    rarity_tokens = []
    rarity_list = []
    json_file = open('result.json', 'r')
    json_file = json.load(json_file)
    count = len(json_file)
    print(f'найдено {count} токенов')
    for token_info in json_file:
        token_info = json.loads(token_info)

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

    json_file = open('result.json', 'r')
    for token_info in json.load(json_file):
        token_info = json.loads(token_info)
        for attribute in token_info['attributes']:
            for line in rarity_list:
                atr = {"value": line['value'], "trait_type": line['trait_type']}
                if attribute == atr:
                    rarity_tokens.append({token_info['name']: line['rarity']})

    for line in rarity_tokens:
        print(line)


rarity()
