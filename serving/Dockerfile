#tensorflow 2.10.0-gpu version?error
FROM tensorflow/tensorflow:2.11.0-gpu

RUN apt update
RUN apt install git wget unzip -y

WORKDIR /tmp
# model
COPY ./output_model /wowboard_model

# TF OBDE API
RUN git clone https://github.com/tensorflow/models.git /tmp/models
RUN wget https://github.com/protocolbuffers/protobuf/releases/download/v22.0/protoc-22.0-linux-x86_64.zip -P /tmp
RUN unzip protoc-22.0-linux-x86_64.zip  -d /tmp/protoc

WORKDIR /tmp/models/research
RUN ../../protoc/bin/protoc object_detection/protos/*.proto --python_out=.

# RUN cp object_detection/packages/tf2/setup.py .
# RUN python -m pip install .
# RUN python -m pip install tensorflow==2.11.0

# https://stackoverflow.com/questions/71759248/importerror-cannot-import-name-builder-from-google-protobuf-internal

# app.py
COPY ./app.py /app.py

RUN pip3 install flask google-cloud-storage pillow


CMD ["/bin/sh", "-c", "python app.py"]