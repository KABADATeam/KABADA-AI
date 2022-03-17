# KABADA AI

### Model description
AI model is a bayes network representing probability 
distribution over business plans. By conditiong Bayes network on 
already filled fields from UI - we can recommend most likely
field values for still unfilled fields.

### Implementation description

BayesFusion.org implementation of Bayes Network inference and training 
is used via python bindings. The AI application can be run as python 
application or as docker application.

### Installation and running on Windows host

To install python 3.8 on Your windows machine together with pip (python package manager) run 
python-3.8.10.exe (for 32 bit machine) or python-3.8.10-amd64.exe (for 64 bit machine). Both exe files 
are in the root directory of this repository.
In the prompt push Customize button and fill the tick boxes as in image bellow and install python.
![python install menu](docs/python_customized_installation.png "python customized installation")


After that install necessary python libraries with these commands in CMD
```buildoutcfg
pip install -r requirements.txt
pip install --no-cache-dir --index-url https://support.bayesfusion.com/pysmile-A/ pysmile
```

To start application go to this repository's root directory via CMD and run 
Applicaiton runs as a daemon - start it with command
```buildoutcfg
python ai_daemon.py start --ip=localhost --port=2222
```
and stop it with command
```buildoutcfg
python ai_daemon.py stop
```
or restart it with command
```buildoutcfg
python ai_daemon.py restart --ip=localhost --port=2222
```
There is default values for ip adress and port (localhost and 2222 
respectively), so if default values are ok, you can skip providing 
these values.

#### Testing on windows
To test if all necessary components are installed start the rest server
as describer previously. Then also from repository's root directory via CMD run
```buildoutcfg
python tests/fake_client.py
```
This script will generate random business plans and send it to AI application.
for processing 4 times. If this script terminates without error - AI 
application is installed succesfully.

### Installation and running as docker container

To build docker image
```buildoutcfg
docker build -t kabada_ai .
```

To start AI service for the first time
```buildoutcfg
docker run --name kaby -v shared_files:/shared_files -d -p 2222:2222 kabada_ai
```
To start AI service next time
```buildoutcfg
docker start kaby
```

To shutdown the service
```buildoutcfg
docker stop kaby
```

## Installation and running on Ubuntu 20.04LTS
Open bash shell this repository's root directory and run this command
```buildoutcfg
sudo bash install_on_linux.sh
```
The script installs python and all necessary libraries.

Applicaiton runs as a daemon - start it with command
```buildoutcfg
python3 ai_daemon.py start --ip=localhost --port=2222
```
and stop it with command
```buildoutcfg
python3 ai_daemon.py stop
```
or restart it with command
```buildoutcfg
python3 ai_daemon.py restart --ip=localhost --port=2222
```
There is default values for ip adress and port (localhost and 2222 
respectively), so if default values are ok, you can skip providing 
these values.

The only difference with running on windows is using ``python3`` instead
of ``python`` on windows.


## Endpoints
To receive recommandations for field values, use predict endpoint, which
has url ``http:/<ip>:<port>/predict``. For this request use ``post`` method.

## Default ip and port
If You don't want to use daemon parameters to set ip and port other than ``localhost`` 
and ``2222``, then make a json file in repo root with name ``ip_port.json`` that contains 
the desired ip and port. For example ``{"ip": "192.168.1.137","port": "2222"}``.