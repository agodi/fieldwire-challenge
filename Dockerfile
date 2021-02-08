FROM python:3
WORKDIR /home/app
COPY ./application ./application
COPY ./requirements.txt .
COPY ./wait-for-it.sh .
ENV FLASK_APP=application.py
ENV FLASK_RUN_HOST=0.0.0.0
RUN pip install -r requirements.txt
EXPOSE 5000
#CMD ./wait-for-it.sh db:3306 -- flask run
