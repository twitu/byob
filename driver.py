from tkinter import *
from tkinter import filedialog
import argparse
import sys
import os

from os.path import join
from generate_readables import generate_readables
from generate_csv import process_csv
from generate_doc import process_doc


# Horrible code starts here

x = ''

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

def set_status(text): # Bhanuka, use this function
    T.insert(END, text)
    T.set(END)


def generateCSV():
    if os.path.exists(pathName.get()) and os.path.isdir(pathName.get()):
        working_dir = pathName.get()
        files = list(filter(lambda x: x.endswith(".pdf"), os.listdir(working_dir)))
    elif os.path.exists(pathName.get()) and os.path.isfile(pathName.get()):
        working_dir = os.path.dirname(pathName.get())
        files = [os.path.basename(pathName.get())]
    else:
        T.insert(END,"Status: Entered file / directory path is not valid")
        return
    generate_readables(working_dir, files)

    for file_name in files:
        name = file_name.split(".")[0]
        process_csv(
            join(working_dir, "xml", name + ".xml"),
            join(working_dir, "csv", name + ".csv")
        )
        T.insert(END,"Status: All files converted successfully")


def generateDoc():
    if os.path.exists(pathName.get()) and os.path.isdir(pathName.get()):
        working_dir = pathName.get()
        files = list(filter(lambda x: x.endswith(".pdf"), os.listdir(working_dir)))
    elif os.path.exists(pathName.get()) and os.path.isfile(pathName.get()):
        working_dir = os.path.dirname(pathName.get())
        files = [os.path.basename(pathName.get())]
    else:
        T.insert(END,"Status: Entered file / directory path is not valid")
        return
    generate_readables(working_dir, files)
    for file_name in files:
        name = file_name.split(".")[0]
        process_doc(
            join(working_dir, "xml", name + ".xml"),
            join(working_dir, "doc", name + ".doc"),
            parsing_modes[args.mode]
        )
    T.insert(END,"Status: All files converted successfully")


def com():
    global x
    x = filedialog.askdirectory()

def com2():
    global x
    x = filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("pdf files","*.pdf"),("all files","*.*")))


window = Tk()
rdb_var = StringVar()
rdb_var.set(1)

window.title("Balance Sheet Manager")
window.geometry('400x400')

lbl = Label(window, text = 'File / directory path:')
pathName2 = Button(window, text = "Load directory", command = com)
pathName2.grid(column = 0, row = 0, pady = 10, padx = 10)

pathName = Button(window, text = 'Load File')
pathName.grid(column = 1, row = 0, pady = 10, padx = 10)

rd1 = Radiobutton(window, text="Default", variable = rdb_var, value = 'standard', padx = 10, pady = 5)
rd2 = Radiobutton(window, text="Sparse", variable = rdb_var, value  = 'sparse', padx = 10, pady = 5)
rd3 = Radiobutton(window, text="Dense", variable = rdb_var, value = 'dense', padx = 10, pady = 5)
lbl2 = Label(window, text = '')

rd1.grid(column = 0, row = 1)
rd2.grid(column = 0, row = 2)
rd3.grid(column = 0, row = 3)
lbl2.grid(column = 0, row = 4)

btn = Button(window, text = "Generate Docx", command = generateDoc, padx = 10, pady = 5)
btn2 = Button(window, text = "Generate CSV", command = generateCSV, padx = 10, pady = 5)

btn.grid(column = 0, row = 5)
btn2.grid(column = 1, row = 5)
T = Text(window, height = 10, width = 50)
T.grid(row = 6, pady = 10, padx = 10, columnspan = 3)

window.mainloop()

# Horrible code ends here