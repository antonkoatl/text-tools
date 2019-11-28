r_case_opencorpora = {
    'и': 'nomn',
    'р': 'gent',
    'д': 'datv',
    'в': 'accs',
    'т': 'ablt',
    'п': 'loct',
    'им.': 'nomn',
    'род.': 'gent',
    'дат.': 'datv',
    'вин.': 'accs',
    'твор.': 'ablt',
    'пр.': 'loct',
    'именительного': 'nomn',
    'родительного': 'gent',
    'дательного': 'datv',
    'винительного': 'accs',
    'творительного': 'ablt',
    'предложного': 'loct',
}
r_case_universalD = {
    'и': 'Nom',
    'р': 'Gen',
    'д': 'Dat',
    'в': 'Acc',
    'т': 'Ins',
    'п': 'Loc',
    'им.': 'Nom',
    'род.': 'Gen',
    'дат.': 'Dat',
    'вин.': 'Acc',
    'твор.': 'Ins',
    'пр.': 'Loc',
    'именительного': 'Nom',
    'родительного': 'Gen',
    'дательного': 'Dat',
    'винительного': 'Acc',
    'творительного': 'Ins',
    'предложного': 'Loc',
}
r_number = {
    'ед': 'Sing',
    '1': 'Sing',
    'мн': 'Plur',
}
r_tense_opencorpora = {
    'наст': 'pres',
    'пр': 'past',
    'буд': 'futr',
}
r_tense_universalD = {
    'наст': 'Pres',
    'пр': 'Past',
    'буду': 'Fut',
}
r_gender = {
    'м': 'Masc',
    'ж': 'Fem',
    'с': 'Neut',
}
r_person_opencorpora = {
    '1': '1per',
    '2': '2per',
    '3': '3per',
}
r_person_universalD = {
    '1': '1',
    '2': '2',
    '3': '3',
}

known_templates = ['Форма-сущ', 'Форма-гл']

def known_template(template):
    template_name = template.name.strip()
    if template_name in known_templates:
        return True
    return False

def get_name_value(argument):
    name = argument.name.strip()
    value = argument.value.strip()
    return name, value if len(value) > 0 else None

def parse_template(template, opencorpora_tag, universalD_tag):
    template_name = template.name.strip()

    if template_name == 'Форма-сущ':
        opencorpora_tag['pos'] = 'NOUN'
        if 'tag' not in opencorpora_tag: opencorpora_tag['tag'] = {}

        universalD_tag['pos'] = 'NOUN'
        if 'tag' not in universalD_tag: universalD_tag['tag'] = {}

        for argument in template.arguments:
            name, value = get_name_value(argument)

            if name in ['база', '1'] and value is not None:
                opencorpora_tag['base'] = value
                universalD_tag['base'] = value
                continue

            if name in ['падеж', '2'] and value is not None:
                if value in ['ив', 'рв', 'рдп']:
                    opencorpora_tag['tag']['Case'] = []
                    universalD_tag['tag']['Case'] = []
                    for v in value:
                        opencorpora_tag['tag']['Case'].append(r_case_opencorpora.get(v))
                        universalD_tag['tag']['Case'].append(r_case_universalD.get(v))
                    continue

                if ' и ' in value:
                    opencorpora_tag['tag']['Case'] = []
                    universalD_tag['tag']['Case'] = []
                    for v in value.split(' и '):
                        opencorpora_tag['tag']['Case'].append(r_case_opencorpora.get(v))
                        universalD_tag['tag']['Case'].append(r_case_universalD.get(v))
                    continue

                opencorpora_tag['tag']['Case'] = r_case_opencorpora.get(value)
                universalD_tag['tag']['Case'] = r_case_universalD.get(value)
                continue

            if name in ['число', '3'] and value is not None:
                opencorpora_tag['tag']['Number'] = r_number[value]
                universalD_tag['tag']['Number'] = r_number[value]
                continue

            if name in ['помета', '5']:
                continue

            if name == 'число' and value is not None:
                opencorpora_tag['tag']['Number'] = r_number[value]
                universalD_tag['tag']['Number'] = r_number[value]
                continue

            if name == 'слоги':
                continue

        return

    if template_name == 'Форма-гл':
        opencorpora_tag['pos'] = 'VERB'
        if 'tag' not in opencorpora_tag: opencorpora_tag['tag'] = {}

        universalD_tag['pos'] = 'VERB'
        if 'tag' not in universalD_tag: universalD_tag['tag'] = {}

        for argument in template.arguments:
            name, value = get_name_value(argument)

            if name in ['база', '1'] and value is not None:
                opencorpora_tag['base'] = value
                universalD_tag['base'] = value
                continue

            if name in ['время', '2']:
                if value is None: continue
                opencorpora_tag['tag']['Tense'] = r_tense_opencorpora.get(value)
                universalD_tag['tag']['Tense'] = r_tense_universalD.get(value)
                continue

            if name == 'залог':
                continue

            if name in ['род', '3']:
                if value is None: continue
                opencorpora_tag['tag']['Gender'] = r_gender.get(value)
                universalD_tag['tag']['Gender'] = r_gender.get(value)
                continue

            if name in ['лицо', '4']:
                opencorpora_tag['tag']['Person'] = r_person_opencorpora.get(value)
                universalD_tag['tag']['Person'] = r_person_universalD.get(value)
                continue

            if name in ['число', '5'] and value is not None:
                opencorpora_tag['tag']['Number'] = r_number[value]
                universalD_tag['tag']['Number'] = r_number[value]
                continue

            if name in ['накл', '6'] and value is not None:
                continue

            if name == 'деепр':
                continue

            if name == 'прич':
                continue

            if name == 'кр':
                continue

            if name in ['помета', '7'] and value is not None:
                continue

            if name == 'форма':
                continue

            if name == 'слоги':
                continue

        return


    print(template_name)
    raise Exception()