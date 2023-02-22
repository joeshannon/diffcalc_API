#Install python and copy over repo files
FROM python:3.8
ARG PIP_OPTIONS=.

ENV ENV_DIR /diffcalc_api
WORKDIR ${ENV_DIR}
COPY . ${ENV_DIR}

RUN pip install ${PIP_OPTIONS}

CMD ["diffcalc_api"]