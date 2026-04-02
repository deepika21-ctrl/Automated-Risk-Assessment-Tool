# 🚀 Deployment Guide

This guide covers deploying the Automated Risk Assessment Tool locally and on Kubernetes.

---

## 📋 Prerequisites

- Python 3.11+
- Docker Desktop (for local containerized deployment)
- kubectl (for Kubernetes deployment)
- Kubernetes cluster (minikube, EKS, GKE, or AKS)
- Hugging Face API key (optional, for LLM features)

---

## 🖥️ Local Development

### Option 1: Direct Python

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export HUGGINGFACE_API_KEY="your_api_key_here"

# Run the enhanced app
streamlit run app/streamlit_app_enhanced.py --server.port 8501
```

Access at: `http://localhost:8501`

### Option 2: Docker

```bash
# Build the image
docker build -t risk-assessment-tool:latest .

# Run container
docker run -p 8501:8501 \
  -e HUGGINGFACE_API_KEY="your_key" \
  risk-assessment-tool:latest
```

Access at: `http://localhost:8501`

### Option 3: Docker Compose

```bash
# Create .env file
echo "HUGGINGFACE_API_KEY=your_key" > .env

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## ☸️ Kubernetes Deployment

### Step 1: Prepare Cluster

#### For Minikube (Local)
```bash
# Start minikube
minikube start --cpus=4 --memory=8192

# Enable metrics server (for HPA)
minikube addons enable metrics-server

# Check status
kubectl get nodes
```

#### For Cloud (AWS EKS example)
```bash
# Create cluster
eksctl create cluster \
  --name risk-assessment-cluster \
  --region us-west-2 \
  --nodes 3 \
  --node-type t3.medium

# Configure kubectl
aws eks update-kubeconfig --name risk-assessment-cluster --region us-west-2
```

### Step 2: Build and Push Image

#### For Docker Hub
```bash
# Tag image
docker tag risk-assessment-tool:latest your-dockerhub-username/risk-assessment-tool:latest

# Push to registry
docker push your-dockerhub-username/risk-assessment-tool:latest
```

#### For AWS ECR
```bash
# Authenticate
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com

# Create repository
aws ecr create-repository --repository-name risk-assessment-tool

# Tag and push
docker tag risk-assessment-tool:latest YOUR_ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com/risk-assessment-tool:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com/risk-assessment-tool:latest
```

### Step 3: Create Kubernetes Secrets

```bash
# Create secret for Hugging Face API key
kubectl create secret generic risk-assessment-secrets \
  --from-literal=huggingface-api-key=YOUR_HUGGINGFACE_API_KEY

# Verify secret
kubectl get secrets
kubectl describe secret risk-assessment-secrets
```

### Step 4: Update Deployment Image

Edit `k8s/deployment.yaml` and update the image:

```yaml
spec:
  containers:
  - name: streamlit-app
    image: your-registry/risk-assessment-tool:latest  # Update this
```

### Step 5: Deploy Application

```bash
# Apply all Kubernetes manifests
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml

# Check deployment
kubectl get deployments
kubectl get pods
kubectl get svc
kubectl get hpa

# Watch pod creation
kubectl get pods -w
```

### Step 6: Access Application

#### For LoadBalancer (Cloud)
```bash
# Get external IP
kubectl get svc risk-assessment-service

# Wait for EXTERNAL-IP to be assigned
# Access at: http://<EXTERNAL-IP>
```

#### For Minikube
```bash
# Get service URL
minikube service risk-assessment-service --url

# Or use port-forward
kubectl port-forward svc/risk-assessment-service 8501:80

# Access at: http://localhost:8501
```

#### For NodePort (Alternative)
```bash
# Get node IP and port
kubectl get nodes -o wide
kubectl get svc risk-assessment-service

# Access at: http://<NODE-IP>:<NODE-PORT>
```

### Step 7: Monitor Application

```bash
# View pod logs
kubectl logs -f deployment/risk-assessment-deployment

# View specific pod
kubectl logs -f <pod-name>

