from gigabase

COPY data /opt/data
COPY api /app

WORKDIR /app

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]

# To build:
# /backend: docker build --build-arg KEY=<API_KEY_STR> -t gigahack-api .
# To run:
# docker run -d -p 5000:5000 gigahack-api 