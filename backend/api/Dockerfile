FROM python:3-slim-buster

ARG NODE_ENV
ARG MONGO_ROOT_PASSWORD

ENV NODE_ENV $NODE_ENV
ENV MONGO_ROOT_PASSWORD $MONGO_ROOT_PASSWORD

RUN mkdir /code

WORKDIR /code

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .
ENV PYTHONPATH "${PYTHONPATH}:/code"

# CMD ["uvicorn", "app:app", "--host=0.0.0.0", "--port=8000", "--reload"]