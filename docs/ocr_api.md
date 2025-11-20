## OCR setup with Docker
Version 2025.11.19

To set up OCR with Docker, you need to install and configure a GPU. You can also use it without a GPU, but this might affect performance.

To verify and configure GPU support for Docker, please follow the instructions provided in the [NVIDIA Container Toolkit Installation Guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html).

Once Docker is configured to use GPUs, you can run docTR Docker containers with GPU support.

To test with nvidia-smi inside a Docker container

```shell
docker run --rm --gpus all nvidia/cuda:12.3.0-base-ubuntu20.04 nvidia-smi
```

- If it prints out the GPU status (model, memory, usage), your Docker is correctly using the GPU.

- If you see an error like nvidia-smi: command not found or "no CUDA-capable device is detected", GPU is not correctly set up.

## Usage

### Starting your web server

You will need to clone the repository first, go into `api` folder and start the api:

```shell
cd /opt
git clone https://github.com/mindee/doctr.git
cd doctr/api
```

[More information](https://github.com/mindee/doctr/blob/main/api/README.md)

## To change the port address

Skip this step if port 8080 on your host machine is not being used by any other services. If your LLM is using port 8080, you will need to host OCR on another port, such as 8002.

Edit docker-compose.yml in the doctr/api folder

```yaml
ports:
      - 8080:8080
```

to

```yaml
ports:
      - 8002:8080
```

If you need to use OCR with a GPU, also add the following lines to the docker-compose.yml file.

```yaml
runtime: nvidia
environment:
  - NVIDIA_VISIBLE_DEVICES=all  # or "0" for a specific GPU
```

The updated docker-compose.yml will be as follows:

```yaml
services:
  web:
    container_name: ocr_api_web
    build:
      context: .
      dockerfile: Dockerfile
    command: uvicorn app.main:app --reload --workers 1 --host 0.0.0.0 --port 8080
    ports:
      - 8002:8080
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all  # or "0" for a specific GPU
```

Now,

```shell
make run
```

Once completed, your [FastAPI](https://fastapi.tiangolo.com/) server should be running on port 8002.

See config.yaml.example for configuring OCR API parameters.

```yaml
ocr:
  api_uri: http://localhost:8002/ocr
  det_arch: db_resnet50
  reco_arch: vitstr_base
  verify-HTTPS: false
```

Edit 'workflow-config.yaml', and use 'extract_text_doctr_api' instead of 'extract_text_doctr' to use the OCR API endpoint.

Note: The first time you use the function 'extract_text_doctr_api', the system may seem to pause but it is just take a long time to download and install the model on first run. However, on second run of the function, it will be alot faster.

To stop and remove the OCR container:
```shell
docker ps -a
docker stop ocr_web_api
docker rm ocr_web_api
```

## Troubleshoot

### AI-MOA stops working, the logs show the process stalls during ocr process.

If you are using the OCR docker version, sometimes the OCR model unloads from memory. You can verify this by checking ```nvidia-smi``` which should show you the memory usage. If you compare the current memory usage from the previous fully loaded memory usage (llm-container and OCR doctr usage) then you may notice that the main LLM model from llm-container is still loaded, but the total video memory usage is less the OCR model.

Simple restart the OCR docker container:
```
/usr/bin/docker restart ocr_web_api
```

