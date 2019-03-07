from tkinter import *
from tkinter import filedialog
import argparse
import sys
import os

from os.path import join
from generate_readables import generate_readables
from generate_csv import process_csv
from generate_doc import process_doc
from functools import partial


# global variable for storing path from file dialog box
input_path = ''

# list of parsing modes
parsing_modes = {
    'sparse': {
        'r_margin': 20,
        'c_margin': 10,
        'l_margin': 20,
        'm_margin': 20,
        'p_margin': 20
    },
    'dense': {
        'r_margin': 20,
        'c_margin': 10,
        'l_margin': 20,
        'm_margin': 10,
        'p_margin': 20
    },
    'standard':{
        'r_margin': 20,
        'c_margin': 10,
        'l_margin': 20,
        'm_margin': 15,
        'p_margin': 20
    }
}

# sets passed text in text box at the end
def set_status(text):
    display_status.insert(END, text + '\n')
    display_status.see(END)


def generate(is_doc):

    # check given path and set working directory for making readable files
    if os.path.exists(input_path) and os.path.isdir(input_path):
        working_dir = input_path
        files = list(filter(lambda x: x.endswith(".pdf"), os.listdir(working_dir)))
    elif os.path.exists(input_path) and os.path.isfile(input_path):
        working_dir = os.path.dirname(input_path)
        files = [os.path.basename(input_path)]
    else:
        set_status("Status: Entered file / directory path is not valid")
        return

    # log files found
    set_status("Found the following files:")
    for file in files:
        set_status(file)

    # generate readable files from pdfs i.e. ocr pdf and xml
    generate_readables(working_dir, files, set_status)

    # call function to generate csv or doc
    for file_name in files:
        name = file_name.split(".")[0]
        if is_doc:
            set_status("converting {} to doc".format(name))
            process_doc(
                join(working_dir, "xml", name + ".xml"),
                join(working_dir, "doc", name + ".doc"),
                parsing_modes[rdb_var.get()],
            )
        else:
            set_status("converting {} to csv".format(name))
            process_csv(
                join(working_dir, "xml", name + ".xml"),
                join(working_dir, "csv", name + ".csv")
            )
    
    set_status("All files converted successfully")


def get_dir_dlg():
    global input_path
    input_path = filedialog.askdirectory()

def get_file_dlg():
    global input_path
    input_path = filedialog.askopenfilename(
        title = "Select file",
        filetypes = (("pdf files","*.pdf"),("all files","*.*"))
    )

if __name__ == "__main__":
    
    window = Tk()
    rdb_var = StringVar()
    rdb_var.set("standard")

    window.title("Balance Sheet Manager")
    window.geometry('400x400')

    lbl = Label(window, text = 'File / directory path:')
    dir_path_btn = Button(window, text = "Load directory", command = get_dir_dlg)
    dir_path_btn.grid(column = 0, row = 0, pady = 10, padx = 10)

    file_path_btn = Button(window, text = 'Load File', command = get_file_dlg)
    file_path_btn.grid(column = 1, row = 0, pady = 10, padx = 10)

    rd1 = Radiobutton(window, text="Default", variable = rdb_var, value = 'standard', padx = 10, pady = 5)
    rd2 = Radiobutton(window, text="Sparse", variable = rdb_var, value  = 'sparse', padx = 10, pady = 5)
    rd3 = Radiobutton(window, text="Dense", variable = rdb_var, value = 'dense', padx = 10, pady = 5)
    lbl2 = Label(window, text = '')

    rd1.grid(column = 0, row = 1)
    rd2.grid(column = 0, row = 2)
    rd3.grid(column = 0, row = 3)
    lbl2.grid(column = 0, row = 4)

    doc_btn = Button(window, text = "Generate Docx", command = partial(generate, True), padx = 10, pady = 5)
    csv_btn = Button(window, text = "Generate CSV", command = partial(generate, False), padx = 10, pady = 5)

    doc_btn.grid(column = 0, row = 5)
    csv_btn.grid(column = 1, row = 5)
    display_status = Text(window, height = 10, width = 50)
    display_status.grid(row = 6, pady = 10, padx = 10, columnspan = 3)

    window.mainloop()
