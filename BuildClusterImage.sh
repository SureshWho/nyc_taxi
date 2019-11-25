#!/bin/bash
#
#
echo "Building NYC Taxi Application "
./BuildDockerImage.sh nyc-taxi-app
rc=$?; if [[ $rc != 0 ]]; then exit $rc; fi

echo "Creating tar image"
tar -cvf nyc-taxi-pkg.tar ./Install.sh ./DockerInstall.sh ./KuberInstall.sh ./SecretInstall.sh ./deployments

