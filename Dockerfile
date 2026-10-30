FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /opt/harness/requirements.txt
RUN pip install --no-cache-dir -r /opt/harness/requirements.txt
COPY harness_lock.py /opt/harness/harness_lock.py
COPY adjudicate.py /opt/harness/adjudicate.py
RUN chmod -R a-w /opt/harness && useradd --create-home gate && git config --system --add safe.directory /workspace
USER gate
WORKDIR /workspace
ENV LM_STUDIO_URL="http://host.docker.internal:1234/v1/chat/completions"
# Mount the repo read-only at run time: -v "$PWD":/workspace:ro
CMD ["sh", "-c", "python /opt/harness/harness_lock.py verify && python /opt/harness/adjudicate.py"]
