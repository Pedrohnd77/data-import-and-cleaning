# ============================================================
# Custom Airflow image for the NBA Stats EDA Pipeline
# Base: apache/airflow 2.9.3 with Python 3.11
# ============================================================
FROM apache/airflow:2.9.3-python3.11

# Switch to root to install system packages
USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create the directories that the pipeline will use
RUN mkdir -p /opt/airflow/data \
             /opt/airflow/outputs \
             /opt/airflow/repo

# Switch back to the airflow user for pip installs (security best practice)
USER airflow

# Install Python data-science dependencies
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt