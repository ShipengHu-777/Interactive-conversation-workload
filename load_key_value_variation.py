import os
import matplotlib.pyplot as plt
import numpy as np


def draw_vary_loaded_size(history_size_num_hist):
    width=0.5
    plt.figure(figsize=(8,3))
    ax=plt.gca()
    ax.bar([i for i in range(9)],history_size_num_hist,width,color='salmon',edgecolor="k")
    ax.set_ylabel('Number of requests',fontsize=18)
    ax.set_xlabel('\nLoaded Key/Value size (MB)',fontsize=18)
    ax.set_xticks([])
    plt.yticks(fontsize=20)
    plt.tight_layout()
    plt.show()


def main():
    load_history_lens=[]
    for i in range(7):
        print("i=",i)
        trace_file="total_traces_part"+str(i+1)+".txt"
        f=open(trace_file,"r")
        list_lines=f.readlines()
        f.close()
        list_lines=list_lines[1:]
        user_history_lens={}
        for line in list_lines:
            split_list=line.split()
            if int(split_list[-1])==0:
                load_history_lens.append(0)
                user_history_lens[split_list[0]]=(int(split_list[2])+int(split_list[3]))
            else:
                load_history_lens.append(user_history_lens[split_list[0]])
                user_history_lens[split_list[0]]+=(int(split_list[2])+int(split_list[3]))
    history_size_mb=[]
    for history_per_len in load_history_lens:
        # key or value size
        history_size_mb.append((800*history_per_len/1024.0)/2)
    history_size_num_hist=[0 for i in range(9)]
    for per_size in history_size_mb:
        if per_size<100:
            history_size_num_hist[0]+=1
        elif per_size<200:
            history_size_num_hist[1]+=1
        elif per_size<300:
            history_size_num_hist[2]+=1
        elif per_size<400:
            history_size_num_hist[3]+=1
        elif per_size<500:
            history_size_num_hist[4]+=1
        elif per_size<600:
            history_size_num_hist[5]+=1
        elif per_size<700:
            history_size_num_hist[6]+=1
        elif per_size<800:
            history_size_num_hist[7]+=1
        else:
            history_size_num_hist[8]+=1

    draw_vary_loaded_size(history_size_num_hist)





if __name__ == '__main__':
    main()