#!/bin/bash
#

### Docker Installation
sudo ./DockerInstall.sh <<EOF 
Y
EOF

### K8s Installation
sudo ./KuberInstall.sh

### Init the master node
sudo kubeadm init --pod-network-cidr=10.244.0.0/16 --apiserver-advertise-address=$(hostname -i)

#export KUBECONFIG=/etc/kubernetes/admin.conf

mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
export KUBECONFIG=$HOME/.kube/config

sudo sysctl net.bridge.bridge-nf-call-iptables=1
sudo kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/2140ac876ef134e0ed5af15c65e414cf26827915/Documentation/kube-flannel.yml
kubectl taint nodes --all node-role.kubernetes.io/master-
sudo chown -R $(id -u):$(id -g) $HOME/.kube/config

### Add service account keys for accessing GCR
./SecretInstall.sh

./PodsInstall.sh
