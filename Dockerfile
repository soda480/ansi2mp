#   -*- coding: utf-8 -*-
FROM python:3.9-slim
ENV PYTHONDONTWRITEBYTECODE 1
WORKDIR /code
COPY . /code/
RUN pip install pybuilder names essential_generators
RUN pyb install_dependencies
RUN pyb install