FROM alazartech/ubuntu20.04

COPY . .

RUN apt-get install python3-dev python3-pip
RUN pip3 install -r requirements.txt
RUN pip install --no-cache-dir --index-url https://support.bayesfusion.com/pysmile-A/ pysmile
