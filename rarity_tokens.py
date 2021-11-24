import json


def read_project_tokens():
    duplicate_attributes = {}
    project_tokens = json.load(open('dump SREDPANDA.json', 'r'))
    # project_tokens = json.load(open('ASPECT_tokens.json', 'r'))
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
        attribute_type = json.loads(key)["trait_type"]
        type_list.append(attribute_type)

    # подсчёт уникальности атрибутов
    rarity_attributes = []
    for attribute_type in set(type_list):
        for attribute in sorted_attributes.items():
            types = json.loads(attribute[0])['trait_type']
            value = json.loads(attribute[0])['value']
            proc = 100 - (attribute[1]/tokens_count)*100
            # фильтрование уникальности (не менее 90%)
            if proc >= 90:
                if types == attribute_type:
                    rarity_attributes.append({'value': value, 'trait_type': attribute_type, 'rarity': proc})
                    break

    # поиск редких атрибутов в списке всех токенов
    for token in project_tokens:
        project_name = token['symbol']
        project_url = token['external_url']
        for attribute in token['attributes']:
            for line in rarity_attributes:
                rare_attribute = {"value": line['value'], "trait_type": line['trait_type']}
                if rare_attribute == attribute:
                    rarity_tokens.append({'name': token['name'], 'rarity': line['rarity']})

    # сортировка токенов по редкости и вывод топ 3
    rarity_tokens = sorted(rarity_tokens, key=lambda k: k['rarity'])[-3:]

    project_info = {project_name: [{'info': [{'project_url': project_url}, {'{candy machine': ''}, {'config': ''}, {'items_redeemed': ''}, {'items_available': ''}, {'price': ''}, {'go_live_date': ''}]}, {'rarity_tokens': ''}]}
    print(project_info)


read_project_tokens()
