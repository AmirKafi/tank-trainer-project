FROM python:3.12

WORKDIR /usr/local/app

RUN apt-get update && apt-get install -y libpq-dev

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 5000


RUN useradd app
USER app

CMD ["uvicorn", "entry_points.app:app", "--host", "0.0.0.0", "--port", "5000"]