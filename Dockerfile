FROM apify/actor-python:3.11

WORKDIR /usr/src/app

COPY pyproject.toml ./
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir . && \
    crawl4ai-setup

COPY src ./src

CMD ["python", "-m", "crawl4ai_actor.main"]
