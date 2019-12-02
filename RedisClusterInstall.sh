
# Install helm
curl https://raw.githubusercontent.com/kubernetes/helm/master/scripts/get > get_helm.sh
chmod 700 get_helm.sh
./get_helm.sh

### Install has some bug we need to delete and re-create ###
kubectl get all --all-namespaces | grep tiller
kubectl delete deployment tiller-deploy -n kube-system
kubectl delete service tiller-deploy -n kube-system
kubectl get all --all-namespaces | grep tiller

helm init

kubectl create serviceaccount --namespace kube-system tiller
kubectl create clusterrolebinding tiller-cluster-rule --clusterrole=cluster-admin --serviceaccount=kube-system:tiller
kubectl patch deploy --namespace kube-system tiller-deploy -p '{"spec":{"template":{"spec":{"serviceAccount":"tiller"}}}}'

kubectl --namespace kube-system get pods | grep tiller

echo "Waiting till tiller gets ready"
sleep 10

sudo mkdir /mnt/data/
#sudo mkdir /mnt/data/0
#sudo mkdir /mnt/data/1
#sudo mkdir /mnt/data/2
#sudo mkdir /mnt/data/3

sudo sudo chown -R 1001:1001 /mnt/data/
#sudo chown -R 1001:1001 /mnt/data/0
#sudo chown -R 1001:1001 /mnt/data/1
#sudo chown -R 1001:1001 /mnt/data/2
#sudo chown -R 1001:1001 /mnt/data/3

kubectl apply -f deployments/volumn_0.yml 
kubectl apply -f deployments/volumn_1.yml
kubectl apply -f deployments/volumn_2.yml
kubectl apply -f deployments/volumn_3.yml


helm repo update
helm install stable/redis --name nyc-taxi --values values-production.yaml
#helm install stable/redis


