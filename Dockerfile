FROM python:3.12

ENV TZ=Europe/Ekaterinburg

COPY ./app/ /app/

WORKDIR app

COPY requirements.txt .

RUN pip install --no-cache-dir -r /app/requirements.txt

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0"]
