import xml.etree.ElementTree as tree
import csv

class Rectangle:

    def __init__(self, values):
        self.x1 = values[0]
        self.y1 = values[1]
        self.x2 = values[2]
        self.y2 = values[3]

    def __gt__(self, value):
        return self.y1 > value.y1

    def merge(self, value):
        self.x1 = min(self.x1, value.x1)
        self.y1 = min(self.y1, value.y1)
        self.x2 = max(self.x2, value.x2)
        self.y2 = max(self.y2, value.y2)


class Text:

    def __init__(self, value, box):
        self.value = value
        self.box = box
        self.row_num = 0
        self.col_num = 0

    def __str__(self):
        return self.value

    def __gt__(self, value):
        return self.col_num > value.col_num

    def merge(self, other):
        self.value += " " + other.value
        self.box.merge(other.box)


class Line:

    def __init__(self, word):
        self.box = word.box
        self.words = [word]
        self.row_num = 0

    def add_word(self, word):
        self.words.append(word)
        if word.box.y1 < self.box.y1:
            self.box.y1 = word.box.y1
        if self.box.y2 < word.box.y2:
            self.box.y2 = word.box.y2

    def __iter__(self):
        return self.words.__iter__()

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


    def add_word(self, word):
        self.words.append(word)
        if word.box.x1 < self.box.x1:
            self.box.x1 = word.box.x1
        if self.box.x2 < word.box.x2:
            self.box.x2 = word.box.x2

    def __iter__(self):
        return self.words.__iter__()

    def __gt__(self, value):
        return self.box.x1 > value.box.x1

    # debugging convenience will affect performance
    def __str__(self):
        return "\n".join([word.__str__() for word in self.words])


def get_lines(page_element, margin=5):
    lines = []
    page_box = Rectangle(list(map(float, page_element.attrib["bbox"].split(","))))
    for text_box in page_element.getchildren():
        if not text_box.tag == "textbox": continue
        for text_line in text_box.getchildren():
            if not text_line.tag == "textline": continue
            bbox = Rectangle(list(map(float, text_line.attrib["bbox"].split(","))))
            value = ''.join([text_char.text if text_char.text else " " for text_char in text_line.getchildren()])
            value = value.strip()
            word = Text(value, bbox)
            if filter_centre_word(page_box, word):
                continue
            added = False
            for line in lines:
                # check within a margin of error if the text_line can be added in an exisiting line
                if line.box.y1 - margin < bbox.y1 < line.box.y1 + margin and line.box.y2 - margin < bbox.y2 < line.box.y2 + margin:
                    line.add_word(word)
                    added = True
            
            if not added:
                new_line = Line(word)
                lines.append(new_line)

    return lines


# check if box passes centre line and check if it is greater than 20% of page width
def filter_centre_word(page_box, word):
    centre = page_box.x2/2
    if (word.box.x1 < centre < word.box.x2) and \
        (word.box.x2 - word.box.x1)/(page_box.x2 - page_box.x1) > 0.15:
        return True
    else:
        return False


def get_columns(lines, margin=10):
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
                new_column = Column(word)
                columns.append(new_column)
    return columns

def merge_words(line, margin=10):
    new_line = []
    merger = line.words[0]
    for i, word in enumerate(line.words[1:]):
        if merger.box.x2 + margin > word.box.x1:
            merger.merge(word)
        else:
            new_line.append(merger)
            merger = word
    new_line.append(merger)
    line = new_line
    

if __name__ == "__main__":
    file_name = "data.xml"
    xml_file = tree.parse(file_name).getroot()
    page = xml_file.getchildren()[0]
    lines = get_lines(page, 5)
    lines.sort(reverse=True)
    columns = get_columns(lines)
    columns.sort()
    for i, column in enumerate(columns):
        for word in column.words:
            word.col_num = i

    with open("table.csv", "w") as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        for line in lines:
            line.words.sort()
            max_col = line.words[-1].col_num
            csv_line = [None]*(max_col + 1)
            for word in line.words:
                csv_line[word.col_num] = word.value
            print(csv_line)
            csvwriter.writerow(csv_line)


#Merging single line objects to form multi line objects
class Para:

    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

def merge_lines():

    multiline_objs = []
    vertical_gap = 5
    prev_line = None

    for line_obj in lines:
       for multi_line in multiline_objs:
        if line_obj.y2 < (prev_line.y2 - vertical_gap) and line_obj.y2 > (prev_line.y2 + vertical_gap):
            Para1 = Para()  
        else:
           # new_line = 
            continue
        prev_line = line_obj 
