import os
import matplotlib.pyplot as plt
import numpy as np

def draw_alive_time(time_list):
    usage_durations = np.sort(time_list)
    cdf = np.arange(1, len(usage_durations)+1) / len(usage_durations)
    plt.figure(figsize=(8, 3.5))


    plt.plot(usage_durations/60, cdf, marker='o', color='seagreen',linewidth=5, markersize=6)
    plt.xlabel('User conversation duration (Min)',fontsize=24)
    plt.ylabel('CDF',fontsize=24)
    plt.yticks(fontsize=22)
    plt.xlim(0,60)
    plt.xticks(fontsize=22)
    plt.ylim(bottom=0)
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def main():
    time_list=[]
    for i in range(7):
        print("i=",i)
        trace_file="total_traces_part"+str(i+1)+".txt"
        f=open(trace_file,"r")
        list_lines=f.readlines()
        f.close()
        list_lines=list_lines[1:]
        user_start_time={}
        user_end_time={}
        for line in list_lines:
            split_list=line.split()
            if int(split_list[-1])==0:
                user_start_time[split_list[0]]=int(split_list[1])
            else:
                user_end_time[split_list[0]]=int(split_list[1])
        for key,val in user_end_time.items():
            time_list.append(val-user_start_time[key])
        for j in range(len(user_start_time)-len(user_end_time)):
            time_list.append(0)
    draw_alive_time(time_list)







if __name__ == '__main__':
    main()