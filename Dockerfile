FROM neurodebian:buster
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y nodejs npm git python3 python3-pip python3-numpy python python-pip python-tk && \
    git clone https://github.com/sergivalverde/nicMSlesions.git && \
    cd nicMSlesions && \
    pip3 install nibabel==2.0 && \
    pip install tensorflow==1.6.0 && \
    pip install -r requirements.txt && \
    npm install -g bids-validator@0.19.2 && \
    apt-get remove -y python-pip python3-pip git npm && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
# RUN ls /nicMSlesions | grep batch.py$ | xargs -I {} sed -i "s#CURRENT_PATH, 'config'#'/', 'config'#g" /nicMSlesions/{}
ENV PYTHONPATH=""
COPY config.py /nicMSlesions/utils/load_options.py
COPY run.py /run.py
COPY version /version
ENTRYPOINT ["/run.py"]
