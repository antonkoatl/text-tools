import json
import pickle
import re
import tqdm as tqdm

import dawg_python as dawg

import pymorphy2 as pymorphy2

from wiktparser import parse_wikt_ru

morpher = pymorphy2.MorphAnalyzer()

# from russian_g2p.Accentor import Accentor
# your_accentor = Accentor(mode='many')
# print(your_accentor.do_accents([['сорок']]))

russian_vowels = {'а', 'о', 'у', 'э', 'ы', 'и', 'я', 'ё', 'ю', 'е', 'А', 'О', 'У', 'Э', 'Ы', 'И', 'Я', 'Ё', 'Ю', 'Е'}

def count_vovels(word):
    vowels_counter = 0
    for c in word:
        if c in russian_vowels:
            vowels_counter += 1
    return vowels_counter

def get_first_vovel_pos(word):
    for i, c in enumerate(word):
        if c in russian_vowels:
            return i + 1



# accents = {}
# homographs = {}

# for k in accents:
#     accents[k] = [accents[k], None]

# for k in homographs:
#     homographs[k] = [homographs[k], {}]

def compare_tags(pos1, tag1, pos2, tag2, strict=False):
    synonims =[['DET', 'ADJ', 'ADJS', 'ADJF'],
               ['ADVB', 'ADV'],
               ['VERB', 'GRND', 'INFN']]
    if pos1 != pos2:
        fl = False
        for syn in synonims:
            if pos1 in syn and pos2 in syn:
                fl = True
                break
        if not fl: return False

    tag1 = tag1.replace('_', '')
    tag2 = tag2.replace('_', '')

    tags_dict1 = tag1.split('|')
    tags_dict2 = tag2.split('|')

    tags_dict1 = {x.split('=')[0]: x.split('=')[1] for x in tags_dict1 if len(x) > 0}
    tags_dict2 = {x.split('=')[0]: x.split('=')[1] for x in tags_dict2 if len(x) > 0}

    for key in tags_dict1:
        if key == 'Number':
            if not key in tags_dict2:
                return False
            if tags_dict1[key] == 'Sing' and tags_dict2[key] != 'Sing':
                return False
            if tags_dict1[key] != 'Sing' and tags_dict2[key] == 'Sing':
                return False

        if key == 'Degree':
            if not key in tags_dict2:
                return False
            if tags_dict1[key] != tags_dict2[key]:
                return False

        if key == 'Case':
            if strict:
                if not key in tags_dict2:
                    return False
                if tags_dict1[key] != tags_dict2[key]:
                    return False
            else:
                if key in tags_dict2:
                    if tags_dict1[key] != tags_dict2[key]:
                        fl = False
                        if tags_dict1[key] in ['Nom', 'Acc', 'Nomn'] and tags_dict2[key] in ['Nom', 'Acc']: fl = True
                        if tags_dict1[key] in ['Gen', 'Dat', 'Ins'] and tags_dict2[key] in ['Gen', 'Dat', 'Ins']: fl = True
                        if not fl:
                            return False



    return True

