#!/usr/bin/env bash
set -Eeuo pipefail

# Ubuntu setup script to run assignment3/main.py
# Usage:
#   bash setup_script.sh            # install deps, create venv, run script
#   bash setup_script.sh --no-run   # install deps, create venv, skip running

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$PROJECT_ROOT/.venv"
PYTHON_BIN="$VENV_DIR/bin/python"
PIP_BIN="$VENV_DIR/bin/pip"
RUN_AFTER_SETUP=true

if [[ "${1:-}" == "--no-run" ]]; then
  RUN_AFTER_SETUP=false
fi

echo "[1/5] Installing system packages (requires sudo) ..."
if ! command -v sudo >/dev/null 2>&1; then
  echo "sudo not found; attempting to continue without it (running apt directly)."
  SUDO=""
else
  SUDO="sudo"
fi

$SUDO apt-get update -y
$SUDO DEBIAN_FRONTEND=noninteractive apt-get install -y \
  python3 python3-venv python3-pip \
  git build-essential \
  libopenblas-dev libffi-dev libssl-dev \
  curl ca-certificates

echo "[2/5] Creating Python virtual environment at $VENV_DIR ..."
if [[ ! -d "$VENV_DIR" ]]; then
  python3 -m venv "$VENV_DIR"
fi

echo "[3/5] Upgrading pip/setuptools/wheel ..."
"$PIP_BIN" install --upgrade pip setuptools wheel

echo "[4/5] Installing Python dependencies ..."

# Core scientific stack used by gensim/torch
"$PIP_BIN" install numpy scipy smart-open tqdm

# CPU-only PyTorch (works on vanilla Ubuntu without CUDA)
"$PIP_BIN" install --index-url https://download.pytorch.org/whl/cpu torch

# Transformers stack for Hugging Face models
"$PIP_BIN" install "transformers>=4.40" tokenizers safetensors huggingface-hub accelerate

# NLP and ML utilities referenced in environment.yml
"$PIP_BIN" install gensim "scikit-learn<=1.6.1" nltk==3.4 bs4 python-dotenv openai google-genai sapling-py

echo "[5/5] Verifying installation ..."
"$PYTHON_BIN" - <<'PY'
import sys
print("Python:", sys.version)
import torch, transformers, gensim
print("torch:", torch.__version__)
print("transformers:", transformers.__version__)
print("gensim:", gensim.__version__)
PY

if "$RUN_AFTER_SETUP"; then
  echo "Running assignment3/main.py ..."
  cd "$PROJECT_ROOT/assignment3"
  exec "$PYTHON_BIN" main.py
else
  echo "Setup complete. To run:"
  echo "  source $VENV_DIR/bin/activate && python assignment3/main.py"
fi