FROM python:3.12 as builder

WORKDIR /usr/local/app

RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

FROM python:3.12-slim

WORKDIR /usr/local/app

COPY --from=builder /usr/local/app /usr/local/app
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

ENV PATH=/usr/local/bin:$PATH

EXPOSE 5000

RUN useradd -m app && chown -R app /usr/local/app
USER app

CMD ["uvicorn", "entry_points.app:app", "--host", "0.0.0.0", "--port", "5000"]
