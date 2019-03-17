import os
import wordsegment
import re

from text_objects import Line, Word, Rectangle, LineType
import spell_correct

# load data for word segementation
wordsegment.load()

term_index = 0
count_index = 1
prefix_length = 7
max_ed_dictionary = 3

UNIMPORTANT_SINGLES = [
    '.',
    ',',
    '('
]

PL_LINES = [
    # add corrections for words
    ["PRONT", "LOSS", "ACCOUNT"],
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


def spelling_fixer(word):
    '''
    Takes a string and returns its spell corrected value

    '''
    words = word.split(' ')
    fixed_words = []
    for word in words:
        print(word + "***")
        if not word.isdigit():
            seg_words = wordsegment.segment(word)
        else:
            seg_words = [word]
        print(word + "***")
        for seg_index in range(len(seg_words)):
            seg_words[seg_index] = spell_correct.correction(seg_words[seg_index])
        fixed_words += seg_words
    return " ".join(fixed_words)


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
        for word in match_line:
            flag = False
            for words in line:
                if word.lower() in words.value.lower():
                    flag = True
            
            if not flag:
                status = False
                break

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
        if line.type == -1:
            continue
        if is_in_top_quarter(line):
            if gen_filter(line, PL_LINES):
                status = 1
                line.type = LineType.HEADER
            elif gen_filter(line, HEADER_ENDINGS):
                line.type = LineType.HEADER
                break
            elif status == 1:
                break
            else:
                line.type = LineType.HEADER
        else:
            break

def set_footers(lines):
    '''
    (Should) return the lines which are a part of footer
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
        if line.type == -1:
            continue
        if is_in_lowest_quarter(line):
            if gen_filter(line, FOOTERS):
                status = 1
                line.type = LineType.FOOTER
            elif status == 1:
                if gen_filter(line, FOOTERS):
                    line.type = LineType.FOOTER
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
