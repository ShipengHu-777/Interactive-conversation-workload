import os
import matplotlib.pyplot as plt
import numpy as np
import math
import pickle




def persist_rd_sort_list(sort_list,summarized_user_list,start_time,end_time):
    rd_sort_list=[0 for i in range(len(sort_list))]
    for name in summarized_user_list:
        exclude_name_list = {}
        first_flag = True
        for(i, record) in enumerate(sort_list):
            if record[2] == name and first_flag:
                first_flag = False
                rd_sort_list.append(record)
                continue
            if record[2] != name:
                if not first_flag:
                    exclude_name_list[record[2]]=(min(record[1],2048) * 800.0 / 1024) /1024
            else:
                rd_sort_list[i]=sum(exclude_name_list.values())
                exclude_name_list = {}

    return rd_sort_list
    


def loc_rd_interval_idx(rd):
    index=0
    if rd<200:
        index=0
    elif rd<240:
        index=1
    elif rd<280:
        index=2
    elif rd<320:
        index=3
    elif rd<360:
        index=4
    elif rd<400:
        index=5
    elif rd<440:
        index=6
    elif rd<480:
        index=7
    else:
        index=8
    return index




def FIFO(rd_sort_list,sort_list,cpu_mem,start_time,end_time):
    safe_cpu_mem=2
    cpu_history_list = {}
    disk_history_list = {}
    sum_count = 0
    hit_count = 0
    miss_count = 0
    cpu_remining = cpu_mem



    hit_num_to_rd=[0,0,0,0,0,0,0,0,0,0]
    miss_num_to_rd=[0,0,0,0,0,0,0,0,0,0]



    for(i, record) in enumerate(sort_list):
            time_record = record[0]
            memory_size_tmp = (min(record[1],2048) * 800.0 / 1024) /1024
            memory_size_formatted = "{:.15f}".format(memory_size_tmp)
            memory_size = float(memory_size_formatted)
            end_flag = record[3]
            file_name = record[2]

            
            if file_name in cpu_history_list:
                if time_record >= start_time and time_record < end_time:
                    hit_num_to_rd[loc_rd_interval_idx(rd_sort_list[i])]+=1
                cpu_remining -= (memory_size - cpu_history_list[file_name][0])
                cpu_history_list[file_name][0]=memory_size
                cpu_history_list[file_name][2]+=1
            elif file_name in disk_history_list:
                if time_record >= start_time and time_record < end_time:
                    miss_num_to_rd[loc_rd_interval_idx(rd_sort_list[i])]+=1
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

    return hit_num_to_rd,miss_num_to_rd




def LRU(rd_sort_list,sort_list,cpu_mem,start_time,end_time):
    safe_cpu_mem=2
    cpu_history_list = {}
    disk_history_list = {}

    cpu_remining = cpu_mem

    hit_num_to_rd=[0,0,0,0,0,0,0,0,0,0]
    miss_num_to_rd=[0,0,0,0,0,0,0,0,0,0]



    for(i, record) in enumerate(sort_list):
            time_record = record[0]
            memory_size_tmp = (min(record[1],2048) * 800.0 / 1024) /1024
            memory_size_formatted = "{:.15f}".format(memory_size_tmp)
            memory_size = float(memory_size_formatted)
            end_flag = record[3]
            file_name = record[2]
      

            if file_name in cpu_history_list:
                if time_record >= start_time and time_record < end_time:
                    hit_num_to_rd[loc_rd_interval_idx(rd_sort_list[i])]+=1
                cpu_remining -= (memory_size - cpu_history_list[file_name][0])
                cur_hit_num=cpu_history_list[file_name][2]
                cpu_history_list[file_name] = [memory_size, time_record, cur_hit_num+1]
            elif file_name in disk_history_list:
                if time_record >= start_time and time_record < end_time:
                    miss_num_to_rd[loc_rd_interval_idx(rd_sort_list[i])]+=1
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

    return hit_num_to_rd,miss_num_to_rd




