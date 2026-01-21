import os
import matplotlib.pyplot as plt
import numpy as np
import math






def draw_reuse_dist(sort_list,summarized_user_list):
    rd_size_record = []
    
    for name in summarized_user_list:
        count = 0
        exclude_name_list = {}
        first_flag = True
        for(i, record) in enumerate(sort_list):
            if record[0] < 3600*3:
                continue
            if record[0] > 3600*3+600:
                break
            if record[2] != name:
                if not first_flag:
                    exclude_name_list[record[2]]=min(record[1],2048) * 800.0 / 1024
            else:
                if first_flag:
                    first_flag = False
                    continue
                rd_size_record.append(sum(exclude_name_list.values()))
                exclude_name_list = {}


    
    rd_size_list = np.sort(rd_size_record)
    cdf = np.arange(1, len(rd_size_list)+1) / len(rd_size_list)
    
    rd_size_list_GB = rd_size_list / 1024.0
    for i in range(len(rd_size_list_GB)):
        if rd_size_list_GB[i]>=200:
            print("200 ratio is ",cdf[i])
            break

    plt.figure(figsize=(9, 6))
    plt.plot(rd_size_list_GB, cdf, marker='o', color='seagreen',linewidth=5, markersize=6)
    plt.xlabel('Weighted reuse distance(GB)',fontsize=30)
    plt.ylabel('CDF',fontsize=30)
    plt.yticks(fontsize=26)
    plt.xticks(fontsize=26)
    plt.ylim(bottom=0)
    plt.xlim(50,590)
    plt.grid(True)
    plt.tight_layout()
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


    draw_reuse_dist(sort_list,summarized_user_list)







if __name__ == '__main__':
    main()