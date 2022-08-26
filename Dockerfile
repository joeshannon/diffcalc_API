#Install python and copy over repo files
FROM python:3.8

ENV ENV_DIR /diffcalc_API
WORKDIR ${ENV_DIR}

COPY . ${ENV_DIR}

#Install dependencies
RUN pip install . -c requirements.txt


#Run the API
CMD ["uvicorn", "src.diffcalc_API.server:app", "--host", "0.0.0.0"]