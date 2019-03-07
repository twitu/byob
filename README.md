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
sudo apt-get install -y tesseract-ocr python3-tk
python3 -m pip install -r requirements.txt
```
## Usage:

With the `byob_env` environment activated
```shell
python3 driver.py
```
With docker use
```shell
docker run --rm -v /tmp/.X11-unix:/tmp/.X11-unix byob-app:latest
```

## License:
GNU GPLv3 open source license
