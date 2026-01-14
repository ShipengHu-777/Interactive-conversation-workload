import asyncio
import time
from functools import partial
from typing import (Any, Dict, Iterable, List, Optional, Set, Tuple, Type,
                    Union)

from vllm.config import ModelConfig
from vllm.engine.arg_utils import AsyncEngineArgs
from vllm.engine.llm_engine import LLMEngine
from vllm.engine.ray_utils import initialize_cluster, ray
from vllm.logger import init_logger
from vllm.outputs import RequestOutput
from vllm.sampling_params import SamplingParams
import random
import queue


logger = init_logger(__name__)


class AsyncEngineDeadError(RuntimeError):
    pass

request_serve_time_stamp={}




class RequestTracker:
    """Synchronous abstraction for tracking requests."""

    def __init__(self) -> None:
        self._finished_requests = queue.Queue()
        self._new_requests = queue.Queue()
        self.new_requests_event = None
        
        self.total_latency=0
        self.total_finished_req=0

        


    def process_request_output(self,
                               request_output: RequestOutput,
                               running_request_record:Dict[str,int],
                               *,
                               verbose: bool = False) -> Any:
        """Process a request output from the engine."""
        request_id = request_output.request_id


        if request_output.finished:
            request_serve_time_stamp[request_id].append(time.time())
            cur_latency=request_serve_time_stamp[request_id][1]-request_serve_time_stamp[request_id][0]
            self.total_latency+=cur_latency
            self.total_finished_req+=1

            request_serve_time_stamp.pop(request_id)
            del running_request_record[request_id]            
            self.abort_request(request_id)
            return running_request_record
  

    def add_request(self, request_id: str,
                    **engine_add_request_kwargs):
        """Add a request to be sent to the engine on the next background
        loop iteration."""


        self._new_requests.put( {
            "request_id": request_id,
            **engine_add_request_kwargs
        })



    def abort_request(self, request_id: str, *, verbose: bool = False) -> None:
        """Abort a request during next background loop iteration."""
        if verbose:
            logger.info(f"Aborted request {request_id}.")

        self._finished_requests.put(request_id)

 

    def get_new_and_finished_requests(self) -> Tuple[List[dict], Set[str]]:
        """Get the new requests and finished requests to be
        sent to the engine."""
        new_requests: List[dict] = []
        finished_requests: Set[str] = set()

        while not self._finished_requests.empty():
            request_id = self._finished_requests.get()
            finished_requests.add(request_id)


        while not self._new_requests.empty():
            new_request = self._new_requests.get()
            new_requests.append(new_request)



        return new_requests, finished_requests

    



class _TraceLLMEngine(LLMEngine):
    """Extension of LLMEngine to add async methods."""

    def step_sync(self) -> List[RequestOutput]:
        """Performs one decoding iteration and returns newly generated results.
        The workers are ran asynchronously if possible.

        This function performs one decoding iteration of the engine. It first
        schedules the sequences to be executed in the next iteration and the
        token blocks to be swapped in/out/copy. Then, it executes the model
        and updates the scheduler with the model outputs. Finally, it decodes
        the sequences and returns the newly generated results.
        """
        
       

        seq_group_metadata_list, scheduler_outputs, ignored = self._schedule()
      
        

        self.avg_batch_size=(self.avg_batch_size*self.total_step_num+len(seq_group_metadata_list))/(self.total_step_num+1)
        (self.total_step_num)+=1

        # logger.info(
        #             f"current batch size is: {len(seq_group_metadata_list)}")
        # logger.info(
        #             f"avg batch size is: {self.avg_batch_size}")
        if scheduler_outputs.is_empty():
            return ignored

        
     
        # Execute the model.
        output, seq_ids_processed = self._run_workers_sync(
            "execute_model",
            seq_group_metadata_list=seq_group_metadata_list,
            blocks_to_swap_in=scheduler_outputs.blocks_to_swap_in,
            blocks_to_swap_out=scheduler_outputs.blocks_to_swap_out,
            blocks_to_copy=scheduler_outputs.blocks_to_copy,
        )
        
       

  

        return self._process_model_outputs(output, scheduler_outputs, seq_ids_processed) + ignored


    # there will be a problem when running with ray, need to be fixed.
    def _run_workers_sync(
        self,
        method: str,
        *args,
        get_all_outputs: bool = False,
        **kwargs,
    ) -> Any:
        """Runs the given method on all workers."""
        all_outputs = []
        for worker in self.workers:
            if self.parallel_config.worker_use_ray:
                executor = partial(worker.execute_method.remote, method)
            else:
                executor = getattr(worker, method)

            output, seq_ids_processed = executor(*args, **kwargs)
            all_outputs.append(output)

        if get_all_outputs:
            return all_outputs

        # Make sure all workers have the same results.
        output = all_outputs[0]
        for other_output in all_outputs[1:]:
            assert output == other_output
        return output, seq_ids_processed


