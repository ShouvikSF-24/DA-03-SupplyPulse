FROM apache/airflow:2.11.1-python3.12

USER airflow

RUN pip install --no-cache-dir \
    "apache-airflow==2.11.1" \
    pandas \
    numpy \
    "SQLAlchemy<2.0" \
    psycopg2-binary \
    python-dotenv \
    requests \
    prophet \
    --constraint "${HOME}/constraints.txt"