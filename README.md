# Profit and Loss Statement Processing
 
## Usage:
To start the dockerfile <INSERT FILE NAME HERE>,
```
docker start
docker run
```
Inside the docker, generate text enabled pdfs from ocr by running,
```shell
python2 driver_ocr.py <file_name>
```
where file_name is the path to the file or the directory

Post that, you can run the file with the following options,
1. To extract documents (docx) from a single pdf, run
```shell
python3 driver.py <file_name>
```

2. To extract documents (docx) from all files in a directory, run
```shell
python3 driver.py <dir_path>
```

3. To extract documents (docx) with densely spaced text, run
```shell
python3 driver.py <dir_path> -m=dense
```

4. To extract documents (docx) with sparsely spaced text, run
```shell
python3 driver.py <dir_path> -m=sparse
```

5. To extract csv of a P&L sheet, run
```shell
python3 driver.py <dir_path> -c
```


**Note:** The -m option allows to improve accuracy based on the type of document which has to be processed


## License:
GNU GPLv3 open source license
