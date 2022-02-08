FROM alazartech/ubuntu20.04

COPY . .

RUN apt-get install -y python3-dev python3-pip dos2unix nano
RUN pip3 install flask numpy
#RUN dos2unix requirements.txt && pip3 install -r requirements.txt
#RUN 'export PYTHONPATH="${PYTHONPATH}:/"' >>
RUN pip install --no-cache-dir --index-url https://support.bayesfusion.com/pysmile-A/ pysmile

# docker run -it kabada_test /bin/bash
# python3 app.py & python3 tests/fake_client.py