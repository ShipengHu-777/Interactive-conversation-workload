import argparse
from typing import AsyncGenerator
import asyncio

from vllm.engine.arg_utils import AsyncEngineArgs
from vllm.engine.async_llm_engine import AsyncLLMEngine
from vllm.engine.trace_llm_engine import TraceLLMEngine
from vllm.sampling_params import SamplingParams
from vllm.utils import random_uuid



engine = None




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser = AsyncEngineArgs.add_cli_args(parser)
    args = parser.parse_args()

    engine_args = AsyncEngineArgs.from_cli_args(args)
    engine = TraceLLMEngine.from_engine_args(engine_args)
    engine.generate()

   
