#!/bin/bash
#
#
### Deploy the PODs

sleep 10
echo "!!! Deploying...nyc-taxi-app"
kubectl apply -f deployments/nyc-taxi-app.yml

echo "!!! Deploying...subscriber"
kubectl apply -f deployments/subscriber.yml
