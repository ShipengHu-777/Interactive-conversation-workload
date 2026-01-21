import os
import matplotlib.pyplot as plt
import numpy as np


def draw_round_num(round_numbers):
    round_numbers = np.sort(round_numbers)
    print("avg round num is ",np.mean(round_numbers))
    print("median round num is ",round_numbers[int(len(round_numbers)*0.5)])
    print("P90 round num is ",round_numbers[int(len(round_numbers)*0.9)])
    cdf = np.arange(1, len(round_numbers)+1) / len(round_numbers)
    plt.figure(figsize=(8, 3.5))


    plt.plot(round_numbers, cdf, marker='o', color='seagreen',linewidth=5, markersize=6)
    plt.xlabel('round num',fontsize=24)
    plt.ylabel('CDF',fontsize=24)
    plt.yticks(fontsize=22)
    plt.xticks(fontsize=22)
    plt.xlim(0,100)
    plt.ylim(bottom=0)
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def main():
    round_numbers=[]
    for i in range(7):
        print("i=",i)
        trace_file="total_traces_part"+str(i+1)+".txt"
        f=open(trace_file,"r")
        list_lines=f.readlines()
        f.close()
        list_lines=list_lines[1:]
        user_end_round={}
        for line in list_lines:
            split_list=line.split()
            user_end_round[split_list[0]]=int(split_list[-1])+1
        for key,val in user_end_round.items():
            round_numbers.append(val)
    draw_round_num(round_numbers)







if __name__ == '__main__':
    main()