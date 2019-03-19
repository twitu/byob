import os

from os.path import join
from pypdfocr.pypdfocr import PyPDFOCR


def generate_readables(working_dir, files):
    '''
    convert all pdfs in dir_path in 3 formats,
    1. text readable pdfs, stored in ocr/
    2. xml from pdf, stored in xml/

    Requires pdf2txt.py
    '''

    ocr_dir = join(working_dir, "ocr")
    xml_dir = join(working_dir, "xml")
    doc_dir = join(working_dir, "doc")
    xml_dir = join(working_dir, "xml")
    converter = PyPDFOCR()

    # generate readable pdf using ocr library
    if not os.path.isdir(ocr_dir):
        print("Creating OCR directory")
        os.mkdir(ocr_dir)
    if not os.path.isdir(xml_dir):
        print("Creating XML directory")
        os.mkdir(xml_dir)
    if not os.path.isdir(doc_dir):
        print("Creating DOC directory")
        os.mkdir(doc_dir)

    for i, file_name in enumerate(files):
        output_file = file_name.split(".")[0] + "_ocr.pdf"
        output_path = join(ocr_dir, output_file)

        # do not convert if file of the same name is already converted
        if output_file not in os.listdir(ocr_dir):
            print("Converting {} to ocr pdf".format(file_name))
            file_path = join(working_dir, file_name)
            # print error message and ignore file if cannot convert ocr
            try:
                converter.go(file_path)
            except:
                print("Could not convert {} to OCR pdf".format(file_name))
                del files[i]
            os.rename(join(working_dir, output_file), output_path)
        else:
            print("OCR version for {} exists".format(file_name))

    # generate parsable xml files from ocr pdf


    for file_name in files:
        input_path = join(ocr_dir, file_name.split(".")[0] + "_ocr.pdf")
        output_file = file_name.split(".")[0] + ".xml"
        output_path = join(xml_dir, output_file)

        # do not convert if file of the same name is already converted
        if output_file not in os.listdir(xml_dir):
            print("Converting {} to XML file".format(file_name))
            os.system('pdf2txt.py -t xml ' + input_path + ' > ' + output_path)
        else:
            print("XML version for {} exists".format(file_name))
