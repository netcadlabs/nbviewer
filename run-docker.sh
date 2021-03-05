#!/bin/bash

docker run \
    -p 5000:5000 -d \
    -v ~/.mynbviewerdata:/srv/nbviewer/data/ \
    --name nbviewer --restart unless-stopped \
    netcadlabs/nbviewer:latest