class Parser():
    def __init__(self):
        self.accents = []
        self.homographs = []
        self.homographs2 = set()
        self.changed = False

    def load(self):
        with open(r'accents.pickle', 'rb') as f:
            self.accents = pickle.load(f)
        with open(r'homographs.pickle', 'rb') as f:
            self.homographs = pickle.load(f)
        with open(r'homographs2.pickle', 'rb') as f:
            self.homographs2 = set(pickle.load(f))

        self.start_size = (len(self.accents), len(self.homographs), len(self.homographs2))
        print(*self.start_size)

    def save(self):
        with open(r'accents.pickle', 'wb') as f:
            pickle.dump(self.accents, f)
        with open(r'homographs.pickle', 'wb') as f:
            pickle.dump(self.homographs, f)
        with open(r'homographs2.pickle', 'wb') as f:
            pickle.dump(self.homographs2, f)

        print(len(self.accents) - self.start_size[0], len(self.homographs) - self.start_size[1], len(self.homographs2) - self.start_size[2])

    def add_homograph(self, word, *pms):
        if count_vovels(word) < 2: return
        self.accents.pop(word, None)

        if word in self.homographs:
            for p, m in pms:
                if p in self.homographs[word][0]:
                    if m is not None:
                        found = False

                        splits = m.split()

                        if len(splits) == 1:
                            m_base = None
                            m_pos = splits[0]
                            m_tag = ''
                        if len(splits) == 2:
                            if '=' in splits[1]:
                                m_base = None
                                m_pos = splits[0]
                                m_tag = splits[1]
                            else:
                                m_base = splits[0]
                                m_pos = splits[1]
                                m_tag = ''
                        else:
                            m_base = splits[0]
                            m_pos = splits[1]
                            m_tag = splits[2]

                        for key in self.homographs[word][1]:
                            splits = key.split()

                            if len(splits) == 1:
                                base = None
                                pos = splits[0]
                                tag = ''
                            if len(splits) == 2:
                                if '=' in splits[1]:
                                    base = None
                                    pos = splits[0]
                                    tag = splits[1]
                                else:
                                    base = splits[0]
                                    pos = splits[1]
                                    tag = ''
                            else:
                                base = splits[0]
                                pos = splits[1]
                                tag = splits[2]

                            if compare_tags(pos, tag, m_pos, m_tag, True):
                                if self.homographs[word][1][key] != p: continue
                                if base is None and m_base is not None:
                                    self.homographs[word][1].pop(key)
                                    self.homographs[word][1][m] = p
                                    self.changed = True
                                    print('added base', m, word)
                                found = True
                                break

                        if not found:
                            # new form for same position
                            if m in self.homographs[word][1]:
                                if isinstance(self.homographs[word][1][m], int):
                                    self.homographs[word][1][m] = {self.homographs[word][1][m], p}
                                else: self.homographs[word][1][m].add(p)
                                print(self.homographs[word])
                            else:
                                self.homographs[word][1][m] = p
                            self.changed = True
                            print('new form', word, p, m)

                else:
                    self.homographs[word][0].add(p)

                    if m is not None:
                        if m in self.homographs[word][1]:
                            self.homographs[word][1][m] = {self.homographs[word][1][m], p}
                            print(self.homographs[word])
                        else:
                            self.homographs[word][1][m] = p

                    self.changed = True
                    print('new homograph', word, p, m)

        else:
            self.homographs[word] = [set(), {}]
            for p, m in pms:
                self.homographs[word][0].add(p)

                if m is not None:
                    self.homographs[word][1][m] = p

            self.changed = True
            print('new homograph', word, self.homographs[word])

    def add_accent(self, f, pos):
        if count_vovels(f) < 2: return
        if f in self.accents:
            if self.accents[f] != pos:
                self.add_homograph(f, [pos, None], [self.accents[f], None])
        else:
            if f in self.homographs:
                self.add_homograph(f, [pos, None])
            else:
                self.accents[f] = pos
                self.changed = True
                print('new accent', f, pos)

    def add_homograph2(self, word):
        if count_vovels(word) < 2: return
        self.accents.pop(word, None)
        self.homographs.pop(word, None)

        if word not in self.homographs2:
            self.homographs2.append(word)
            self.changed = True
            print('new homographs2', word)


    def clean_homographs(self):
        for k in list(self.homographs):
            if len(self.homographs[k][0]) == 1:
                data = self.homographs.pop(k)
                if count_vovels(k) > 1:
                    self.add_accent(k, list(data[0])[0])

    def clean_accents(self):
        for k in list(self.accents):
            if count_vovels(k) == 1:
                self.accents.pop(k)
                print(k)

    def save_if_changed(self):
        if self.changed:
            self.save()

    def remove_homograph(self, word, p):
        self.homographs[word][0].remove(p)
        for m in list(self.homographs[word][1]):
            if self.homographs[word][1][m] == p:
                self.homographs[word][1].pop(m)
        if len(self.homographs[word][0]) == 1:
            p = self.homographs[word][0].pop()
            self.homographs.pop(word)
            self.add_accent(word, p)


def parse_forms():
    with open(r'C:\Users\Admin\PycharmProjects\russian_g2p\russian_g2p\data\All_Forms_UTF8.txt', encoding='utf-8') as f:
        for line in tqdm.tqdm(f):
            line = line.rstrip()
            line = line.replace('`', '') # побочное ударение, игнорируем

            words = line.split('#')
            word = words[0]

            forms = words[1].split(',')

            for f in forms:
                if 'ё' in f: continue
                if re.match('^[a-яА-ЯёЁ\-\']+$', f) is None:
                    print('!!!', f)
                pos = f.find('\'')
                if pos == -1: continue
                f = f.replace('\'', '')

                if f in simple_words_dawg:
                    parser.add_accent(f, simple_words_dawg[f])

                parser.add_accent(f, pos)

def parse_accents():
    # data = json.loads(r'C:\Users\Admin\PycharmProjects\russian_g2p\russian_g2p\data\Accents.json')
    with open(r'C:\Users\Admin\PycharmProjects\russian_g2p\russian_g2p\data\Accents_new.json', mode='r', encoding='utf-8', errors='ignore') as fp:
        data = json.load(fp)

        # for f in tqdm.tqdm(data[1]):
        for f in data[1]:
            pos = f.find('+')
            if pos == -1: continue
            f = f.replace('+', '')

            if 'ё' in f: continue
            if re.match('^[a-яА-ЯёЁ\-\']+$', f) is None:
                print('!!!', f)

            if f in simple_words_dawg:
                parser.add_accent(f, simple_words_dawg[f])

            parser.add_accent(f, pos)

        for f in data[0]:
            for m, f in data[0][f].items():
                pos = f.find('+')
                if pos == -1: continue
                f = f.replace('+', '')

                if 'ё' in f: continue
                if re.match('^[a-яА-ЯёЁ\-\']+$', f) is None:
                    print('!!!', f)

                if re.match('^[0-9]+$', m) is not None:
                    m = None

                parser.add_homograph(f, [pos, m])

