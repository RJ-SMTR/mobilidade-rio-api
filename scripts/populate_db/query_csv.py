# query csv file

import csv
import os

def query_csv(_csv_file, contains_word: list, and_contains_word: list=[], not_contains_word: list = []):
    """Query csv file and return a list with the lines that contains the words in the list 'contains_word'"""
    with open(_csv_file, 'r', encoding='utf-8') as _csv_file:
        csv_reader = csv.reader(_csv_file, delimiter=';')
        line_count = 0
        lines = []
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                for word in contains_word:
                    if word in row[0] and not any(word in row[0] for word in not_contains_word)\
                            and (any(word in row[0] for word in and_contains_word) or not and_contains_word):
                        lines.append(row)
                        break
                line_count += 1
        return lines


if __name__ == '__main__':
    csv_file = os.path.join(os.path.dirname(__file__), 'temp.txt')
    print("Result:")
    result = query_csv(csv_file, [
        'O0309AAN0AVDU01',  # 1
        'O0105AAA0AVDU01',  # 4
        'O0041CAA0AIDU01',  # 1
        'O0538AAN0AVDU01',  # 1
        'O0410AAA0AIDU01',  # 28
        'O0538AAA0AVDU01',  # 8
        'O0409AAA0AIDU01',  # 29
        'O0583AAA0ACDU01',  # 10
        'O0548AAA0AIDU01',  # 13
        'O0309AAA0AVDU01',  # 34
        ],  # = 128
        and_contains_word=[
        '2028O00023C0'
        ],
        # not_contains_word=[
        # ]
        )
    # write to result.txt
    with open('result.txt', 'w') as result_file:
        # write total at first line
        result_file.write(str(len(result)) + '\n')
        for line in result:
            result_file.write(str(line) + '\n')
