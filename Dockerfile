FROM apify/actor-python:3.11

WORKDIR /usr/src/app

COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir . && \
    crawl4ai-setup

CMD ["python", "-m", "crawl4ai_actor.main"]
