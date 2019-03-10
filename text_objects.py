from enum import Enum

import spell_fixer

class LineType(Enum):
    CENTRE = 1
    TABLE = 2
    PARA = 3
    HEADER = 4
    FOOTER = 5


class Rectangle:
    def __init__(self, values):
        self.x1 = values[0]
        self.y1 = values[1]
        self.x2 = values[2]
        self.y2 = values[3]

    def copy(self):
        return Rectangle([self.x1, self.y1, self.x2, self.y2])

    # sort in vertically
    def __gt__(self, value):
        return self.y1 > value.y1

    # merge two rectangles to get largest possible rectangles
    def merge(self, value):
        self.x1 = min(self.x1, value.x1)
        self.y1 = min(self.y1, value.y1)
        self.x2 = max(self.x2, value.x2)
        self.y2 = max(self.y2, value.y2)

    def __str__(self):
        return " ".join(map(str, [self.x1, self.y1, self.x2, self.y2]))


class Word:

    def __init__(self, value, box):
        self.value = value
        self.box = box
        self.row_num = 0
        self.col_num = 0

    def __str__(self):
        return self.value

    # sort from left to right
    def __gt__(self, value):
        return self.box.x1 > value.box.x1

    # concatenate text and merge box
    def merge(self, other):
        self.value += " " + other.value
        self.box.merge(other.box)


class Line:

    def __init__(self, word=None):
        if not word:
            self.box = None
            self.words = []
        else:
            self.box = word.box.copy()
            self.words = [word]
        self.row_num = 0
        self.type = -1

    # add words to list and change bounding box accordingly
    def add_word(self, word):
        # if it is the first word make bounding box same as word
        if not self.words:
            self.box = word.box.copy()
        else:
            if word.box.y1 < self.box.y1:
                self.box.y1 = word.box.y1
            if self.box.y2 < word.box.y2:
                self.box.y2 = word.box.y2

        self.words.append(word)
        

    # get word from list of words
    def __getitem__(self, item):
        return self.words[item]

    # iterate over list of words
    def __iter__(self):
        return self.words.__iter__()

    # sort lines vertically
    def __gt__(self, value):
        return self.box.y1 > value.box.y1

    # debugging convenience will affect performance
    def __str__(self):
        return " ".join([word.__str__() for word in self.words])


class Column:

    def __init__(self, word):
        self.words = [word]
        self.box = word.box.copy()
        self.col_num = 0

    # add word to column and modify bounding box
    def add_word(self, word):
        self.words.append(word)
        if word.box.x1 < self.box.x1:
            self.box.x1 = word.box.x1
        if self.box.x2 < word.box.x2:
            self.box.x2 = word.box.x2

    # get item from list of words
    def __getitem__(self, item):
        return self.words[item]

    # iterate over words in a column
    def __iter__(self):
        return self.words.__iter__()

    # sort columns from left to right
    def __gt__(self, value):
        return self.box.x1 > value.box.x1

    # debugging convenience will affect performance
    def __str__(self):
        return "\n".join([word.__str__() for word in self.words])


class Paragraph:

    def __init__(self, line):
        self.lines = [line]
        self.box = line.box

    # add lines to paragraph and modify bounding box
    def add_line(self, line):
        self.lines.append(line)
        self.box.merge(line.box)

    # get line from list of lines
    def __getitem__(self, item):
        return self.lines[item]

    # iterate over lines in paragraph
    def __iter__(self):
        return self.lines.__iter__()

    # sort vertically
    def __gt__(self, value):
        return self.box.y1 > value.box.x1


# group words that are horizontally in the same line
def get_lines(page_element, margin=5):
    lines = []
    page_box = Rectangle(
        list(map(float, page_element.attrib["bbox"].split(","))))
    for text_box in page_element.getchildren():
        if not text_box.tag == "textbox":
            continue
        for text_line in text_box.getchildren():
            if not text_line.tag == "textline":
                continue
            bbox = Rectangle(list(map(float, text_line.attrib["bbox"].split(","))))
            value = ''.join(
                [text_char.text if text_char.text else " " for text_char in text_line.getchildren()])
            value = value.strip()
            if value[0] == '(' or value[-1] == ')':
                value.rstrip(')')
                value.lstrip('(')
                value = "-" + value
            word = Word(value, bbox)
            added = False
            for line in lines:
                # check within a margin of error if the text_line can be added in an exisiting line
                if (line.box.y1 - margin < bbox.y1 < line.box.y1 + margin) and (line.box.y2 - margin < bbox.y2 < line.box.y2 + margin):
                    line.add_word(word)
                    added = True

            if not added:
                lines.append(Line(word))

    return lines

# filter words and remake lines
def check_fix_spellings(lines, types):
    new_lines = []
    for line in lines:
        if line.type not in types:
            new_lines.append(line)
            continue
        new_line = Line()
        new_line.row_num = line.row_num
        new_line.type = line.type
        for word in line:
            if spell_fixer.spelling_accept(word.value):
                new_line.add_word(Word(spell_fixer.spelling_fixer(word.value), word.box))
        # if new line contains words after filtering add it to list
        if new_line.words:
            new_lines.append(new_line)
    
    return new_lines


# take lines of words and create columns from them
def get_columns(lines, margin=20):
    columns = []
    for line in lines:
        for word in line:
            added = False
            for column in columns:
                if column.box.x1 - margin < word.box.x1 < column.box.x1 + margin \
                        or column.box.x2 - margin < word.box.x2 < column.box.x2 + margin \
                        or column.box.x1 + margin < word.box.x1 and word.box.x2 < column.box.x2:
                    column.words.append(word)
                    added = True
            if not added:
                columns.append(Column(word))
    return columns

def get_paragraphs(lines, margin=20):
    paras = []
    para = []
    for i, line in enumerate(lines):
        if i < len(lines) - 1:
            para.append(line)
            if line.box.y1 - margin > lines[i+1].box.y2:
                paras.append(para)
                para = []
        else:
            para.append(line)
            paras.append(para)

    return paras

# merge closely spaced words
def merge_words(lines, margin=15):
    new_lines = []
    for i, line in enumerate(lines):
        line.words.sort()
        merger = line.words[0]
        new_line = Line()
        for i, word in enumerate(line.words[1:]):
            if merger.box.x2 + margin > word.box.x1:
                merger.merge(word)
            else:
                new_line.add_word(merger)
                merger = word
        new_line.add_word(merger)
        new_lines.append(new_line)
    return new_lines


def centre_aligned(line, page_box, margin=15, cutoff=0.8):
    mid = (page_box.x1 + page_box.x2)/2
    width = page_box.x2 - page_box.x1

    if line.box.x1 < mid < line.box.x2:
        left = mid - line.box.x1
        right = line.box.x2 - mid
        if (-margin < left - right < margin) and ((line.box.x2 - line.box.x1)/width < cutoff):
            return True

    return False
