#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Yunzhao,Luke

import argparse
import time
import threading
#import _thread
import sys
import json
import time
import os
import codecs

import subprocess
import numpy as np

# subprocess.check_call("soxi -d *.wav", shell=True)

def main():
    # ./calc-info.py -h
    parser = argparse.ArgumentParser(description='Command line client for kaldigstserver')
    parser.add_argument('-f', '--file', default="", dest="file", help="audio file")
    parser.add_argument('-o', '--output', default="temp.txt", dest="output", help="Output of calculation")
    parser.add_argument('-d', '--directory', default=".", dest="directory", help="directory to process")
    parser.add_argument('-p', '--parallel', default=4, type=int, dest="parallel", help="parallel of threads")
    args = parser.parse_args()

    def chunks(lst, n):
      #"""Yield successive n-sized chunks from lst."""
      #for i in range(0, len(lst), n):
      #  yield lst[i:i + n]
      n = max(1, n)
      return (lst[i:i+n] for i in range(0, len(lst), n))

    def doCalculate(result, wavfile):
        wavinfo = subprocess.check_output("soxi -d "+wavfile, shell=True)
        arr = wavinfo.strip().decode().split(":")
        farr = np.array(arr).astype(np.float)
        result.append(farr)

    def runThread(result, wfiles):
      for wf in wfiles:
        doCalculate(result, wf)

    result=[]
    if args.file != "":
      doCalculate(result, args.file)
    else:
      tmpfiles = os.listdir(args.directory)
      wvfiles = []
      for tf in tmpfiles:
        if tf.endswith(".wav"):
          wvfiles.append(os.path.join(args.directory, tf))
      wl = len(wvfiles)
      if wl == 0:
        print("No wav files")
        sys.exit()

      #wlist = chunks(wvfiles,args.parallel)
      wlist = np.array_split(wvfiles,args.parallel)

      threads = []
      for ti in range(args.parallel):
        t = threading.Thread(target=runThread, args=(result, wlist[ti]))
        threads.append(t)
      for t in threads:
        t.start()
      for t in threads:
        t.join()

    #print(result)
    final = np.sum(result, axis=0)
    #print("axis=0:",final)
    num_secs = final[0]*3600 + final[1]*60.0 + final[2]
    print("%d hh %d mm %0.2f ss"%(int(num_secs/3600),int((num_secs%3600)/60),num_secs%60.0))
    #print("axis=1:",np.sum(result, axis=1))
    if args.output:
      with codecs.open(args.output, "wb", encoding="utf-8") as fw:
        fw.write("%d hh %d mm %0.2f ss"%(int(num_secs/3600),int((num_secs%3600)/60),num_secs%60.0))
        #fw.write(str(int(num_secs/3600))+"hh"+str(int((num_secs%3600)/60)+"mm"+(num_secs%60)+"ss")

if __name__ == "__main__":
    main()