def parse_homographs():
    # data = json.loads(r'C:\Users\Admin\PycharmProjects\russian_g2p\russian_g2p\data\Accents.json')
    with open(r'C:\Users\Admin\PycharmProjects\russian_g2p\russian_g2p\data\homographs.json', mode='r', encoding='utf-8', errors='ignore') as fp:
        data = json.load(fp)

        # for f in tqdm.tqdm(data[1]):
        for f in data:
            for m, f in data[f].items():
                pos = f.find('+')
                if pos == -1: continue
                f = f.replace('+', '')

                if 'ё' in f: continue
                if re.match('^[a-яА-ЯёЁ\-\']+$', f) is None:
                    print('!!!', f)

                if re.match('^[0-9]+$', m) is not None:
                    m = None

                parser.add_homograph(f, [pos, m])

def parse_hagen():
    with open(r'C:\Users\Admin\PycharmProjects\untitled\lop1v2.txt', encoding='utf-8') as f:
        for line in f.readlines():
            line = line.strip()
            if len(line) == 0: continue

            line = line.split('%')[0].split('#')[0]

            for w in line.split():
                pos = w.find('\`')
                if pos == -1: continue
                w = w.replace('`', '')

                if 'ё' in w: continue
                if re.match('^[a-яА-ЯёЁ\-\']+$', w) is None:
                    print('!!!', w)

def remove_some():
    accents = ['молча']
    homographs = [['молча', [3, '']],
                  ]

    for w in accents:
        parser.accents.pop(w)

def convert_pymorph_tag(morph):
    # if morph.tag.POS in replace_pos:
    #     tag = replace_pos[morph.tag.POS] + ' '
    # else:
    #     tag = morph.tag.POS + ' '

    tag = morph.tag.POS + ' '

    if morph.tag.animacy is not None:
        tag += 'Animacy=' + morph.tag.animacy.capitalize() + '|'

    if morph.tag.aspect is not None:
        tag += 'Aspect=' + morph.tag.aspect.capitalize() + '|'

    if morph.tag.case is not None:
        tag += 'Case=' + morph.tag.case.capitalize() + '|'

    if morph.tag.gender is not None:
        tag += 'Gender=' + morph.tag.gender.capitalize() + '|'

    # involvement

    if morph.tag.mood is not None:
        tag += 'Mood=' + morph.tag.mood.capitalize() + '|'

    if morph.tag.number is not None:
        tag += 'Number=' + morph.tag.number.capitalize() + '|'

    if morph.tag.person is not None:
        tag += 'Person=' + morph.tag.person.capitalize() + '|'

    if morph.tag.tense is not None:
        tag += 'Tense=' + morph.tag.tense.capitalize() + '|'

    # transitivity

    if morph.tag.voice is not None:
        tag += 'Voice=' + morph.tag.voice.capitalize() + '|'

    tag = tag[:-1]

    return tag

def get_homographs_from_wikt(word):
    homographs = []
    morphs = morpher.parse(word)
    wiki_variants = parse_wikt_ru(word)

    for w, tag in wiki_variants:
        pos = tag.split()[0]

        if len(tag.split()) > 1:
            tags = tag.split()[1]
        else:
            tags = ''

        count = 0
        m_tag_saved = None

        for m in morphs:
            m_tag = convert_pymorph_tag(m)

            if compare_tags(pos, tags, m_tag.split()[0], m_tag.split()[1] if len(m_tag.split()) > 1 else ''):
                if count == 0:
                    count += 1
                    m_tag_saved = m_tag
                else:
                    if not compare_tags(m_tag_saved.split()[0], m_tag_saved.split()[1], m_tag.split()[0], m_tag.split()[1]):
                        count += 1

        if count == 1:
            acc_pos = w.find('́')
            homographs.append([acc_pos, tag])

        if count == 0:
            acc_pos = w.find('́')
            print(w, tag)
            tag = input('wiki morph not found, enter morph: ')
            homographs.append([acc_pos, tag])

    return homographs

def add_from_wiki(word):
    homograps = get_homographs_from_wikt(word)
    for pm in homograps:
        parser.add_homograph(word, pm)

def add_some():
    accents = []
    homographs = [
                    #['цвета', [3, 'NOUN Case=Gen|Gender=Masc|Number=Sing']],
                    #['города', [6, 'NOUN Case=Nom|Gender=Masc|Number=Plur']],
                  ]
    remove = []

    for x in remove:
        parser.accents.pop(x, None)
        parser.homographs.pop(x, None)

    for w in accents:
        pos = w.find('+')
        w = w.replace('+', '')
        parser.add_accent(w, pos)

    for w, pms in homographs:
        parser.add_homograph(w, pms)

if __name__ == "__main__":
    parser = Parser()
    parser.load()
    # add_from_wiki('дела')
    add_some()
    # parser.accents.pop('большие', None)
    # parser.homographs.pop('большие', None)
    # parser.homographs2.add('порочных')
    parser.save()