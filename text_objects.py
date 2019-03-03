from enum import Enum

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
        return " ".join(map(str, [x1, y1, x2, y2]))


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
        return self.box.x1 > self.box.x2

    # concatenate text and merge box
    def merge(self, other):
        self.value += " " + other.value
        self.box.merge(other.box)


class Line:

    def __init__(self, word):
        self.box = word.box
        self.words = [word]
        self.row_num = 0
        self.type = -1

    # add words to list and change bounding box accordingly
    def add_word(self, word):
        self.words.append(word)
        if word.box.y1 < self.box.y1:
            self.box.y1 = word.box.y1
        if self.box.y2 < word.box.y2:
            self.box.y2 = word.box.y2

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
        self.box = word.box
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
