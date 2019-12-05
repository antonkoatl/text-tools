import re

import pymorphy2 as pymorphy2

from dict_parser import Parser, count_vovels, get_first_vovel_pos, compare_tags
from text_prepare_sentences import prepare_sentences

acc_dict = Parser()
acc_dict.load()

from wiktionaryparser import WiktionaryParser
parser = WiktionaryParser()
parser.set_default_language('russian')

# import maru
# analyzer = maru.get_analyzer(tagger='rnn', lemmatizer='pymorphy')

_stress_vowels = {'á': 'а', 'ó': 'о', 'é': 'е', 'ý': 'у',
                  'а́': 'а', 'и́': 'и', 'у́': 'у', 'э́': 'э', 'о́': 'о', 'ю́': 'ю', 'я́': 'я', 'ы́': 'ы', 'е́': 'е',
                  'А́': 'А', 'И́': 'И', 'У́': 'У', 'Э́': 'Э', 'О́': 'О', 'Ю́': 'Ю', 'Я́': 'Я', 'Ы́': 'Ы', 'Е́': 'Е'}
_stress_vowels_inv = {v: k for k, v in _stress_vowels.items()}

p = re.compile('[А-Яа-яЁё' + ''.join(_stress_vowels) + '-]+')

morph = pymorphy2.MorphAnalyzer()
from rnnmorph.predictor import RNNMorphPredictor
predictor = RNNMorphPredictor(language="ru")

from russian_g2p.Accentor import Accentor
your_accentor = Accentor(mode='many')

def serach_wiki(word):
    root_text = your_accentor.load_wiki_page(word)
    if root_text != None:
        cur_accented_wordforms = sorted(your_accentor.get_simple_form_wiki(root_text, word))
        return cur_accented_wordforms
    return []



def get_accent(word, words, sentence):
    if 'ё' in word or any(s in word for s in _stress_vowels): return -1
    vovels = count_vovels(word)
    if vovels == 0: return -1
    if vovels == 1: return get_first_vovel_pos(word)

    if word in acc_dict.homographs2:
        return acc_dict.accents.get(word, -2)

    if word in acc_dict.accents:
        return acc_dict.accents[word]

    if word in acc_dict.homographs:
        forms = predictor.predict(words)
        # forms2 = list(analyzer.analyze(words))

        index = -1
        for i, w in enumerate(words):
            if w == word:
                index = i
                break

        if index == -1:
            for i, w in enumerate(words):
                if w.lower() == word:
                    index = i
                    break

        form = forms[index]
        # form2 = forms2[index]

        if form.score < 0.6:
            print('resolved by moprhrnn, but score is too low', word, form, sentence)
            # return -1

        for m in acc_dict.homographs[word][1]:
            if compare_tags(m.split()[0], m.split()[1] if len(m.split()) > 1 else '', form.pos, form.tag):
                pos = acc_dict.homographs[word][1][m]
                print('resolved by moprhrnn', word, pos, sentence)
                return pos

        print(form, '\n', 'form2', '\n', acc_dict.homographs[word][1])
        return -2

    if word[0].isupper():
        return get_accent(word.lower(), words, sentence)

    wiki_data = serach_wiki(word)

    if len(wiki_data) == 1:
        if wiki_data[0].count('+') == 1:
            pos = wiki_data[0].find('+')
            print('resolved by wikidict', word, wiki_data, sentence)

            acc_dict.add_accent(word, pos)
            return pos
        else:
            print('found by wikidict, not resolved', word, wiki_data, sentence)

    # if len(wiki_data) > 1:
    #     for item in wiki_data:
    #         if item.count('+') == 1:
    #             pos = item.find('+')
    #             acc_dict.add_homograph(word, [pos, None])
    #
    #     print('new variants by wikidict', word, wiki_data, sentence)
    #     return get_accent(word, words, sentence)

    # if word in simple_words_dawg:
    #     pos = simple_words_dawg[word]
    #     print('resolved by simple_words_dawg', word, pos, sentence)
    #     return pos

    pos = your_accentor.do_accents([[word]])

    return -2

if __name__ == "__main__":
    fname = r'D:\syn\NMDS\1\Азимов Айзек. Движущая сила.txt'

    with open(fname, encoding='utf-8') as f:
        lines = f.readlines()

    sentences = prepare_sentences(lines)

    sentences_acc = []
    for sentence in sentences:
        words = [x for x in p.findall(sentence)]
        sentence_acc = sentence

        for word in words:
            if len(word) == 1: continue
            pos = get_accent(word, words, sentence)

            if pos == -1: continue

            if pos == -2:
                print(word, sentence, acc_dict.homographs[word] if word in acc_dict.homographs else None)
                print('Введите ударение:')
                pos = int(input())

            m = re.search(r'([^а-яёА-ЯЁ́]|^)(' + word + r')([^а-яёА-ЯЁ́]|$)', sentence_acc)
            if m is None:
                print(sentence, word)
            sentence_acc = sentence_acc[:m.start(2)] + word[:pos-1] + _stress_vowels_inv[word[pos-1]] + word[pos:] + sentence_acc[m.end(2):]

        sentences_acc.append(sentence_acc)
        print(sentence_acc)

    with open(fname.replace('.txt', '-prepared.txt'), 'w', encoding='utf-8') as f:
        for i, s in enumerate(sentences_acc):
            if i > 0: f.write('\n')
            f.write(s)

    acc_dict.save_if_changed()