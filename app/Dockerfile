FROM ubuntu:20.04

RUN apt-get update -y \
    && apt-get install -y python3 python3-pip \
    && apt-get install -y git \
    && rm -rf /var/lib/apt/lists/*

RUN ln -s /usr/bin/pip3 /usr/bin/pip \
    && pip install --upgrade pip

RUN useradd -m app
USER app
WORKDIR /home/app

COPY --chown=app:app requirements.txt requirements.txt
RUN pip install --user -r requirements.txt

ENV PATH="/home/app/.local/bin:${PATH}"

COPY --chown=app:app . .

LABEL maintainer="Blair Drummond <blair.drummond@canada.ca>" \
      version="1.0.0"

CMD ["python3", "main.py"]
