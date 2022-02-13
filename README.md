# KABADA AI

### Model description
AI model is a bayes network representing probability 
distribution over business plans. By conditiong Bayes network on 
already filled fields from UI - we can recommend most likely
field values for still unfilled fields.

### Implementation description

BayesFusion.org implementation of Bayes Network inference and training 
is used via python bindings. KABADA AI component is packaged as docker 
application.

### Installation and running
First - go to repo root. 

To build docker image
```buildoutcfg
docker build -t kabada_ai .
```

To start AI service
```buildoutcfg
docker run --name kaby -d -p 2222:2222 kabada_ai
```

To shutdown the service
```buildoutcfg
docker stop kaby
```

Service url is ``localhost:2222``