class TraceLLMEngine:
    """An asynchronous wrapper for LLMEngine.

    This class is used to wrap the LLMEngine class to make it asynchronous. It
    uses asyncio to create a background loop that keeps processing incoming
    requests. The LLMEngine is kicked by the generate method when there
    are requests in the waiting queue. The generate method yields the outputs
    from the LLMEngine to the caller.

    NOTE: For the comprehensive list of arguments, see `LLMEngine`.

    Args:
        worker_use_ray: Whether to use Ray for model workers. Required for
            distributed execution. Should be the same as
            `parallel_config.worker_use_ray`.
        engine_use_ray: Whether to make LLMEngine a Ray actor. If so, the
            async frontend will be executed in a separate process as the
            model workers.
        log_requests: Whether to log the requests.
        start_engine_loop: If True, the background task to run the engine
            will be automatically started in the generate call.
        *args, *kwargs: Arguments for LLMEngine.
    """

    _engine_class: Type[_TraceLLMEngine] = _TraceLLMEngine

    def __init__(self,
                 worker_use_ray: bool,
                 engine_use_ray: bool,
                 *args,
                 log_requests: bool = True,
                 max_log_len: Optional[int] = None,
                 start_engine_loop: bool = True,
                 **kwargs) -> None:
        self.worker_use_ray = worker_use_ray
        self.engine_use_ray = engine_use_ray
        self.log_requests = log_requests
        self.max_log_len = max_log_len
        self.engine = self._init_engine(*args, **kwargs)

        self._request_tracker = RequestTracker()
        self.listoflines=[]
        


        self.running_request_record={}
        
        self.total_delayed_request_num=0


   


    def _init_engine(self, *args,
                     **kwargs) -> Union[_TraceLLMEngine, "ray.ObjectRef"]:
        if not self.engine_use_ray:
            engine_class = self._engine_class
        elif self.worker_use_ray:
            engine_class = ray.remote(num_cpus=0)(self._engine_class).remote
        else:
            engine_class = ray.remote(num_gpus=1)(self._engine_class).remote
        return engine_class(*args, **kwargs)

    def engine_step(self) -> bool:
        """Kick the engine to process the waiting requests.

        Returns True if there are in-progress requests."""
        new_requests, finished_requests = (
            self._request_tracker.get_new_and_finished_requests())

        
        for new_request in new_requests:
            if self.engine_use_ray:
                self.engine.add_request.remote(**new_request)
            else:
                self.engine.add_request(**new_request)
        
        
        


        if self.engine_use_ray:
            request_outputs = self.engine.step.remote()
        else:
            request_outputs = self.engine.step_sync()

        # Put the outputs into the corresponding streams.
        for request_output in request_outputs:
            res = self._request_tracker.process_request_output(
                request_output,self.running_request_record, verbose=self.log_requests)
            if res is not None:
                self.running_request_record=res
     
        return len(request_outputs) > 0

    def _engine_abort(self, request_ids: Iterable[str]):

        self.engine.abort_request(request_ids)

    
    def sync_add_request(
        self,
        request_id: str,
        prompt: Optional[str],
        sampling_params: SamplingParams,
        prompt_token_ids: Optional[List[int]] = None,
        arrival_time: Optional[float] = None,
        input_len: Optional[int] = 0,
    ):
        if self.log_requests:
            shortened_prompt = prompt
            shortened_token_ids = prompt_token_ids
            if self.max_log_len is not None:
                if shortened_prompt is not None:
                    shortened_prompt = shortened_prompt[:self.max_log_len]
                if shortened_token_ids is not None:
                    shortened_token_ids = shortened_token_ids[:self.
                                                              max_log_len]
            # logger.info(f"Received request {request_id}: ")
            request_serve_time_stamp[request_id]=[]
            request_serve_time_stamp[request_id].append(time.time())
                        # f"prompt: {shortened_prompt!r}, "
                        # f"sampling params: {sampling_params}, "
                        # f"prompt token ids: {shortened_token_ids}.")
        self._request_tracker.add_request(
            request_id,
            prompt=prompt,
            sampling_params=sampling_params,
            prompt_token_ids=prompt_token_ids,
            arrival_time=arrival_time,
            input_len=input_len)
        

   
    def generate(
            self):
        

        start_time=time.time()
        f=open("sampled_traces.txt","r")
        self.listoflines=f.readlines()
        f.close()
        request_counter=1
        issue_time=0
        has_requests_in_progress = False
        
  
        while True:
            now_time=time.time()
            has_requests_in_progress, end_flag, request_counter = self.process_trace_file(request_counter,start_time,now_time)
            if end_flag:
                return
            has_requests_in_progress = self.engine_step()

            

           
    def process_trace_file(self,request_counter,start_time,now_time):
        add_trace_flag=False
        issue_time=0
        while 1:
            if request_counter>=len(self.listoflines):
                return add_trace_flag,True,request_counter

            line=self.listoflines[request_counter]
            line=line[:len(line)-1]
            split_list=line.split()
            request_id=request_counter
            input_len = int(split_list[2])

            input_token_num=input_len
            input_token_ids=[]
            for i in range(input_token_num):
                input_token_ids.append(random.randint(1,100))
            prompt=None

            output_token_num=int(split_list[3])
            sampling_params = SamplingParams(max_tokens=output_token_num)
            
            issue_time=int(split_list[1])
        
            gap_time=now_time-start_time
            current_iteration = int(split_list[4]-1)
            
            if gap_time >= issue_time:
                self.running_request_record[request_id]=current_iteration            
                self.sync_add_request(request_id,
                                        prompt,
                                        sampling_params,
                                        prompt_token_ids=input_token_ids,
                                        arrival_time=issue_time,
                                        input_len=input_len)
                add_trace_flag=True
                request_counter+=1
            else:
                break

        return add_trace_flag,False,request_counter
        
            



    @classmethod
    def from_engine_args(cls,
                         engine_args: AsyncEngineArgs,
                         start_engine_loop: bool = True) -> "TraceLLMEngine":
        """Creates an async LLM engine from the engine arguments."""
        # Create the engine configs.
        engine_configs = engine_args.create_engine_configs()
        parallel_config = engine_configs[2]
        # Initialize the cluster.
        distributed_init_method, placement_group = initialize_cluster(
            parallel_config, engine_args.engine_use_ray)
        # Create the async LLM engine.
        engine = cls(engine_args.worker_use_ray,
                     engine_args.engine_use_ray,
                     *engine_configs,
                     distributed_init_method,
                     placement_group,
                     log_requests=not engine_args.disable_log_requests,
                     log_stats=not engine_args.disable_log_stats,
                     max_log_len=engine_args.max_log_len,
                     start_engine_loop=start_engine_loop)
        return engine
