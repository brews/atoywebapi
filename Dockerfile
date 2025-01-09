# Container spec for web API server.
FROM python:3.12

WORKDIR /opt/atoywebapi

# Need this so GCP Cloud Run does Cloud SQL connection via Unix sockets.
RUN mkdir /cloudsql
RUN chmod 777 /cloudsql

# Start by copying requirements so these are cached in Docker layer, speeding up later build times.
# These options also help keep cruft off the container image.
COPY ./requirements.txt /opt/atoywebapi/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /opt/atoywebapi/requirements.txt

COPY ./app.py /opt/atoywebapi/app.py

# Setting these defaults so they work with how the container will mostly be deployed,
# and what Cloud Run/Knative expects.
ENV PORT="8080"
ENV HOST="0.0.0.0"

CMD ["python", "/opt/atoywebapi/app.py"]
