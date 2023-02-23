FROM python:3.10-slim-buster

RUN apt-get update
RUN apt-get install -y mecab libmecab-dev mecab-ipadic-utf8
RUN ln -s /etc/mecabrc /usr/local/etc/mecabrc
RUN apt-get clean

WORKDIR /app/

COPY . .

RUN pip install -r requirements.txt

EXPOSE 3000

CMD ["python", "app.py"]