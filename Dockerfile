FROM python:3
COPY . /byob_app
WORKDIR /byob_app
RUN apt-get update && apt-get install -y tesseract-ocr
RUN pip install -r requirements.txt
ENTRYPOINT ["python3", "driver.py"]
