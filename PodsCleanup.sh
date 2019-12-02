#!/bin/bash
#
#
### PODs cleanup
sudo docker rm -f $(sudo docker ps -a -q --filter "name=k8s")

kubectl delete rc      --all
kubectl delete deploy  --all
kubectl delete service --all
kubectl delete pods    --all

sudo docker image rm gcr.io/prj-nyc-taxis/nyc-taxi-app
sudo docker image rm gcr.io/prj-nyc-taxis/subscriber



