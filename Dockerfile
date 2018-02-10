FROM python:3

ADD bot.py /

RUN pip install requests praw pyrebase

CMD [ "python", "./bot.py" ]