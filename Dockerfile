FROM python:3
COPY . /byob_app
WORKDIR /byob_app
RUN apt-get update && apt-get install -y tesseract-ocr python3-tk
RUN pip install -r requirements.txt
ENV DISPLAY :0
CMD ["python3", "driver.py"]
