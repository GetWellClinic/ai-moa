# LLM Container Installation Guide

This guide will walk you through the steps to set up and install **LLM Container** on your local machine.

## Prerequisites

Before starting, make sure you have the following installed:

- **docker** [docker.md](docker.md)
- **docker-composer**
- **Git**

## Steps for Installation

### 1. Clone the Repository

First, clone the repository to your local machine. Open your terminal and run the following command:

`git clone https://github.com/GetWellClinic/ai-moa.git`

Checkout the branch you will be using. For example, git checkout dev-gwc

Note:- If you already have cloned the repo you can skip this step

### 2. Change to the `llm-container` Directory

Navigate to the llm-container folder within the repository:

`cd ai-moa/llm-container
`

### 3. Download the Desired LLM Model from Hugging Face

Download the model you want to use and place it under the models folder.

For this example, we'll be using Mistral-7B-Instruct-v0.3-gguf. If you're using the command line, run the following:

`wget https://huggingface.co/RichardErkhov/mistralai_-_Mistral-7B-Instruct-v0.3-gguf/resolve/main/Mistral-7B-Instruct-v0.3.Q8_0.gguf`


If you're using a web browser, use this link to download the file:

`https://huggingface.co/RichardErkhov/mistralai_-_Mistral-7B-Instruct-v0.3-gguf/resolve/main/Mistral-7B-Instruct-v0.3.Q8_0.gguf`

### 4. Update the `docker-compose.yml` File

If you're using a different model, make sure to specify the model name with namespace(Hugging face) in the environment variable.

For example (downloaded model in model folder): 

`export MODEL_NAME="/models/Mistral-7B-Instruct-v0.3.Q8_0.gguf"
`

To directly use the model from hugging face, you can add the hugging face token and use the model namespace directly.

For example:

`export HF_TOKEN="your_hf_token"`


`export MODEL_NAME="microsoft/Phi-3.5-mini-instruct"
`

To update the GPU utilization percentage, look for the following line in the `docker-compose.yml` file:

`command: --model ${MODEL_NAME:-/models/gemma-2-2b-it} --enable-chunked-prefill --max_model_len 20000 --gpu_memory_utilization 0.8` 

Here, the value `0.8` tells the system to use 80% of the available GPU memory to avoid running out of memory. Based on the model you're using, about 10GB of GPU memory should be sufficient for the LLM container to run with optimal performance. Feel free to adjust this value depending on the GPU memory available on your system.

Note:- The model name you are using should be added to the `config.yaml` file in order for the application to communicate properly with the LLM.

Example (config.yaml):

`llm:
	model: /models/Mistral-7B-Instruct-v0.3.Q8_0.gguf`


### 5. LLM container setup

Make sure you are in the llm-container folder and have completed all the above steps. Then, use `docker-compose up -d` to start the container.

Use `docker ps -a` to check if any containers are already running.

Check if any of the following Docker images are already running:

1. local-llm-container-caddy
2. local-llm-container-llm-container


To view the Docker logs, use:

`docker logs CONTAINER_ID`

Replace CONTAINER_ID with the actual container ID. You can find the container ID by running `docker ps -a`.

If the LLM is running as expected, the llm-container log should show a similar response (towards the end of the log) as the one provided below:

“INFO: Avg prompt throughput: 0.0 tokens/s, Avg generation throughput: 0.0 tokens/s, Running: 0 reqs, Swapped: 0 reqs, Pending: 0 reqs, GPU KV cache usage: 0.0%, CPU KV cache usage: 0.0%.”

You can also use nvidia-smi to verify that the LLM is loaded into the GPU memory.

