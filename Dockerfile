#Install python and copy over repo files
FROM python:3.8

ENV ENV_DIR /diffcalc_api
WORKDIR ${ENV_DIR}

COPY . ${ENV_DIR}

#Install dependencies
RUN pip install .


#Run the API
CMD ["uvicorn", "src.diffcalc_api.server:app", "--host", "0.0.0.0"]