kubectl delete secret ghcr-cred --ignore-not-found
kubectl create secret docker-registry ghcr-cred \
  --docker-server=ghcr.io \
  --docker-username=GITHUB_USERNAME \
  --docker-password=GITHUB_PAT_TOKEN \
  --docker-email=GITHUB_EMAIL

kubectl delete secret caios-creds --ignore-not-found
kubectl create secret generic caios-creds \
  --from-literal=AWS_ACCESS_KEY_ID=your_access_key \
  --from-literal=AWS_SECRET_ACCESS_KEY=your_secret_key

kubectl delete configmap model-config --ignore-not-found
kubectl create configmap model-config \
  --from-literal=S3_MODEL_PATH=s3://zachweek/Qwen3-235B-Instruct \
  --from-literal=S3_ENDPOINT=http://cwlota.com
