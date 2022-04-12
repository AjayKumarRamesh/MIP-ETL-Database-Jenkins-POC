# Sonarqube-Kubernetes

### Create the Namespace
~~~
    $ kubectl create namespace sonarqube
~~~

### Deploying Postgres Secrets, PVC(PersistentVolumeClaim), Deployment and Service
~~~
    $ kubectl apply -f postgres.yml
~~~

### Deploying SonarQube ConfigMaps, PVC(PersistentVolumeClaim), Deployment, Service and Ingress
~~~
    $ kubectl apply -f sonarqube.yml
~~~








