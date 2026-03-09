# Interactive conversation workload
The total trace of interactive conversation workload.
Format:
User_id, Timestamp(seconds), Query_length, Response_length, Round_index.  

# The required environment and dependencies

Docker image: nvcr.io/nvidia/pytorch:23.10-py3

vLLM version: 0.1.7

Ray version: 2.48.0

safetensors version: 0.6.2

sniffio version: 1.3.1

tokenizers version: 0.21.4

SentencePiece version: 0.2.1

GPU: NVIDIA A800 80GB GPU

PCIe version: PCIe 4.0


# Demonstrating key observations in the paper
We provide python scripts to analyze our workload. To run these scripts, put these scripts into the folder of "total_workload".

### Observation 1 

To get the conversation duration of each user's multi-round conversation, run:
```
python3 conversation_duration.py
```

To get the number of interaction rounds of each user's multi-round conversation, run:
```
python3 conversation_round.py
```

### Observation 2

To get the weighted reuse distances of KV accesses, run:
```
python3 weighted_reuse_distance.py
```


### Observation 3

To validate the large variability of KV loading, run:
```
python3 load_key_value_variation.py
```

To get the observation of the WRD lower bound, run:
```
python3 output_rd_relation.py
```



# The scripts to run the trace

It is more recommended to re-implement your own scripts to run the trace, due to different versions of vLLM (the version of vLLM used here is rather old).

1. Download the docker image: nvcr.io/nvidia/pytorch:23.10-py3, and download vLLM repository.

2. Run image:
```
docker run --gpus all -it --ipc=host -v /data/test:/app -d nvcr.io/nvidia/pytorch:23.10-py3 /bin/bash
```

3. Run docker:
```
docker exec -it ea91dfe3a6c9 /bin/bash
```

4. Enter vLLM repository and install dependencies: 

```
pip install -r requirements.txt -i https://mirrors.ustc.edu.cn/pypi/web/simple
```
```
pip install -e . -i https://mirrors.ustc.edu.cn/pypi/web/simple
```

5. Put the trace_llm_engine_demo.py under the "engine" folder of vLLM.

6. Run the trace:
```
python trace_entry_demo.py --model /app/opt-13b/
```

For different user arrival rates, conduct simple user sampling and adjust sampling ratios on the workload.

