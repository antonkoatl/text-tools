import argparse
import re

replacements = {'…': '...', '—': '-', '–': '-', '“': '\'', '”': '\'', '"': '\'', }

sentences = []
p = re.compile(r'(?=\'?[А-Яа-яЁё0-9́]|- [А-ЯЁ0-9́])'
               r'((?:[А-Яа-яЁё0-9́,\-:;\' ́]|(?:[.?!\']+ - [а-яё]))+)'
               r'(\'?[.!?]+\'?|(?=\n))')

def prepare_sentences(lines):
    sentences = []
    for line in lines:
        if len(line) == 0: continue

        for k in replacements:
            line = line.replace(k, replacements[k])

        s = [''.join(x) for x in p.findall(line)]

        new_s = []

        while len(s) > 0:
            line = ''
            while len(line) < 50 and len(s) > 0:
                line += s.pop(0) + ' '
            line = line[:-1]

            new_s.append(line)

        sentences += new_s

    return sentences

if __name__ == "__main__":
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
