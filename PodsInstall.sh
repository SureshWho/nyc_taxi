#!/bin/bash
#
#
### Deploy the PODs
echo "!!! Deploying...rasid-master"
kubectl apply -f deployments/redis-master.yml

echo "!!! Deploying...nyc-taxi-app"
kubectl apply -f deployments/nyc-taxi-app.yml

echo "!!! Deploying...subscriber"
kubectl apply -f deployments/subscriber.yml


### For Sentina
# Create a bootstrap master
#kubectl create -f redis-master.yaml
#sleep 5

# Create a service to track the sentinels
#kubectl create -f redis-sentinel-service.yaml
#sleep 5

# Create a replication controller for redis servers
#kubectl create -f redis-controller.yaml
#sleep 5

# Create a replication controller for redis sentinels
#kubectl create -f redis-sentinel-controller.yaml
#sleep 5

#kubectl scale rc redis --replicas=3
#kubectl scale rc redis-sentinel --replicas=3

#kubectl delete pods redis-master
#sleep 10

#echo "!!! Deploying...nyc-taxi-app"
#kubectl apply -f deployments/nyc-taxi-app.yml

#echo "!!! Deploying...subscriber"
#kubectl apply -f deployments/subscriber.yml
