import os
import matplotlib.pyplot as plt
import numpy as np
import math



def FIFO(sort_list,cpu_mem,start_time,end_time):
    safe_cpu_mem=2
    cpu_history_list = {}
    disk_history_list = {}
    sum_count = 0
    hit_count = 0
    miss_count = 0
    cpu_remining = cpu_mem



    for(i, record) in enumerate(sort_list):
            time_record = record[0]
            memory_size_tmp = (min(record[1],2048) * 800.0 / 1024) /1024
            memory_size_formatted = "{:.15f}".format(memory_size_tmp)
            memory_size = float(memory_size_formatted)
            end_flag = record[3]
            file_name = record[2]

            if time_record >=end_time:
                sum_count_test = hit_count + miss_count
                hit_rate = hit_count / sum_count_test
                print("sum count is ",sum_count_test)
                return hit_rate
            
            if file_name in cpu_history_list:
                if time_record >= start_time and time_record < end_time:
                    hit_count+=1
                cpu_remining -= (memory_size - cpu_history_list[file_name][0])
                cpu_history_list[file_name][0]=memory_size
                cpu_history_list[file_name][2]+=1
            elif file_name in disk_history_list:
                if time_record >= start_time and time_record < end_time:
                    miss_count += 1
                cpu_remining -= memory_size
                cpu_history_list[file_name] = [memory_size, time_record, 1]
                del disk_history_list[file_name]
            else:
                cpu_remining -= memory_size
                cpu_history_list[file_name] = [memory_size, time_record, 1]

            if end_flag:
                cpu_remining = cpu_remining + cpu_history_list[file_name][0]
                del cpu_history_list[file_name]

            if cpu_remining<safe_cpu_mem:
                sorted_cpu_history_list = sorted(cpu_history_list.items(), key=lambda item: item[1][1])
                for j in range(len(sorted_cpu_history_list)):
                    file_name=sorted_cpu_history_list[j][0]
                    history_size=sorted_cpu_history_list[j][1][0]
                    disk_history_list[file_name]=history_size
                    cpu_remining += history_size
                    del cpu_history_list[file_name]
                    if cpu_remining>=safe_cpu_mem:
                        break

    return




def LRU(sort_list,cpu_mem,start_time,end_time):
    safe_cpu_mem=2
    cpu_history_list = {}
    disk_history_list = {}
    sum_count = 0
    hit_count = 0
    miss_count = 0
    cpu_remining = cpu_mem


    for(i, record) in enumerate(sort_list):
            time_record = record[0]
            
            memory_size_tmp = (min(record[1],2048) * 800.0 / 1024) /1024
            memory_size_formatted = "{:.15f}".format(memory_size_tmp)
            memory_size = float(memory_size_formatted)
            end_flag = record[3]
            file_name = record[2]
      
            if time_record >=end_time:
                sum_count_test = hit_count + miss_count
                hit_rate = hit_count / sum_count_test
                return hit_rate
            

            if file_name in cpu_history_list:
                if time_record >= start_time and time_record < end_time:
                    hit_count+=1
                cpu_remining -= (memory_size - cpu_history_list[file_name][0])
                cur_hit_num=cpu_history_list[file_name][2]
                cpu_history_list[file_name] = [memory_size, time_record, cur_hit_num+1]
            elif file_name in disk_history_list:
                if time_record >= start_time and time_record < end_time:
                    miss_count += 1
                cpu_remining -= memory_size
                del disk_history_list[file_name]
                cpu_history_list[file_name] = [memory_size, time_record, 1]
            else:
                cpu_remining -= memory_size
                cpu_history_list[file_name] = [memory_size, time_record, 1]

            if end_flag:
                cpu_remining = cpu_remining + cpu_history_list[file_name][0]
                del cpu_history_list[file_name]

            if cpu_remining<safe_cpu_mem:
                sorted_cpu_history_list = sorted(cpu_history_list.items(), key=lambda item: item[1][1])
                for j in range(len(sorted_cpu_history_list)):
                    file_name=sorted_cpu_history_list[j][0]
                    history_size=sorted_cpu_history_list[j][1][0]
                    disk_history_list[file_name]=history_size
                    cpu_remining += history_size
                    del cpu_history_list[file_name]
                    if cpu_remining>=safe_cpu_mem:
                        break

                    
    return

