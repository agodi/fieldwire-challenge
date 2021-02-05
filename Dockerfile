FROM python:3
WORKDIR /home/app
COPY ./application ./application
COPY ./requirements.txt .
RUN pip install -r requirements.txt
ENV FLASK_APP=application.py
CMD flask run --host=0.0.0.0
