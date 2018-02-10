FROM python:3

ADD config.py /
ADD bot.py /
ADD run.sh /

RUN pip install requests praw pyrebase

CMD [ "/bin/sh", "./run.sh" ]
