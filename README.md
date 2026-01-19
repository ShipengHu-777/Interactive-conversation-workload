# Interactive conversation workload
The total trace of interactive conversation workload.
Format:
User_id, Timestamp(seconds), Query_length, Response_length, Round_index.  

**The required environment and dependencies:**

Docker image: nvcr.io/nvidia/pytorch:23.10-py3, vLLM version: 0.1.7, Ray version: 2.48.0, safetensors version: 0.6.2, sniffio version: 1.3.1, tokenizers version: 0.21.4, sentencepiece version: 0.2.1.
GPU: NVIDIA A800 80GB GPU
Host memory: 200GB
CPU: Intel Xeon Platinum 8358 CPU
Linux version: Ubuntu 22.04.5
PCIe version: PCIe 4.0


We provide a demo code to run the trace.
Specifically, run trace_entry_demo.py to execute the above trace using vLLM.
It will call the function in trace_llm_engine_demo.py to replay the trace.
Put the trace_llm_engine_demo.py under the "engine" folder of vLLM.
