import os
from os.path import join


def create_ocr(file_name):
    os.system('pypdfocr ' + file_name)
    op_file_name = file_name.split('.')[0] + '_ocr.pdf'
    os.rename(op_file_name, 'ocr_pdfs/' + op_file_name)


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