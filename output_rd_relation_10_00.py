import os
import matplotlib.pyplot as plt
import random
import numpy as np
import math
from multiprocessing import Process
from multiprocessing.sharedctypes import Array
import pickle
import scipy.stats as stats





def draw_rd_output_token_len(rd_token_time_list):
    reduced_x=[]
    reduced_y=[]

    min_dic={}

    total_num=0
    for my_item in rd_token_time_list:
        if my_item[0] in min_dic:
            min_dic[my_item[0]].append(my_item[1])
        else:
            min_dic[my_item[0]]=[my_item[1]]
        total_num+=1
    count_i=0

    for key,value in min_dic.items():
        min_dic[key].sort()
        len_list=len(min_dic[key])
        q1=min_dic[key][int(len_list*0.25)]
        q3=min_dic[key][int(len_list*0.75)]
        IQR=q3-q1
        lower_bound=q1-1.5*IQR
        new_list=[]
        for val in min_dic[key]:
            if val>=lower_bound:

                new_list.append(val)
                if count_i%2==0:
                    reduced_x.append(key)
                    reduced_y.append(val)
                count_i+=1
        min_dic[key]=new_list





    min_x=[]
    min_y=[]
    for key,value in min_dic.items():
        min_x.append(key)
        min_y.append(min(value))




    plt.figure(figsize=(4.5, 3.5))
    plt.scatter(reduced_x,reduced_y,s=1)
    plt.scatter(min_x,min_y,color='red',s=10)
    # plt.xlabel('Previous round\'s model answer length',fontsize=20)
    # plt.ylabel('Weighted Reuse Distance(GB)',fontsize=16)
    plt.xlim(0,250)
    plt.ylim(50,690)
    plt.grid(True)
    plt.yticks(fontsize=20)
    plt.xticks(fontsize=20)
    plt.tight_layout()
    plt.show()


def persist_rd_sort_list_last_round_token(sort_list_last_round_token,summarized_user_list,start_time,end_time):
    rd_token_time_list=[]
    for name in summarized_user_list:
        exclude_name_list = {}
        first_flag = True
        for(i, record) in enumerate(sort_list_last_round_token):
            if record[0]<start_time or record[0]>end_time:
                continue
            if record[2] == name and first_flag:
                first_flag = False
                continue
            if record[2] != name:
                if not first_flag:
                    exclude_name_list[record[2]]=(min(record[1],2048) * 800)/(1024*1024)
            else:
                rd_token_time_list.append((record[-1],(sum(exclude_name_list.values())),record[0]))
                exclude_name_list = {}
    return rd_token_time_list





# ten minute trace during 10:00-11:00
def main():
    trace_file="total_traces_part2.txt"
    f=open(trace_file,"r")
    list_lines=f.readlines()
    f.close()
    list_lines=list_lines[1:]
    user_list=[]
    start_hour=3600*3
    end_hour=start_hour+3600
    for line in list_lines:
        split_list=line.split()
        if int(split_list[-1])==0 and int(split_list[1])>=start_hour and int(split_list[1])<=end_hour:
            user_list.append(int(split_list[0]))
    user_list.sort()
    summarized_user_list=[]
    for i in range(len(user_list)):
        if i%10<5:
            summarized_user_list.append(user_list[i])
    user_meta_info={} 
    sort_list_last_round_token=[]
    for line in list_lines:
        split_list=line.split()
        if int(split_list[0]) not in summarized_user_list:
            continue
        if int(split_list[-1])==0:
            sort_list_last_round_token.append([int(split_list[1]),0,int(split_list[0]),0])
            user_meta_info[int(split_list[0])]=[int(split_list[2])+int(split_list[3]),int(split_list[3])]
        else:
            sort_list_last_round_token.append([int(split_list[1]),user_meta_info[int(split_list[0])][0],int(split_list[0]),user_meta_info[int(split_list[0])][1]])
            user_meta_info[int(split_list[0])][0]+=(int(split_list[2])+int(split_list[3]))
            user_meta_info[int(split_list[0])][1]=int(split_list[3])
    print("finish reading")

    start_time=start_hour+1200
    end_time=start_time+600
    rd_token_num_list=persist_rd_sort_list_last_round_token(sort_list_last_round_token,summarized_user_list,start_time,end_time)
    print("finish sorting")
    draw_rd_output_token_len(rd_token_num_list)
    




if __name__ == '__main__':
    main()