def queueEnhanced(rd_sort_list,sort_list,cpu_mem,start_time,end_time):
    safe_cpu_mem=2
    cpu_history_list = {}
    disk_history_list = {}
    cpu_remining = cpu_mem
    evict_window_count=30

    

    hit_num_to_rd=[0,0,0,0,0,0,0,0,0,0]
    miss_num_to_rd=[0,0,0,0,0,0,0,0,0,0]


    for(i, record) in enumerate(sort_list):
            time_record = record[0]
            memory_size_tmp = (min(record[1],2048) * 800.0 / 1024) /1024
            memory_size_formatted = "{:.15f}".format(memory_size_tmp)
            memory_size = float(memory_size_formatted)
            end_flag = record[3]
            file_name = record[2]
      
            if file_name in cpu_history_list:
                if time_record >= start_time and time_record < end_time:
                    hit_num_to_rd[loc_rd_interval_idx(rd_sort_list[i])]+=1
                cpu_remining -= (memory_size - cpu_history_list[file_name][0])
                cur_hit_num=cpu_history_list[file_name][2]
                cpu_history_list[file_name] = [memory_size, time_record,cur_hit_num+1]
            elif file_name in disk_history_list:
                if time_record >= start_time and time_record < end_time:
                    miss_num_to_rd[loc_rd_interval_idx(rd_sort_list[i])]+=1
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

    
    return hit_num_to_rd,miss_num_to_rd



def fif_optimal(rd_sort_list,sort_list,cpu_mem,start_time,end_time):
    safe_cpu_mem=2
    cpu_history_list = {}
    disk_history_list = {}
    cpu_remining = cpu_mem


    hit_num_to_rd=[0,0,0,0,0,0,0,0,0,0]
    miss_num_to_rd=[0,0,0,0,0,0,0,0,0,0]


    for(i, record) in enumerate(sort_list):
            time_record = record[0]
            memory_size_tmp = (min(record[1],2048) * 800.0 / 1024) /1024
            memory_size_formatted = "{:.15f}".format(memory_size_tmp)
            memory_size = float(memory_size_formatted)
            end_flag = record[3]
            file_name = record[2]

            if time_record>=end_time:
                break

            next_idx=i+1
            while 1:
                if next_idx>=len(sort_list):
                    break
                if sort_list[next_idx][2]==file_name:
                    break
                next_idx+=1

            if file_name in cpu_history_list:
                if time_record >= start_time and time_record < end_time:
                    hit_num_to_rd[loc_rd_interval_idx(rd_sort_list[i])]+=1
                cpu_remining -= (memory_size - cpu_history_list[file_name][0])
            elif file_name in disk_history_list:
                if time_record >= start_time and time_record < end_time:
                    miss_num_to_rd[loc_rd_interval_idx(rd_sort_list[i])]+=1
                cpu_remining -= memory_size
                del disk_history_list[file_name]
            else:
                cpu_remining -= memory_size
            cpu_history_list[file_name] = [memory_size, next_idx]


            if end_flag:
                cpu_remining = cpu_remining + cpu_history_list[file_name][0]
                del cpu_history_list[file_name]


            if cpu_remining<safe_cpu_mem:
                sorted_cpu_history_list = sorted(cpu_history_list.items(), key=lambda item: item[1][1],reverse=True)
                for j in range(len(sorted_cpu_history_list)):
                    file_name=sorted_cpu_history_list[j][0]
                    history_size=sorted_cpu_history_list[j][1][0]
                    disk_history_list[file_name]=history_size
                    cpu_remining += history_size
                    del cpu_history_list[file_name]
                    if cpu_remining>=safe_cpu_mem:
                        break

                    
   

    return hit_num_to_rd,miss_num_to_rd

  

