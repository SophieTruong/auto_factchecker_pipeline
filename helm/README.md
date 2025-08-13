# Installation instructions:

## Prerequisites

- Kubernetes cluster access (or minikube)
- helm set up locally with a fitting kubeconfig

## Setup

You have to configuration files secrets_setup and values (with respective example files).
Most likely you will only have to edit the `api_url` and the `storage_class` values in the values.yml file.
All other settings are likely ok and are mainly to keep values consistent between different pods

Fill in the fields in the secrets.yml (keys for external services + download links for the initial data/model). Everything else (database keys/users etc) not mentioned in there will be generated automatically during deployment and can then be extracted from kubernetes secrets.

There is one field which can only be filled after the setup is done (the rabbitmq_password_hash value)
This value can be obtained from the logs of the rabbitmq-hash-password pod (which runs during setup).

## Deployment

After you have created a values.yml and a secrets.yml based on the two example files install the secrets, adding the namespace is optional, depending on whether you have a specific namespace for this:
helm install <-n namespace> -f values.yml -f secrets.yml fact-checker-secrets setup/

Obtain the rabbitmq password hash:

```
kubectl get pods
# Look for a pod called rabbitmq-hash-password
kubectl logs <rabbitmq-hash-password-tag>
```

Check that the setup job is finished (kubectl get <-n namespace> jobs) before proceeding, as it needs to download the data and setup the model used.

Then run
helm install <-n namespace> -f values.yml fact-checker pipeline/

This will install all components and then run a db seed job. ONce the seed job is done, your system is ready.
