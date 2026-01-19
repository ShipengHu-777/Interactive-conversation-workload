# Interactive conversation workload
The total trace of interactive conversation workload.
Format:
User_id, Timestamp(seconds), Query_length, Response_length, Round_index.  

We provide a demo code to run the trace.
Specifically, run trace_entry_demo.py to execute the above trace using vLLM.
It will call the function in trace_llm_engine_demo.py to replay the trace.
Put the trace_llm_engine_demo.py under the "engine" folder of vLLM.
