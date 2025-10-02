from python:slim

EXPOSE 5000

COPY requirements.txt .

ARG KEY 
ENV OPENAI_API_KEY $KEY

RUN pip install -r "requirements.txt"


# To build:
# /backend: docker build --build-arg KEY=<API_KEY_STR> -t gigahack-api .
# To run:
# docker run -d -p 5000:5000 gigahack-api 