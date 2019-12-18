
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

echo "Settingup kafka cluster"
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm install bitnami/kafka --name nyc-taxi-kafka -f deployments/values-kafka.yml


