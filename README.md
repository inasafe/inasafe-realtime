# inasafe-realtime
Realtime logic for InaSAFE

# Installing dependencies
```
pip install -r REQUIREMENTS.txt
pip install -r src/realtime/REQUIREMENTS.txt
pip install -r src/headless/REQUIREMENTS.txt
```


# Building the docker image

Simply run make build to create docker image, based on the current repo checkout.

```
make build
```

This will create a container with tagged name: `inasafe/inasafe-realtime:latest`.
You can use this container right away (not pulling from docker hub).

```
make up
```

More examples coming.