# Check HPA status
kubectl get hpa -w

# Describe HPA for details
kubectl describe hpa risk-assessment-hpa

# Monitor resource usage
kubectl top nodes
kubectl top pods
```

### Step 8: Test Autoscaling

```bash
# Generate load (requires Apache Bench)
ab -n 1000 -c 100 http://<SERVICE-URL>/

# Or use kubectl run
kubectl run -i --tty load-generator --rm --image=busybox --restart=Never -- /bin/sh -c "while sleep 0.01; do wget -q -O- http://risk-assessment-service; done"

# Watch HPA scale up
kubectl get hpa -w
kubectl get pods -w
```

---

## 🔧 Troubleshooting

### Issue: Pods not starting

```bash
# Check pod status
kubectl describe pod <pod-name>

# View pod logs
kubectl logs <pod-name>

# Common fixes:
# 1. Image pull error - check image name and registry access
# 2. Secret not found - verify secret creation
# 3. Resource limits - adjust in deployment.yaml
```

### Issue: Service not accessible

```bash
# Check service endpoints
kubectl get endpoints risk-assessment-service

# Verify pods are ready
kubectl get pods

# Check service type
kubectl get svc risk-assessment-service

# For LoadBalancer, ensure cloud provider supports it
```

### Issue: HPA not scaling

```bash
# Check metrics server
kubectl get apiservices | grep metrics

# Verify HPA conditions
kubectl describe hpa risk-assessment-hpa

# Check pod resource requests (required for HPA)
kubectl describe pod <pod-name> | grep -A5 Requests
```

---

## 🔄 Updates and Rollbacks

### Update Deployment

```bash
# Build new image with tag
docker build -t risk-assessment-tool:v2 .
docker push your-registry/risk-assessment-tool:v2

# Update deployment
kubectl set image deployment/risk-assessment-deployment \
  streamlit-app=your-registry/risk-assessment-tool:v2

# Check rollout status
kubectl rollout status deployment/risk-assessment-deployment
```

### Rollback Deployment

```bash
# View rollout history
kubectl rollout history deployment/risk-assessment-deployment

# Rollback to previous version
kubectl rollout undo deployment/risk-assessment-deployment

# Rollback to specific revision
kubectl rollout undo deployment/risk-assessment-deployment --to-revision=2
```

---

## 🧹 Cleanup

### Remove Kubernetes Resources

```bash
# Delete all resources
kubectl delete -f k8s/

# Delete secrets
kubectl delete secret risk-assessment-secrets

# Verify deletion
kubectl get all
```

### Stop Minikube

```bash
minikube stop
minikube delete
```

### Delete Cloud Cluster

```bash
# AWS EKS
eksctl delete cluster --name risk-assessment-cluster --region us-west-2

# GKE
gcloud container clusters delete risk-assessment-cluster --zone us-central1-a
```

---

## 📊 Performance Optimization

### Tuning HPA

Edit `k8s/hpa.yaml`:

```yaml
spec:
  minReplicas: 3          # Increase for high traffic
  maxReplicas: 20         # Increase ceiling
  targetCPUUtilization: 60  # Lower = more aggressive scaling
```

### Tuning Resource Limits

Edit `k8s/deployment.yaml`:

```yaml
resources:
  requests:
    memory: "1Gi"       # Increase for large portfolios
    cpu: "1000m"
  limits:
    memory: "4Gi"
    cpu: "4000m"
```

---

## 🔐 Security Best Practices

1. **Use Private Registry**: Store images in private Docker registry
2. **Rotate Secrets**: Regularly update API keys
3. **Network Policies**: Implement Kubernetes Network Policies
4. **RBAC**: Configure Role-Based Access Control
5. **TLS**: Use Ingress with TLS certificates

---

## 📞 Support

For deployment issues:
1. Check the logs: `kubectl logs -f <pod-name>`
2. Review pod events: `kubectl describe pod <pod-name>`
3. Open GitHub issue with error details

---

**Happy Deploying! 🚀**
