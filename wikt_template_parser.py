import copy
import re

import wikitextparser as wtp

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
    'именительный': 'nomn',
    'родительный': 'gent',
    'дательный': 'datv',
    'винительный': 'accs',
    'творительный': 'ablt',
    'предложный': 'loct',
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
    'именительный': 'Nom',
    'родительный': 'Gen',
    'дательный': 'Dat',
    'винительный': 'Acc',
    'творительный': 'Ins',
    'предложный': 'Loc',
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
    'm': 'Masc',
    'f': 'Fem',
    'n': 'Neut',
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
r_anim = {
    'a': 'Anim',
    'ina': 'Inan',
}

known_templates = ['Форма-сущ', 'Форма-гл', 'conj ru']
advansed_templates = ['сущ ru']

def known_template(template):
    template_name = template.name.strip()
    if template_name in known_templates:
        return True

    for i in advansed_templates:
        if i in template_name:
            return True
    return False

def get_name_value(argument):
    name = argument.name.strip()
    value = argument.value.strip()
    return name, value if len(value) > 0 else None

def parse_template(template, opencorpora_tag, universalD_tag):
    from wiktparser import search_section_for_template, get_word_from_slogi, get_wikitext_api_expandtemplates

    template_name = template.name.strip()

    if 'tag' not in opencorpora_tag: opencorpora_tag['tag'] = {}
    if 'tag' not in universalD_tag: universalD_tag['tag'] = {}

    if template_name == 'Форма-сущ':
        opencorpora_tag['pos'] = 'NOUN'
        universalD_tag['pos'] = 'NOUN'

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

        return []

    if template_name == 'Форма-гл':
        opencorpora_tag['pos'] = 'VERB'
        universalD_tag['pos'] = 'VERB'

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

        return []

    if template_name == 'conj ru':
        opencorpora_tag['pos'] = 'CONJ'
        universalD_tag['pos'] = 'CONJ'

        t = search_section_for_template(template, 'по-слогам')
        base = get_word_from_slogi(t)[0].replace('́', '')
        opencorpora_tag['base'] = base
        universalD_tag['base'] = base

        return []

    if 'сущ ru' in template_name:
        opencorpora_tag['pos'] = 'NOUN'
        universalD_tag['pos'] = 'NOUN'

        base = get_word_from_slogi(template)[0].replace('́', '')
        opencorpora_tag['base'] = base
        universalD_tag['base'] = base

        opencorpora_tag['tag']['Number'] = r_number['ед']
        universalD_tag['tag']['Number'] = r_number['ед']

        data = template_name.split()[2:-1]

        for d in data:
            if d in r_gender:
                opencorpora_tag['tag']['Gender'] = r_gender.get(d)
                universalD_tag['tag']['Gender'] = r_gender.get(d)
                continue

            if d in r_anim:
                opencorpora_tag['tag']['Animacy'] = r_anim.get(d)
                universalD_tag['tag']['Animacy'] = r_anim.get(d)
                continue

            print(template_name, d)

        # склонения по падежу / числу
        additional_variants = []
        parsed = wtp.parse(get_wikitext_api_expandtemplates(template.string))
        table = parsed.tables[0].data()
        header = table.pop(0)
        for row in table:
            case = re.match(r'\[\[([а-яё.]+)(\||\]\])', row[0]).group(1)
            m = re.fullmatch(r'([́а-яёА-ЯЁ]+)', row[1])
            if m is None: m = re.search(r'>([́а-яёА-ЯЁ]+)<', row[1])

            if m is not None:
                sing = [m.group(1)]
            else:
                splits = row[1].split('<br/>')
                if len(splits) > 1:
                    sing = splits
                else:
                    raise Exception

            m = re.fullmatch(r'([́а-яёА-ЯЁ]+)', row[2])
            if m is None: m = re.search(r'>([́а-яёА-ЯЁ]+)<', row[2])

            if m is not None:
                plur = [m.group(1)]
            else:
                splits = row[2].split('<br/>')
                if len(splits) > 1:
                    plur = splits
                else:
                    raise Exception

            if r_case_opencorpora[case]  != 'nomn':
                opencorpora_tag_copy = copy.deepcopy(opencorpora_tag)
                universalD_tag_copy = copy.deepcopy(universalD_tag)
                opencorpora_tag_copy['tag']['Case'] = r_case_opencorpora[case]
                universalD_tag_copy['tag']['Case'] = r_case_universalD[case]
                opencorpora_tag_copy['tag']['Number'] = r_number['ед']
                universalD_tag_copy['tag']['Number'] = r_number['ед']
                additional_variants.append([sing, opencorpora_tag_copy, universalD_tag_copy])

            opencorpora_tag_copy = copy.deepcopy(opencorpora_tag)
            universalD_tag_copy = copy.deepcopy(universalD_tag)
            opencorpora_tag_copy['tag']['Case'] = r_case_opencorpora[case]
            universalD_tag_copy['tag']['Case'] = r_case_universalD[case]
            opencorpora_tag_copy['tag']['Number'] = r_number['мн']
            universalD_tag_copy['tag']['Number'] = r_number['мн']
            additional_variants.append([plur, opencorpora_tag_copy, universalD_tag_copy])



        return additional_variants

    print(template_name)
    raise Exception()