#!/bin/bash -x

### CONFIGURATION VARIABLES
#GLUU_SECRET_ADAPTER="kubernetes"
#ADMIN_PW="admin_Abcd1234#"
#EMAIL="support@gluu.org"
DOMAIN="demoexample.gluu.org"
##ORG_NAME="Deimos"
#COUNTRY_CODE="PT"
#STATE="NA"
#CITY="Lisbon"
#GLUU_CONFIG_ADAPTER="kubernetes"
#LDAP_TYPE="opendj"

# Install minikube and kubectl
K8S_VER=v1.12.0
TF_VER=0.12.16
MINIKUBE_VER=v1.9.1

#eval $(minikube docker-env)

#cd ../
#docker build -t eoepca/um-user-profile:travis_${TRAVIS_BUILD_NUMBER:-0} .
#cd travis

# Apply user-profile
echo "Applying user-profile"
kubectl apply -f ../src/config/user-profile-volumes.yaml
cat ../src/config/user-profile.yaml | sed "s/{{GLUU_DOMAIN}}/$DOMAIN/g" | sed -s "s@NGINX_IP@$(minikube ip)@g" | kubectl apply -f -
echo "##### Waiting for user-profile to start (will take around 5 minutes, ContainerCreating errors are expected):"
echo "Done!"
