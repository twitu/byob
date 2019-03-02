import os
from symspellpy.symspellpy import SymSpell, Verbosity

term_index = 0
count_index = 1
prefix_length = 7
max_ed_dictionary = 3

sym_spell = SymSpell(max_ed_dictionary, prefix_length)
dictionary_path = os.path.join(os.path.dirname(__file__), "dataset/dictionary-en.txt")

UNIMPORTANT_SINGLES = [
    '.',
    ',',
    '('
]

PL_LINES = [
    ['PROFIT', 'LOSS', 'ACCOUNT'],
    ['STATEMENT', 'COMPREHENSIVE', 'INCOME'],
    ['ABRIDGED', 'PROFIT', 'LOSS', 'ACCOUNT'],
    ['PROFIT', 'LOSS', 'ACCOUNT'],
    ['INCOME', 'EXPENDITURE'],
    ['INCOME', 'STATEMENT'],
    ['OTHER', 'COMPREHENSIVE', 'INCOME'],
    ['STATEMENT', 'FINANCIAL', 'ACTIVITES'],
    ['STATEMENT', 'INCOME', 'RETAINED', 'EARNINGS']
]

HEADER_ENDINGS = [
    ['FOR', 'THE', 'YEAR', 'ENDED'],
    ['FOR', 'THE', 'PERIOD', 'ENDED'],
    ['YEAR', 'ENDED'],
]

FOOTERS = [
    ['NOTES', 'FORM', 'PART', 'THESE', 'FINANCIAL', 'STATEMENTS'],
    ['PAGE']
]


if not sym_spell.load_dictionary(dictionary_path, term_index, count_index):
    print("Dictionary file not found")
    exit(0)


def spelling_fixer(word):
    '''
    Takes a string and returns its spell corrected value

    '''
    max_ed_lookup = 2
    suggestions = sym_spell.lookup(word, Verbosity.CLOSEST,
                                   max_ed_lookup)
    
    if not suggestions:
        return word
    else:
        return suggestions[0].term


def spelling_accept(word):
    '''
    Takes a string and returns a bool telling
    whether the word should be accepted as a
    valid word or not
    '''
    if len(word) == 1 and word != 'a' and word.isalpha():
        return False
    if not any(char.isalpha() for char in word) and len(word) <= 3:
        return not any(not char.isdigit() for char in word)
    return True


def gen_filter(line, match_lines):
    '''
    return True if line has a match with any of the match_lines to the profit and loss table
    '''
    for match_line in match_lines:
        status = True
        for word in line:
            if word not in match_line:
                status = False
        if status:
            return True

        return False


def p_l_filter(lines):
    '''
    return True if any of the lines is related to p and l
    '''
    for line in lines:
        if gen_filter(line, PL_LINES):
            return True
    return False

        
def set_headers(lines):
    '''
    (Should) Set headers on lines which could be headers
    IMPORTANT:
        1. Send the lines in order of row_num
        2. Works only for p & l tables
    status:
        0 = header continues
        1 = possible header reached
    '''
    status = 0
    for line in lines:
        if is_in_top_quarter(line):
            if gen_filter(line, PL_LINES):
                status = 1
                line.type = 4
            elif gen_filter(line, HEADER_ENDINGS):
                line.type = 4
                break
            elif status == 1:
                break
            else:
                line.type = 4
        else:
            break

def set_footers(lines):
    '''
    (Should) reutrn the lines which are a part of footer
    IMPORTANT: 
        1. Send the lines in order of row_num
        2. Works only for p & l tables
    status:
        0 = footer continues
        1 = possible footer reached
    '''
    lines.sort(reverse = True)
    status = 0
    for line in lines:
        if is_in_lowest_quarter(line):
            if gen_filter(line, FOOTERS):
                status = 1
                line.type = 5
            elif status == 1:
                if gen_filter(line, FOOTERS):
                    line.type = 5
                break
        else:
            break


def is_in_lowest_quarter(line):
    '''
    Returns true if the line is in the lowermost quarter
    HACK: Terribly hard coded value for y1
    '''
    if line.box.y1 < 160: 
        return True
    return False


def is_in_top_quarter(line):
    '''
    Returns true if the line is in the uppermost quarter
    HACK: Terribly hard coded value for y1
    '''
    if line.box.y1 > 700:
        return True
    return False