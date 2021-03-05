#!/usr/bin/env bash

#prepared to run in jenkins

echo "Starting docker build.."

echo "$DOCKER_USER_PSW" | docker login -u "$DOCKER_USER_USR" --password-stdin

BUILD_TAG="$BUILD_NUMBER"

BUILD_NAME=netcadlabs/nbviewer

docker build -t ${BUILD_NAME}:${BUILD_TAG} .

docker tag ${BUILD_NAME}:${BUILD_TAG} ${BUILD_NAME}:latest

echo "Pushing new images to registry"

# docker push ${BUILD_NAME}:${BUILD_TAG}

docker push ${BUILD_NAME}:latest

if [ "$REMOVE_LOCAL_IMAGES" == "true" ]; then
  docker rmi ${BUILD_NAME}:${BUILD_TAG}
fi

docker logout