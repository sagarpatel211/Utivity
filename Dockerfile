FROM python:3.7
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install pyqt5
RUN pip install -r requirements.txt
COPY . /app
ENTRYPOINT [ "python" ]
CMD ["app.py" ]
