FROM neurodebian:buster
ARG GPU="-gpu"
ENV PYTHONPATH=""
WORKDIR /opt
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y nodejs npm git python3 python3-pip python3-numpy python python-pip python-tk && \
    git clone https://github.com/sergivalverde/nicMSlesions.git && \
    cd nicMSlesions && \
    pip3 install nibabel==2.0 && \
    pip install tensorflow${GPU}==1.6.0 && \
    pip install -r requirements.txt && \
    npm install -g bids-validator@0.19.2 && \
    apt-get remove -y python-pip python3-pip git npm && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
COPY ./config.py ./nicMSlesions/utils/load_options.py
COPY run.py version /
ENTRYPOINT ["/run.py"]

# build image
# docker build -t pennsive/nicmslesions:gpu .
# docker build --build-arg GPU="" -t pennsive/nicmslesions:cpu .