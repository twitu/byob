import os
from os.path import join


def create_ocr(file_name):
    os.system('pypdfocr ' + file_name)
    op_file_name = file_name.split('.')[0] + '_ocr.pdf'
    os.rename(op_file_name, 'ocr_pdfs/' + op_file_name)


def create_xml(file_name):
    os.system('pdf2txt.py -t xml ' + file_name + ' > ' + file_name.split('.')[0] + '.xml')
    op_file_name = file_name.split('.')[0] + '.xml'
    os.rename(op_file_name, 'xml/' + op_file_name)


def generate_readables(dir_path):
    '''
    convert all pdfs in dir_path in 3 formats,
    1. text readable pdfs, stored in ocr_pdfs/
    2. txt from pdf, stored in textfiles/
    3. xml from pdf, stored in xml/

    Requires pdf2txt.py
    '''

    if os.path.isdir(dir_path):
        os.chdir(dir_path)
        files = os.listdir()
    else:
        files = [dir_path]

    for file_name in files:
        if 'ocr_pdfs' in os.listdir():
            if file_name.split('.')[0] not in os.listdir('ocr_pdfs'):
                create_ocr(file_name)
        else:
            os.mkdir('ocr_pdfs')
            create_ocr(file_name)

        if 'xml' in os.listdir():
            if file_name.split('.')[0] not in os.listdir('xml'):
                create_xml(file_name)
        else:
            os.mkdir('xml')
            create_xml(file_name)
