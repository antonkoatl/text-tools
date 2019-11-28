import re
from pprint import pprint

from requests import get
import wikitextparser as wtp

from wikt_template_parser import parse_template, known_template

replacements_opencorpora = {'adv ru': 'ADVB',
                            'деепр ru': 'GRND',
                            'Форма-сущ': 'NOUN',
                            'сущ ru': 'NOUN',
                            'Форма-гл': 'VERB',
                            'Форма-прил': 'ADJS',
                            'part ru': 'PRCL',
                            'предикатив': 'PRED',
                            'предикативы': 'PRED',
                            }
replacements_universalD = {'adv ru': 'ADV',
                           'деепр ru': 'VERB',  # VerbForm=Conv
                           'Форма-сущ': 'NOUN',
                            'сущ ru': 'NOUN',
                           'Форма-гл': 'VERB',
                           'Форма-прил': 'ADJ',
                           'part ru': 'PART',
                           'предикатив': 'ADV',
                           'предикативы': 'ADV',
                           }
r_gender = {
    'м': 'Masc',
    'ж': 'Fem',
    'с': 'Neut',
}
r_case_opencorpora = {
    'предложного': 'loct',
}
r_case_universalD = {
    'предложного': 'Loc',
}
r_number = {
    'ед': 'Sing',
    'мн': 'Plur',
}
r_degree = {

}
r_aspect_opencorpora = {
    'сов': 'perf',
    'несов': 'impf',
}
r_aspect_universalD = {
    'сов': 'Perf',
    'несов': 'Imp',
}
r_tense_opencorpora = {
    'наст': 'pres',
    'прош': 'past',
    'будущ': 'futr',
}
r_tense_universalD = {
    'наст': 'Pres',
    'прош': 'Past',
    'будущ': 'Fut',
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


def get_wikitext_api(word, language='ru'):
    resp = get('https://{}.wiktionary.org/w/api.php'.format(language), {
        'action': 'query',
        'titles': word,
        'languages': language,
        'prop': 'revisions',
        'rvprop': 'content',
        'format': 'json',
    }).json()

    pages = resp['query']['pages']
    page = list(pages.values())[0]
    data = page['revisions'][0]['*']

    if 'redirect' in data.lower():
        new_word = re.search('\[\[([́а-яёА-ЯЁ]+)\]\]', data).group(1)
        return get_wikitext_api(new_word, language)

    return data


def accent(*words):
    return all(['́' in w for w in words])


def search_template_for_argument(template, name):
    for a in template.arguments:
        if a.name.strip() == name:
            return a

    return None

repl = ['по-слогам', '{', '}', '|']

def parse_slogi(value):
    word_acc = []
    # if 2 variants
    match = re.fullmatch(r'[{}а-яА-Я́\-\|]+(( и )|(, ))[{}а-яА-Я́\-\|]+', value)
    if match is not None:
        var1, var2 = value.split(match.group(1))



        for r in repl:
            var1 = var1.replace(r, '')
            var2 = var2.replace(r, '')

        word_acc = [var1, var2]

    else:
        for r in repl:
            value = value.replace(r, '')

        word_acc = [value]

    return word_acc


def search_template_for_argument_value(template, name):
    a = search_template_for_argument(template, name)
    if a is not None:
        v = a.value.strip()
        if len(v) > 0: return v
    return None


def get_name_value(argument):
    name = argument.name.strip()
    value = argument.value.strip()
    return name, value if len(value) > 0 else None

def parse_tags_from_template(template, opencorpora_tag, universalD_tag):
    opencorpora_tag['pos'] = replacements_opencorpora[get_pos_from_template_name(template)]
    if 'tag' not in opencorpora_tag: opencorpora_tag['tag'] = {}

    universalD_tag['pos'] = replacements_universalD[get_pos_from_template_name(template)]
    if 'tag' not in universalD_tag: universalD_tag['tag'] = {}

    opencorpora_tag['norm'] = get_name_value(template.arguments[0])[1]
    universalD_tag['norm'] = get_name_value(template.arguments[0])[1]

    for argument in template.arguments:
        name, value = get_name_value(argument)

        if name == 'база':
            opencorpora_tag['base'] = value
            universalD_tag['base'] = value
            continue

        if name == 'род':
            opencorpora_tag['tag']['Gender'] = r_gender.get(value)
            universalD_tag['tag']['Gender'] = r_gender.get(value)
            continue



        if name == 'падеж':
            opencorpora_tag['tag']['Case'] = r_case_opencorpora.get(value)
            universalD_tag['tag']['Case'] = r_case_universalD.get(value)
            continue

        if name == 'предложного':
            opencorpora_tag['tag']['Case'] = r_case_opencorpora.get(name)
            universalD_tag['tag']['Case'] = r_case_universalD.get(name)
            continue

        if name == 'кр':
            if value == '1':
                opencorpora_tag['tag']['Degree'] = 'Short'
                universalD_tag['tag']['Degree'] = 'Short'
            continue

        if name == 'или':
            if value is None: continue
            opencorpora_tag['pos-or'] = replacements_opencorpora[value]
            v = replacements_universalD[argument.value.strip()]
            if v != universalD_tag['pos']:
                universalD_tag['pos-or'] = v
            continue

        if name == 'степень':
            if value is None: continue
            opencorpora_tag['tag']['Degree'] = r_degree.get(value)
            universalD_tag['tag']['Degree'] = r_degree.get(value)
            continue

        if name == 'вид':
            if value is None: continue
            opencorpora_tag['tag']['Aspect'] = r_aspect_opencorpora.get(value)
            universalD_tag['tag']['Aspect'] = r_aspect_universalD.get(value)
            continue

        if name == 'время':
            if value is None: continue
            opencorpora_tag['tag']['Tense'] = r_tense_opencorpora.get(value)
            universalD_tag['tag']['Tense'] = r_tense_universalD.get(value)
            continue



        if name == 'возвратность':
            if value == 'возвр':
                # Refl
                pass



        if value is not None:
            if value == '1':
                opencorpora_tag['tag']['Number'] = r_number.get('ед')
                universalD_tag['tag']['Number'] = r_number.get('ед')
                continue

            if value == '3':
                opencorpora_tag['tag']['Person'] = r_person_opencorpora.get(value)
                universalD_tag['tag']['Person'] = r_person_universalD.get(value)
                continue

            fl = False
            for v in r_tense_opencorpora:
                if value == v:
                    opencorpora_tag['tag']['Tense'] = r_tense_opencorpora.get(value)
                    universalD_tag['tag']['Tense'] = r_tense_universalD.get(value)
                    fl = True
                    continue

            for v in r_number:
                if value == v:
                    opencorpora_tag['tag']['Number'] = r_number.get(value)
                    universalD_tag['tag']['Number'] = r_number.get(value)
                    fl = True
                    continue

            if fl: continue

        if name == 'слоги':
            continue

        print('argument not used', name, value)


def search_section_for_template(section, name):
    for template in section.templates:
        if template.name.strip() == name:
            return template

    return None


def get_pos_from_template_name(template,):
    name = template.name.strip()
    for key in replacements_opencorpora:
        if key in name:
            return key


def get_variant_from_section(section):
    word_acc = None

    opencorpora_tag = {}
    universalD_tag = {}

    # looking for word
    t = search_section_for_template(section, 'заголовок')
    if t is None: t = search_section_for_template(section, 'з')

    if t is not None:
        v = search_template_for_argument_value(t, 'ударение')
        if v is not None:
            word_acc = [v]

    # # search for section
    # if word_acc is None or not accent(*word_acc):
    #     for section2 in section.sections:
    #         if section2.title == ' Морфологические и синтаксические свойства ':
    #             template = section2.templates[0]
    #             argument = search_template_for_argument(template, 'слоги')
    #             value = argument.value.rstrip()
    #             word_acc = parse_slogi(value)
    #             parse_tags_from_remplate(template, opencorpora_tag, universalD_tag)
    #             break

    # search in templates

    # for template in section.templates:
    #     pos = get_pos_from_template_name(template)
    #     if pos is not None:
    #         if word_acc is None or not accent(*word_acc):
    #             argument = search_template_for_argument(template, 'слоги')
    #             value = argument.value.rstrip()
    #             word_acc = parse_slogi(value)
    #
    #         parse_tags_from_template(template, opencorpora_tag, universalD_tag)
    #
    #         break

    if word_acc is None or not accent(*word_acc):
        raise Exception

    for template in section.templates:
        if known_template(template):
            parse_template(template, opencorpora_tag, universalD_tag)

    return [word_acc, opencorpora_tag, universalD_tag]


def parse_wikt_ru(word):
    parsed = wtp.parse(get_wikitext_api(word))

    variants = []

    for cur_section in parsed.sections:
        if len(cur_section.templates) > 0 and '-ru-' in cur_section.templates[0].name:
            for section in cur_section.sections:
                if len(section.templates) > 0 and (section.templates[0].name == 'заголовок' or section.templates[0].name == 'з'):
                    variants.append(get_variant_from_section(section))

            if len(variants) == 0:
                for section in cur_section.sections:
                    if section.title == ' Морфологические и синтаксические свойства ':
                        variants.append(get_variant_from_section(section))


    return variants

def parse_wikt_en(word):
    pass

if __name__ == "__main__":
    pprint(parse_wikt_ru('вдали'))