# sort_list:[time,history_len,name,end_flag]

def queueEnhanced(sort_list,cpu_mem,start_time,end_time):
    safe_cpu_mem=2
    cpu_history_list = {}
    disk_history_list = {}
    hit_count = 0
    miss_count = 0
    cpu_remining = cpu_mem
    evict_window_count=30

    for(i, record) in enumerate(sort_list):
            time_record = record[0]
            memory_size_tmp = (min(record[1],2048) * 800.0 / 1024) /1024
            memory_size_formatted = "{:.15f}".format(memory_size_tmp)
            memory_size = float(memory_size_formatted)
            end_flag = record[3]
            file_name = record[2]
      
            if time_record >=end_time:
                sum_count_test = hit_count + miss_count
                hit_rate = hit_count / sum_count_test
                return hit_rate
            
            if file_name in cpu_history_list:
                if time_record >= start_time and time_record < end_time:
                    hit_count+=1
                cpu_remining -= (memory_size - cpu_history_list[file_name][0])
                cur_hit_num=cpu_history_list[file_name][2]
                cpu_history_list[file_name] = [memory_size, time_record,cur_hit_num+1]
            elif file_name in disk_history_list:
                if time_record >= start_time and time_record < end_time:
                    miss_count += 1
                cpu_remining -= memory_size
                del disk_history_list[file_name]
                cpu_history_list[file_name] = [memory_size, time_record,1]
            else:
                cpu_remining -= memory_size
                cpu_history_list[file_name] = [memory_size, time_record,1]

            if end_flag:
                cpu_remining += cpu_history_list[file_name][0]
                del cpu_history_list[file_name]

            if cpu_remining<safe_cpu_mem:
                exempt_name_list=[]
                for j in range(evict_window_count):
                    exempt_name_list.append(sort_list[j+i+1][2])
                sorted_cpu_history_list = sorted(cpu_history_list.items(), key=lambda item: item[1][1])
                for j in range(len(sorted_cpu_history_list)):
                    file_name=sorted_cpu_history_list[j][0]
                    if file_name in exempt_name_list:
                        continue
                    history_size=sorted_cpu_history_list[j][1][0]
                    disk_history_list[file_name]=history_size
                    cpu_remining += history_size
                    del cpu_history_list[file_name]
                    if cpu_remining>=safe_cpu_mem:
                        break

    return
  



def main():
    trace_file="total_traces_part2.txt"
    f=open(trace_file,"r")
    list_lines=f.readlines()
    f.close()
    list_lines=list_lines[1:]
    user_list=[]
    for line in list_lines:
        split_list=line.split()
        if int(split_list[-1])==0:
            user_list.append(int(split_list[0]))
    user_list.sort()
    summarized_user_list=[]
    for i in range(len(user_list)):
        if i%10<3:
            summarized_user_list.append(user_list[i])
    sort_list=[]
    user_meta_info={} 
    for line in list_lines:
        split_list=line.split()
        if int(split_list[0]) not in summarized_user_list:
            continue
        if int(split_list[-1])==0:
            user_meta_info[int(split_list[0])]=int(split_list[2])+int(split_list[3])
        else:
            user_meta_info[int(split_list[0])]+=(int(split_list[2])+int(split_list[3]))
        sort_list.append([int(split_list[1]),user_meta_info[int(split_list[0])],int(split_list[0])])

    user_end_names=[]
    for i in range(len(sort_list)):
        trace=sort_list[len(sort_list)-i-1]
        if trace[2] in user_end_names:
            sort_list[len(sort_list)-i-1].append(False)
        else:
            sort_list[len(sort_list)-i-1].append(True)
            user_end_names.append(trace[2])


    cpu_mem=200
    start_time=3600*3
    end_time=start_time+600
    hit_rate=FIFO(sort_list,cpu_mem,start_time,end_time)
    print("FIFO hit rate is ",hit_rate)
    hit_rate=LRU(sort_list,cpu_mem,start_time,end_time)
    print("LRU hit rate is ",hit_rate)
    hit_rate=queueEnhanced(sort_list,cpu_mem,start_time,end_time)
    print("Queue-enhanced hit rate is ",hit_rate)







if __name__ == '__main__':
    main()