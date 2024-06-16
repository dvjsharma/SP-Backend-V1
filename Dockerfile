FROM python:3.11
ENV API_HOME=/home/app/webapp
RUN mkdir -p $API_HOME
WORKDIR $API_HOME
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
COPY . $API_HOME
RUN pip install --upgrade pip && pip install -r requirements.txt
RUN python manage.py makemigrations && python manage.py migrate
EXPOSE 8080
ENTRYPOINT ["python", "manage.py", "runserver", "0.0.0.0:8080"]