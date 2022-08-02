#Install python and copy over repo files
FROM python:3.8

ENV ENV_DIR /diffcalc_API
WORKDIR ${ENV_DIR}

COPY . ${ENV_DIR}

#Install dependencies
RUN pip install pipenv; \
    pipenv install --system --python 3.8; \
    pip uninstall diffcalc-core -y; \
    pip install git+https://github.com/DiamondLightSource/diffcalc-core.git


#Run the API
CMD ["uvicorn", "src.diffcalc_API.server:app", "--host", "0.0.0.0"]