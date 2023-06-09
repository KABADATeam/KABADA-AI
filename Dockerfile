FROM alazartech/ubuntu20.04


COPY . .
RUN apt-get install -y python3-dev python3-pip dos2unix nano
RUN pip3 install flask numpy
#RUN dos2unix requirements.txt && pip3 install -r requirements.txt
#RUN 'export PYTHONPATH="${PYTHONPATH}:/"' >>
RUN pip install --no-cache-dir --index-url https://support.bayesfusion.com/pysmile-A/ pysmile

EXPOSE 2222
#CMD python3 app.py

##### usefull commands
# docker run -v shared_files:/shared_files -p 2222:2222 -it kabada_ai /bin/bash
# docker run --name kaby -d -p 2222:2222 kabada_ai
# docker build -t kabada_ai .
# docker run -it kabada_ai /bin/bash
# python3 app.py & python3 tests/fake_client.py