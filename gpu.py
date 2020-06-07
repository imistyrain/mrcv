#coding=utf-8
import os
import sys
import re
import pwd
import time
import psutil
import subprocess
import operator
import argparse

def is_cuda_avaiable():
    try:
        n = str(subprocess.check_output(["nvidia-smi", "-L"])).count('UUID')
    except Exception as e:
        n = 0
    return n

def clear():
    #print("\033[H\033[J")()
    sys.stdout.write("\x1b[2J\x1b[H")

def get_owner(pid):
    try:
        for line in open('/proc/%d/status' % pid):
            if line.startswith('Uid:'):
                uid = int(line.split()[1])
                return pwd.getpwuid(uid).pw_name
    except:
        return None

def get_cmd(pid):
    process=psutil.Process(int(pid))
    cmd=process.cwd()
    for e in process.cmdline():
        cmd+=" "+e
    return cmd

def is_train(name):
    trains=["python","caffe","python3"]
    for train in trains:
        if name.find(train) >= 0:
            return True
    return False

def get_info(verbose=True):
    gpus=[]
    msg = subprocess.Popen('nvidia-smi', stdout = subprocess.PIPE).stdout.read().decode()
    msg = msg.strip().split('\n')
    lino = 8
    while True:
        status = re.findall('.*\d+C.*\d+W / +\d+W.* +(\d+)MiB / +(\d+)MiB.* +(\d+%).*', msg[lino])
        if status == []: break
        mem_usage, mem_total, usage = status[0]
        gpus.append(mem_usage+"M/"+mem_total+"M\t"+usage)
        lino += 3
    lino = -1
    maps={}
    while True:
        lino -= 1
        status = re.findall('\| +(\d+) +(\d+) +\w+ +([^ ]*) +(\d+)MiB \|', msg[lino])
        if status == []:
            break
        gpuid, pid, _, mem_usage = status[0]
        if pid in maps.keys():
            maps[pid]=str(gpuid)+","+maps[pid]
        else:
            maps[pid]=str(gpuid)+"\t"+pid+"\t"+mem_usage+"M"
    maps=sorted(maps.items(),key=operator.itemgetter(1),reverse=True)
    lines=[]
    for pid in maps:
        try:
            cmd = get_cmd(pid[0])
            if(is_train(cmd)):
                line=pid[1]+"\t"+cmd
                lines.append((line))
        except Exception as e:
            #print(e)
            e
    lines.reverse()
    line=""
    for i,g in enumerate(gpus):
        line+=str(i)+":"+g+"    \t"
        if i % 4 == 3:
            line+="\n"
    if verbose:
        print(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()))
        print(line[:-1])
        print("gpu\tpid\tmemusage\tdir\tcmd")
    runs=[]
    for line in lines:
        runs.append(line)
        if verbose:
            print(line)
    return runs

def gtop():
    while True:
        runs=get_info(False)
        clear()
        print(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()))
        for run in runs:
            print(run)

def write2log(line,path="gpu.log"):
    with open(path,"a+") as f:
        f.write(line+"\n")

def gm():
    allruns={}
    while True:
        runs=get_info(False)
        if len(allruns)==0:
            for run in runs:
                rp=run.split(" ")[1]
                allruns[rp]=run
        else:
            rps=[]
            for run in runs:
                rp=run.split(" ")[1]
                rps.append(rp)
            
            for r in list(allruns.keys()):
                if r not in rps:
                    run=allruns[r]
                    line=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())+" "+run+" closed"
                    print(line)
                    write2log(line)
                    del allruns[r]
            
            for i in range(len(rps)):
                run=runs[i]
                if not allruns.has_key(rps[i]):
                    line=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())+" "+run+" created"
                    print(line)
                    write2log(line)
                    allruns[rps[i]]=runs[i]

def get_args():
    args=argparse.ArgumentParser()
    args.add_argument("-m", "--gm", default=False,help="monitor")
    args.add_argument("-t", "--gtop", default=False,help="monitor")
    args.add_argument("-g", "--info", default=True,help="monitor")
    return args.parse_args()

if __name__ == "__main__":
    args=get_args()
    if not is_cuda_avaiable():
        print("There seems no gpu available.")
        exit(0)
    if args.gm:
        gm()
    elif args.gtop:
        gtop()
    else:
        get_info()