import os
from os.path import join


def generate_readables(dir_path):
    '''
    convert all pdfs in dir_path in 3 formats,
    1. text readable pdfs, stored in ocr_pdfs/
    2. txt from pdf, stored in textfiles/
    3. xml from pdf, stored in xml/

    Requires pdf2txt.py
    '''

    os.chdir(dir_path)

    for data_file_name in os.listdir('.'):
        if '_ocr.pdf' in data_file_name:
            os.system('pdf2txt.py ' + data_file_name + ' > ' +
                      data_file_name.split('.')[0] + '.txt')
            os.system('pdf2txt.py -t xml ' + data_file_name +
                      ' > ' + data_file_name.split('.')[0] + '.xml')

    os.mkdir('textfiles')
    os.mkdir('xml')
    os.mkdir('ocr_pdfs')

    for data_file_name in os.listdir('.'):
        if '.txt' in data_file_name:
            os.rename(data_file_name, 'textfiles/' + data_file_name)
        elif '.xml' in data_file_name:
            os.rename(data_file_name, 'xml/' + data_file_name)
        elif '_ocr.pdf' in data_file_name:
            os.rename(data_file_name, 'ocr_pdfs/' + data_file_name)
