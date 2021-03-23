#!/bin/bash

docker run \
    -p 5000:5000 -d \
    -v ~/.mynbviewerdata:/var/nbviewer/data/ \
    --name nbviewer --restart unless-stopped \
    netcadlabs/nbviewer:latest

# docker run -p 5000:5000 -v ~/.mynbviewerdata:/var/nbviewer/data/ --name nbviewer netcadlabs/nbviewer:latest