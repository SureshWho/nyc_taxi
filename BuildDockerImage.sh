#!/bin/bash
#
#

# Check whether directory is specified
if [[ -z "$1" ]]; then
	echo ERROR!!!: Please specify docker directory BuildDockerImage \<directory\> 1>&2
    exit 1 # terminate and indicate error
fi

# Check whether GCP Project name is set
if [[ -z "${G_PROJECT}" ]]; then
	echo ERROR!!!: GCP Project is NOT set. Set using \"gcs \<gcpProject\> \<gcpCompute\>\" 1>&2
    exit 1
fi


if [ ! -d "$1" ]; then
	echo ERROR!!!: directory \""$1"\" does not exists 1>&2
    exit 1
fi

# Build, Tag, and Push the GCR (Google Cloud Registery) docker image
echo "Building... $1 directory"
docker build -t "$1" ./"$1"

echo "Tagging... it as gcr.io/$G_PROJECT/$1:latest"
docker tag "$1" gcr.io/$G_PROJECT/"$1":latest

echo "Pushing... gcr.io/$G_PROJECT/$1:latest"
docker push gcr.io/$G_PROJECT/"$1":latest

docker image ls