FROM python:3.12-slim AS builder

WORKDIR /app
COPY pyproject.toml .
COPY src/ src/
RUN pip install --no-cache-dir .

FROM python:3.12-slim

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY src/ src/

RUN useradd --create-home scraper
USER scraper

RUN mkdir -p /app/output

ENTRYPOINT ["python", "-m", "yad2_scraper"]
