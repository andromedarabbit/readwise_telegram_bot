FROM python:3.13-slim

LABEL org.opencontainers.image.source="https://github.com/andromedarabbit/readwise_telegram_bot"

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Seoul

RUN apt-get update \
    && apt-get install -yq \
        tzdata \
        locales \
        ca-certificates \
        curl \
        wget \
    && echo "ko_KR.UTF-8 UTF-8" >> /etc/locale.gen \
    && locale-gen ko_KR.UTF-8 \
    && rm -rf /var/lib/apt/lists/*

RUN adduser --disabled-password --gecos '' app
USER app
WORKDIR /home/app

# Set the lang
ENV LC_ALL=ko_KR.UTF-8
ENV LANGUAGE=ko_KR.UTF-8
ENV LANG=ko_KR.UTF-8
ENV PYTHONIOENCODING=UTF-8

ENV PYTHONPATH=/home/app
ENV PATH="/home/app/.local/bin:${PATH}"

COPY --chown=app:app requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY --chown=app:app . .

# RUN pytest -v ./tests
CMD ["python", "app.py"]
