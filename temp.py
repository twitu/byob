from tkinter import *
import argparse
import sys
import os

from os.path import join
from generate_readables import generate_readables
from generate_csv import process_csv
from generate_doc import process_doc

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


def generateCSV():
    if os.path.exists(pathName.get()) and os.path.isdir(pathName.get()):
        working_dir = pathName.get()
        files = list(filter(lambda x: x.endswith(".pdf"), os.listdir(working_dir)))
    elif os.path.exists(pathName.get()) and os.path.isfile(pathName.get()):
        working_dir = os.path.dirname(pathName.get())
        files = [os.path.basename(pathName.get())]
    else:
        statusLbl['text'] = "Status: Entered file / directory path is not valid"
        return
    generate_readables(working_dir, files)

    for file_name in files:
        name = file_name.split(".")[0]
        statusLbl['text'] = "Status: Generating csv from {}".format(file_name)
        process_csv(
            join(working_dir, "xml", name + ".xml"),
            join(working_dir, "csv", name + ".csv")
        )
    statusLbl['text'] = "Status: Generated successfully"


def generateDoc():
    if os.path.exists(pathName.get()) and os.path.isdir(pathName.get()):
        working_dir = pathName.get()
        files = list(filter(lambda x: x.endswith(".pdf"), os.listdir(working_dir)))
    elif os.path.exists(pathName.get()) and os.path.isfile(pathName.get()):
        working_dir = os.path.dirname(pathName.get())
        files = [os.path.basename(pathName.get())]
    else:
        statusLbl['text'] = "Status: Entered file / directory path is not valid"
        return
    generate_readables(working_dir, files)
    for file_name in files:
        name = file_name.split(".")[0]
        statusLbl['text'] = "Status: Converting {} to doc".format(file_name)
        process_doc(
            join(working_dir, "xml", name + ".xml"),
            join(working_dir, "doc", name + ".doc"),
            parsing_modes[args.mode]
        )
    statusLbl['text'] = "Status: Converted successfully"

window = Tk()
rdb_var = IntVar()
rdb_var.set(1)

window.title("Balance Sheet Manager")
window.geometry('400x400')

lbl = Label(window, text = 'File / directory path:')
lbl.grid(column = 0, row = 0, pady = 10, padx = 10)

pathName = Entry(window)
pathName.grid(column = 1, row = 0, pady = 10, padx = 10)

rd1 = Radiobutton(window, text="Default", variable = rdb_var, value = 1, padx = 10, pady = 5)
rd2 = Radiobutton(window, text="Sparse", variable = rdb_var, value  = 2, padx = 10, pady = 5)
rd3 = Radiobutton(window, text="Dense", variable = rdb_var, value = 3, padx = 10, pady = 5)
lbl2 = Label(window, text = '')

rd1.grid(column = 0, row = 1)
rd2.grid(column = 0, row = 2)
rd3.grid(column = 0, row = 3)
lbl2.grid(column = 0, row = 4)

btn = Button(window, text = "Generate Docx", command = generateDoc, padx = 10, pady = 5)
btn2 = Button(window, text = "Generate CSV", command = generateCSV, padx = 10, pady = 5)

btn.grid(column = 0, row = 5)
btn2.grid(column = 1, row = 5)
statusLbl = Label(window, text = 'Status: Waiting to enter file / directory path')
statusLbl.grid(row = 6, pady = 10, padx = 10, columnspan = 2)

window.mainloop()