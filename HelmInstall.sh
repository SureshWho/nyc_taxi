
# Install helm\
echo "Installing Helm"
curl https://raw.githubusercontent.com/kubernetes/helm/master/scripts/get > get_helm.sh
chmod 700 get_helm.sh
./get_helm.sh
sleep 15

### Install has some bug we need to delete and re-create ###
kubectl get all --all-namespaces | grep tiller
kubectl delete deployment tiller-deploy -n kube-system
kubectl delete service tiller-deploy -n kube-system
kubectl get all --all-namespaces | grep tiller
sleep 15

helm init
sleep 15

kubectl create serviceaccount --namespace kube-system tiller
kubectl create clusterrolebinding tiller-cluster-rule --clusterrole=cluster-admin --serviceaccount=kube-system:tiller
kubectl patch deploy --namespace kube-system tiller-deploy -p '{"spec":{"template":{"spec":{"serviceAccount":"tiller"}}}}'
sleep 15

kubectl --namespace kube-system get pods | grep tiller

echo "Waiting till tiller gets ready"
sleep 20
kubectl --namespace kube-system get pods | grep tiller
sleep 5


