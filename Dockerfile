FROM tensorflow/tensorflow:1.6.0-gpu
WORKDIR /opt
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y nodejs-legacy npm git python3 python python-pip python-tk && \
    git clone https://github.com/sergivalverde/nicMSlesions.git && \
    cd nicMSlesions && \
    pip install -r requirements.txt && \
# TF needs to be uninstalled then reinstalled...?
# https://github.com/tensorflow/tensorflow/issues/20778#issuecomment-404964674
    pip uninstall -y tensorflow-gpu protobuf && pip install tensorflow-gpu==1.6.0 && \
    npm install -g bids-validator@0.19.2 && \
    apt-get remove -y python-pip git npm && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
COPY ./config.py ./nicMSlesions/utils/load_options.py
COPY run.py version /
ENTRYPOINT ["/run.py"]

# build image
# docker build -t pennsive/nicmslesions:gpu .
# docker build -f Dockerfile.cpu -t pennsive/nicmslesions:cpu .