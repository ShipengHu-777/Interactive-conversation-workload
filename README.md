# Interactive conversation workload
The total trace of interactive conversation workload.
Format:
User_id, Timestamp(seconds), Query_length, Response_length, Round_index.  

**The required environment and dependencies:**

Docker image: nvcr.io/nvidia/pytorch:23.10-py3

vLLM version: 0.1.7

Ray version: 2.48.0

safetensors version: 0.6.2

sniffio version: 1.3.1

tokenizers version: 0.21.4

SentencePiece version: 0.2.1.

GPU: NVIDIA A800 80GB GPU

Host memory: 200GB

CPU: Intel Xeon Platinum 8358 CPU

Linux version: Ubuntu 22.04.5

PCIe version: PCIe 4.0

**The execution commands and expected outputs:**

1. Download the docker image: nvcr.io/nvidia/pytorch:23.10-py3, and download vLLM repository.

2. Run image:
```
docker run --gpus all -it --ipc=host -v /data/test:/app -d nvcr.io/nvidia/pytorch:23.10-py3 /bin/bash
```

3. Run docker:
```
docker exec -it ea91dfe3a6c9 /bin/bash
```

4. Enter vLLM repository and Install dependicies: 

```
pip install -r requirements.txt -i https://mirrors.ustc.edu.cn/pypi/web/simple
```
```
pip install -e . -i https://mirrors.ustc.edu.cn/pypi/web/simple
```

5. Put the trace_llm_engine_demo.py under the "engine" folder of vLLM.

6. Run the trace:
```
python trace_entry.py --model /app/opt-13b/
```

The script will capture the arrival time of each request and the return time of each request. Each request’s latency and the average latency will be printed. 

The expected output:

```
Start reading trace file.
Finish reading trace file, the total request number is xxx.
Start replaying the trace.
Request 1 returns, latency is xx
The average latency is xx
Request 2 returns, latency is xx
The average latency is xx
……
Finish replaying all the traces.
```

For different user arrival rates, conduct simple user sampling and adjust sampling ratios on the workload.

