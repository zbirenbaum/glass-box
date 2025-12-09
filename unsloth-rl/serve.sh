#!/bin/bash
set -e

# --- Configuration from Environment ---
# We use the internal LOTA endpoint for speed if available, otherwise fallback to standard S3
S3_ENDPOINT=${BUCKET_ENDPOINT_INTERNAL:-$AWS_ENDPOINT_URL_S3}
MODEL_SOURCE="${AWS_BUCKET_URL}/Qwen3-235B-Instruct"
LOCAL_MODEL_PATH="/data/model_weights"

echo "--- CoreWeave Deployment Initialization ---"
echo "Region: $AWS_REGION"
echo "Model Source: $MODEL_SOURCE"
echo "Using Endpoint: $S3_ENDPOINT"

# 1. Sync Model Weights
if [ ! -f "${LOCAL_MODEL_PATH}/config.json" ]; then
    echo "[!] Model not found on PVC. Downloading..."
    mkdir -p ${LOCAL_MODEL_PATH}
    
    # We use the env vars implicitly for auth (AWS_ACCESS_KEY_ID/SECRET)
    # We force the endpoint to your internal URL for speed
    aws s3 sync ${MODEL_SOURCE} ${LOCAL_MODEL_PATH} \
        --endpoint-url ${S3_ENDPOINT} \
        --region ${AWS_REGION}
else
    echo "[+] Model found on PVC. Skipping download."
fi

echo "--- Launching vLLM ---"

# 2. Launch vLLM
python3 -m vllm.entrypoints.openai.api_server \
    --model ${LOCAL_MODEL_PATH} \
    --tensor-parallel-size 4 \
    --gpu-memory-utilization 0.95 \
    --max-model-len 8192 \
    --disable-log-requests \
    --host 0.0.0.0 \
    --port 8000
