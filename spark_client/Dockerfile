FROM veribilimiokulu/pyspark-3.4.1_python-3.8:1.0

# Install MinIO Client
RUN curl -o mc https://dl.min.io/client/mc/release/linux-amd64/mc && chmod +x mc && mv mc /usr/local/bin/

RUN mc alias set dataops_minio http://minio:9000 dataops Ankara06 --api S3v4
