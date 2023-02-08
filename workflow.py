#!/usr/bin/env python3

import time
import argparse
import os
import sys
import shutil
from pathlib import Path, PurePath


from biobb_3dshaper import dshaper
from biobb_3dshaper.dshaper import model
from biobb_3dshaper.dshaper import parsesai
from biobb_common.configuration import settings
from biobb_common.tools import file_utils as fu


def prep_output(destination, source):
    #    wdir = PurePath(source).parents[2]
    #if not os.path.isdir(wdir):
    #    os.mkdir(wdir)
    #print (wdir, source, destination)
    #print (str(wdir)+'/'+destination)
    #file = str(source) +"/output_netScore"
    #prova = str(wdir)+'/'+destination
    #print (file)
    #shutil.copy(file, prova)
    #if os.path.isfile(prova):
    #    print ("File copied.")
    #else:
    #    print ("Some error.")
    wdir = PurePath(source).parents[3]
    #if weights dir not created, created it
    weights_dir = os.path.join(wdir, destination)
    if not os.path.isdir(weights_dir):
        #os.mkdir(weights_dir)
        print ('OK')
    #print (wdir, source, destination)
    print (wdir, weights_dir)
    print (source)
    shutil.copytree(source, weights_dir)
    if os.path.isdir(weights_dir):
        print ("File copied.")
    else:
        print ("Some error.")



def main(args):
    start_time= time.time()
    conf = settings.ConfReader(args.config_path)
    print (conf)
    global_log, _ = fu.get_logs(path=conf.get_working_dir_path(), light_format=True)
    global_prop = conf.get_prop_dic(global_log=global_log)
    global_paths = conf.get_paths_dic()
    
    global_log.info("step1_iteration: paths and prop {} ".format(global_prop["step1_iteration"]))
    
    global_log.info("step1_iteration: Running Simulation Model with PyTorch3D")
    parsesai.registration(**global_paths["step1_iteration"], properties=global_prop["step1_iteration"])

    prep_output(args.output_mesh_path, global_paths["step1_iteration"]["output_mesh_path"])
    elapsed_time = time.time() - start_time
    global_log.info('')
    global_log.info('')
    global_log.info('Execution successful: ')
    global_log.info('  Workflow_path: %s' % conf.get_working_dir_path())
    global_log.info('  Config File: %s' % args.config_path)
    if args.system:
        global_log.info('  System: %s' % system)
    global_log.info('')
    global_log.info('Elapsed time: %.1f minutes' % (elapsed_time/60))
    global_log.info('')

    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Based on the official BioBB tutorial")
    parser.add_argument('--config', dest="config_path", required=True)
    parser.add_argument('--system', dest="system", required=False)
    parser.add_argument('--output_mesh_path', dest='output_mesh_path', required=False)
    args = parser.parse_args()
    main(args)
