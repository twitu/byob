# Convert PDF to DOC and CSV

The application can convert scanned pdfs to docs and can extract table data to store in the form of a csv. The application is tuned to work on a specific structure of pdfs (similar to finanical entries)

## Installation

Supports installation using docker
```
git pull https://github.com/twitu/byob
cd byob
docker build -t byob-app .
```

It can also be built from source  
(Note: instructions are for bash only)
```
git pull https://github.com/twitu/byob
cd byob
virtualenv -p python3 byob_env
. byob_env/bin/activate
sudo apt-get install -y tesseract-ocr
python3 -m pip install -r requirements.txt
```
## Usage:

Note: use the [documentation](https://docs.docker.com/storage/volumes/) to mount the files/directory you want to convert

With the `byob_env` environment activated
```shell
python3 driver.py <arguments>
```
With docker use
```shell
docker run --rm byob-app:latest <arguments>
```

Use `-h` argument to get instructions for help

## License:
GNU GPLv3 open source license
