FROM python:3
COPY . /byob_app
WORKDIR /byob_app
RUN apt-get update && apt-get install -y tesseract-ocr python3-tk
RUN pip install -r requirements.txt
CMD ["python driver.py"]
