#   -*- coding: utf-8 -*-
FROM python:3.6-alpine

ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /mp4ansi

COPY . /mp4ansi/

RUN pip install pybuilder==0.11.17
RUN pyb install_dependencies
RUN pyb install
