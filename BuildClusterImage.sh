#!/bin/bash
#
#
export G_PROJECT=prj-nyc-taxis
echo "Building NYC Taxi Application "
./BuildDockerImage.sh nyc-taxi-app
rc=$?; if [[ $rc != 0 ]]; then exit $rc; fi

echo "Building Pub/Sub Subscriber"
./BuildDockerImage.sh subscriber
rc=$?; if [[ $rc != 0 ]]; then exit $rc; fi

echo "Creating tar image"
tar -cvf nyc-taxi-pkg.tar ./*.sh ./deployments


