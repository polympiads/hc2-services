FROM ubuntu

WORKDIR /hc2admin

RUN apt-get update
RUN apt-get install -y python3 python3-pip python3-venv

RUN python3 -m venv .venv

ENV VIRTUAL_ENV=/hc2admin/.venv
ENV PATH=/hc2admin/.venv/bin:$PATH

COPY ./requirements.txt .
RUN python3 -m pip install -r requirements.txt

COPY ./entrypoint.sh .
COPY ./app .

ENTRYPOINT [ "bash", "entrypoint.sh" ]