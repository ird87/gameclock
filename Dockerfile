FROM python:3
ENV PYTHONUNBUFFERED=1
RUN mkdir /data && echo "RUN mkdir /data"
WORKDIR /data
COPY requirements.txt /data
RUN pip install --upgrade pip setuptools
RUN pip install -r requirements.txt
COPY ./ChessClockAPI /data
EXPOSE 8000:8000
COPY ./entrypoint.sh /data
RUN chmod +x /data/entrypoint.sh
ENTRYPOINT ["sh", "/data/entrypoint.sh"]
#CMD python3 /data/manage.py runserver 0.0.0.0:8000
