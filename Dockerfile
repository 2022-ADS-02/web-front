FROM python:3.8

COPY ./ /app/
WORKDIR /app

RUN apt-get update
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "main:app"]