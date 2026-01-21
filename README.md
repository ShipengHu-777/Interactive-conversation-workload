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

SentencePiece version: 0.2.1.

GPU: NVIDIA A800 80GB GPU

Host memory: 200GB

CPU: Intel Xeon Platinum 8358 CPU

Linux version: Ubuntu 22.04.5

PCIe version: PCIe 4.0


# Demonstrating key observations in the paper
We provide a large number of easy-to-run python scripts to analyze our workload and reproduce the key observations in our paper. To run these scripts, put these scripts into the folder of "total_worload".

1. Observation 1

To get the conversatioin duration of each user's multi-round conversation, run:
```
python3 conversation duration
```

To get the number of interaction rounds of each user's multi-round conversation, run:
```
python3 conversation round
```

2. Observation 2

To get the weighted reuse distances of KV accesses, run:
```
python3 weighted_reuse_distance.py
```

To get the hit rate of difference eviction policies, run:
```
python3 hit_rate.py
```

3. Observation 3

To validate the large variability of KV loading, run:
```
python3 load_key_value_variation.py
```

4. Getting the relation between the weighted reuse distance lower bound and the model answer length (figure 12).
To get the relation between 8:00-9:00, run:
```
python3 output_rd_relation_8_00.py
```
To get the relation between 9:00-10:00, run:
```
python3 output_rd_relation_9_00.py
```
To get the relation between 10:00-11:00, run:
```
python3 output_rd_relation_10_00.py
```
To get the relation between 11:00-12:00, run:
```
python3 output_rd_relation_11_00.py
```
To get the relation between 12:00-13:00, run:
```
python3 output_rd_relation_12_00.py
```
To get the relation between 13:00-14:00, run:
```
python3 output_rd_relation_13_00.py
```
To get the relation between 14:00-15:00, run:
```
python3 output_rd_relation_14_00.py
```
To get the relation between 15:00-16:00, run:
```
python3 output_rd_relation_15_00.py
```
To get the relation between 16:00-17:00, run:
```
python3 output_rd_relation_16_00.py
```
To get the relation between 17:00-18:00, run:
```
python3 output_rd_relation_17_00.py
```
To get the relation between 18:00-19:00, run:
```
python3 output_rd_relation_18_00.py
```
To get the relation between 19:00-20:00, run:
```
python3 output_rd_relation_19_00.py
```

5. To get the hit rate of the optimal evition policy and exiting policies with different weighted reuse distances (figure 13), run:
```
python3 hit_rate_to_rd.py
```


# The execution commands and expected outputs

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

