#!/bin/bash

apt-get install -y python3-dev python3-pip
pip3 install -r requirements.txt
#RUN dos2unix requirements.txt && pip3 install -r requirements.txt
#RUN 'export PYTHONPATH="${PYTHONPATH}:/"' >> .bashrc
pip install --no-cache-dir --index-url https://support.bayesfusion.com/pysmile-A/ pysmile
