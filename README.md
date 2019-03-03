# Profit and Loss Statement Processing

## Installation

Please use virtualenv to setup the environment for running the scripts. The ocr and the parsing scripts require two different virtual environments

```
virtualenv -p python2 byob_ocr
source ./byob_ocr/bin/activate
pip install -r requirements_ocr.txt
deactivate
```

```
virtualenv -p python3 byob_parser
source ./byob_parser/bin/activate
pip install -r requirements_parser.txt
deactivate
```

## Usage:

With the `byob_ocr` environment activated
```shell
python ocr/driver_ocr.py <file_name>
```
where file_name is the path to the file or the directory. This will convert the pdf to text searchable pdf

With the `byob_parser` environment activated, you can run the script with the following options,
1. To extract documents (docx) from a single pdf, run
```shell
python parser/driver.py <file_name>
```

2. To extract documents (docx) from all files in a directory, run
```shell
python parser/driver.py <dir_path>
```

3. To extract documents (docx) with densely spaced text, run
```shell
python parser/driver.py <dir_path> -m=dense
```

4. To extract documents (docx) with sparsely spaced text, run
```shell
python parser/driver.py <dir_path> -m=sparse
```

5. To extract csv of a P&L sheet, run
```shell
python parser/driver.py <dir_path> -c
```


**Note:** The -m option allows to improve accuracy based on the type of document which has to be processed


## License:
GNU GPLv3 open source license
