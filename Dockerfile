#Install python and copy over repo files
FROM python:3.8

ENV ENV_DIR /diffcalc_api
WORKDIR ${ENV_DIR}

COPY . ${ENV_DIR}

RUN ls .
# RUN pip install .

# CMD ["uvicorn", "src.diffcalc_api.server:app", "--host", "0.0.0.0"]