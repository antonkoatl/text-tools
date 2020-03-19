import argparse
import re

replacements = {'…': '...', '—': '-', '–': '-', '―': '-', '“': '\'', '”': '\'', '"': '\'', '«': '\'', '»': '\'',
                ' ': ' ', #No-Break Space
                }

transliteration = {'a': 'а', 'b': 'б', 'c': 'к', 'd': 'д', 'e': 'э', 'f': 'ф', 'g': 'ж',
                   'h': 'х', 'i': 'и', 'j': 'дж', 'k': 'к', 'l': 'л', 'm': 'м', 'n': 'н',
                   'o': 'о', 'p': 'п', 'q': 'кью', 'r': 'р', 's': 'с', 't': 'т', 'u': 'у',
                   'v': 'в', 'w': 'в', 'x': 'икс', 'y': 'й', 'z': 'з',
                   'A': 'А', 'B': 'Б', 'C': 'К', 'D': 'Д', 'E': 'Э', 'F': 'Ф', 'G': 'Ж',
                   'H': 'Х', 'I': 'И', 'J': 'ДЖ', 'K': 'К', 'L': 'Л', 'M': 'М', 'N': 'Н',
                   'O': 'О', 'P': 'П', 'Q': 'КЬЮ', 'R': 'Р', 'S': 'С', 'T': 'Т', 'U': 'У',
                   'V': 'В', 'W': 'В', 'X': 'ИКС', 'Y': 'Й', 'Z': 'З',
                   }

sentences = []
p = re.compile(r'(?=(?:[\']|( -))?[А-Яа-яЁё0-9́́])'
               r'((?:[^!?.]|(?:[.?!\']+ - [а-яё́]))+)'
               r'(\'?[.!?]+\'?|(?=\n)|(?=$))')


def prepare_sentences(lines, keep_dash=False, min_len=50):
    sentences = []
    for line in lines:
        if len(line) == 0: continue

        line = re.sub(' +', ' ', line)

        for k in replacements:
            line = line.replace(k, replacements[k])

        if not keep_dash:
            line = line.replace(' - ', ' ')
            line = line.replace('- ', ' ')
            line = line.replace(' -', ' ')

        for key in transliteration:
            line = line.replace(key, transliteration[key])

        s = [''.join(x) for x in p.findall(line)]

        new_s = []

        while len(s) > 0:
            line = ''
            while len(line) < min_len and len(s) > 0:
                line += s.pop(0) + ' '
            line = line[:-1]

            new_s.append(line)

        sentences += new_s

    return sentences

if __name__ == "__main__":
    prepare_sentences([
                          'Над ним потеша́ются, он…     Белоголо́вый медве́дь встал на дыбы́― и попёр с рёвом:    ― Кортому…   Где Кортома?    Е. И. Замятин. Север'],
                      True)
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('file', metavar='F', help='file to open')
    args = parser.parse_args()

    with open(args.file, encoding='utf-8') as f:
        lines = f.readlines()
        sentences = prepare_sentences(lines)

    with open(args.file.replace('.txt', '-sentences.txt'), 'w', encoding='utf-8') as f:
        for s in sentences:
            f.write(s)
            f.write('\n')

    for s in sentences:
        print(s)