def test_cache_hit_rate_2_rd(rd_sort_list,sort_list,start_time,end_time):
    fifo_hit_rate=[]
    lru_hit_rate=[]
    queue_enhance_hit_rate=[]
    opt_hit_rate=[]
    hist_num=9
    cpu_mem=200

    print("FIFO")
    fifo_hit_num,fifo_miss_num=FIFO(rd_sort_list,sort_list,cpu_mem,start_time,end_time)
    for i in range(hist_num):
        if fifo_hit_num[i]==0:
            fifo_hit_rate.append(0)
            continue
        fifo_hit_rate.append(fifo_hit_num[i]/(fifo_hit_num[i]+fifo_miss_num[i]))


    print("LRU")
    lru_hit_num,lru_miss_num=LRU(rd_sort_list,sort_list,cpu_mem,start_time,end_time)
    for i in range(hist_num):
        if lru_hit_num[i]==0:
            lru_hit_rate.append(0)
            continue
        lru_hit_rate.append(lru_hit_num[i]/(lru_hit_num[i]+lru_miss_num[i]))



    print("Queue-enhanced")
    queue_enhance_hit_num,queue_enhance_miss_num=queueEnhanced(rd_sort_list,sort_list,cpu_mem,start_time,end_time)
    for i in range(hist_num):
        if queue_enhance_hit_num[i]==0:
            queue_enhance_hit_rate.append(0)
            continue
        queue_enhance_hit_rate.append(queue_enhance_hit_num[i]/(queue_enhance_hit_num[i]+queue_enhance_miss_num[i]))

    
    print("Optimal")
    opt_hit_num,opt_miss_num=fif_optimal(rd_sort_list,sort_list,cpu_mem,start_time,end_time)
    for i in range(hist_num):
        if opt_hit_num[i]==0:
            opt_hit_rate.append(0)
            continue
        opt_hit_rate.append(opt_hit_num[i]/(opt_hit_num[i]+opt_miss_num[i]))



    plt.figure(figsize=(10,3.5))
    ax=plt.gca()
    x=np.arange(hist_num)
    width=0.13
    ax.bar(x-width*1.5,fifo_hit_rate,width,color='salmon',edgecolor="k",label="FIFO")
    ax.bar(x-width*0.5,lru_hit_rate,width,color='steelblue',edgecolor="k",hatch='X',label="LRU")
    ax.bar(x+width*0.5,queue_enhance_hit_rate,width,color='sandybrown',edgecolor='k',hatch='.',label="Queue-enhanced")
    ax.bar(x+width*1.5,opt_hit_rate,width,color='royalblue',edgecolor='k',label="Optimal")

    # ax.set_ylabel('Hit rate',fontsize=20)

    # ax.set_xlabel('Weighted reuse distance (GB)',fontsize=20)


    ax.set_yticks(np.arange(0, 1.01, step=0.2),fontsize=20)
    ax.set_yticklabels(['0','20%','40%','60%','80%','100%'],fontsize=14)

    
    ax.set_xlim(0-0.6,8.6)
    ax.set_xticks(np.arange(0, 8.01, step=1),fontsize=20)
    ax.set_xticklabels(['<200','200-240','240-280','280-320','320-360','360-400','400-440','440-480','>480'],fontsize=14)

    plt.tight_layout()
    plt.legend(loc='upper right',ncol=2, prop = {'size':12})
    plt.show()
    


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
    start_time=3600*3
    end_time=start_time+600


    for line in list_lines:
        split_list=line.split()
        if int(split_list[0]) not in summarized_user_list:
            continue

        if int(split_list[-1])==0:
            sort_list.append([int(split_list[1]),0,int(split_list[0])])
            user_meta_info[int(split_list[0])]=int(split_list[2])+int(split_list[3])
        else:
            sort_list.append([int(split_list[1]),user_meta_info[int(split_list[0])],int(split_list[0])])
            user_meta_info[int(split_list[0])]+=(int(split_list[2])+int(split_list[3]))

    user_end_names=[]
    for i in range(len(sort_list)):
        trace=sort_list[len(sort_list)-i-1]
        if trace[2] in user_end_names:
            sort_list[len(sort_list)-i-1].append(False)
        else:
            sort_list[len(sort_list)-i-1].append(True)
            user_end_names.append(trace[2])


    # a slow process
    rd_sort_list=persist_rd_sort_list(sort_list,summarized_user_list,start_time,end_time)

    test_cache_hit_rate_2_rd(rd_sort_list,sort_list,start_time,end_time)
    











if __name__ == '__main__':
    main()