FROM python:3.10-buster

LABEL org.opencontainers.image.source = "https://github.com/andromedarabbit/readwise_telegram_bot"

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Seoul

RUN sed -i 's/archive.ubuntu.com/ftp.daumkakao.com/g' /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -yq \
        tzdata \
        locales locales-all \
        ca-certificates \
        curl wget \
    && locale-gen ko_KR.UTF-8 \
    && /usr/sbin/update-locale LANG=ko_KR.UTF-8 \
    && rm -rf /var/lib/apt/lists/* \
    && fc-cache -fv

RUN adduser app
USER app
WORKDIR /home/app

# Set the lang
ENV LC_ALL ko_KR.UTF-8
ENV LNGUAGE ko_KR.UTF-8
ENV LANG ko_KR.UTF-8
ENV PYTHONIOENCODING UTF-8

ENV PYTHONPATH /home/app
ENV PATH="/home/app/.local/bin:${PATH}"

COPY --chown=app:app requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY --chown=app:app . .

# RUN pytest -v ./tests
CMD python app.py
