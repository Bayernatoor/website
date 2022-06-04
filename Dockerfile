FROM python:slim

RUN useradd website

WORKDIR /home/website

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY app app
COPY migrations migrations
COPY website.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP website.py

RUN chown -R website:website ./
USER website

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
