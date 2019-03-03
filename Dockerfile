FROM python:3
COPY . /byob_app
WORKDIR /byob_app
RUN pip install -r requirements.txt
CMD ["python driver.py"]
