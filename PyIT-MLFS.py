from sklearn.preprocessing import KBinsDiscretizer
import numpy as np
from classes.lrfs import lrfs as LRFS
from classes.igmf import igmf as IGMF
from classes.pmu import pmu as PMU
from classes.d2f import d2f as D2F
from classes.scls import scls as SCLS
from classes.mdmr import mdmr as MDMR
from classes.lsmfs  import  lsmfs as LSMFS
from classes.mlsmfs import mlsmfs as MLSMFS
from classes.ppt_mi import ppt_mi as PPT_MI
from classes.MMRMI import MMRMI as  MMRMI
import argparse
from tqdm import tqdm
import os
import time
from evaluation import classify
from data import read_data





if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-path', type=str, required=False)
    parser.add_argument('--datasets', type=str, nargs='+', required=True)
    parser.add_argument('--fs-methods', type=str, nargs='+', required=True)
    parser.add_argument('--output-path', type=str, required='False', default='results')
    parser.add_argument('--selection-type', type=str, required=False, default='rank')
    parser.add_argument('--num-of-features', type=int, required=False, default=50)
    parser.add_argument('--eval-mode', type=str, default='pre_eval')
    parser.add_argument('--classifiers', type=str, nargs='+', required=False, default=None)
    parser.add_argument('--metrics', type=str, nargs='+', required=False, default='hamming loss')

    args = parser.parse_args() 
    
    if args.selection_type not in ['rank', 'fixed_num']: 
        raise ValueError('The selecion_method should be in [rank, fixed_num]') 

    method_dispatcher = {'LRFS':LRFS, 'PPT_MI':PPT_MI,\
         'IGMF':IGMF, 'PMU':PMU, 'D2F':D2F, 'SCLS':SCLS,\
              'MDMR':MDMR, 'LSMFS':LSMFS, 'MLSMFS':MLSMFS,\
                  'MMRMI': MMRMI }

    for d in args.datasets: 
        X_train, y_train, X_test, y_test = read_data(d_name= d, d_path= args.data_path)
        est = KBinsDiscretizer(n_bins=3, encode='ordinal', strategy='uniform')
        est.fit(X_train)
        X_train = est.transform(X_train).astype(int)
        X_test = est.transform(X_test).astype(int)
        y_train = y_train.astype(int) 

        

            
        for method in args.fs_methods: 
            start = time.time()
            message = 30*'='+'  dataset:{}  method:{}'.format(d,method)+30*'='
            print(message)          
            fs = method_dispatcher[method]()
            if args.selection_type == 'rank':            
                rank = fs.rank(X_train, y_train, mode=args.eval_mode)
            elif args.selection_type == 'fixed_num':
                rank = fs.select(X_train, y_train,args.num_of_features, mode=args.eval_mode)
            end = time.time()
            
            
            # writing the selected subsets into file
            dir_name = args.output_path + r'\SelectedSubsets' 
            if not (os.path.isdir(dir_name)):
                os.mkdir(dir_name) 
            dir_name += r'\{}'.format(d)
            if not (os.path.isdir(dir_name)):
                os.mkdir(dir_name)
            filename = dir_name + r'\\' + method + '.csv'
            np.savetxt(filename, rank, delimiter=',', fmt = '%d')

            # writing the running time into file
            dir_name = args.output_path + r'\RunningTimes' 
            if not (os.path.isdir(dir_name)):
                os.mkdir(dir_name)
            dir_name += r'\{}'.format(d)
            if not (os.path.isdir(dir_name)):
                os.mkdir(dir_name) 
            filename = dir_name + r'\\' + method +  '.txt'
            np.savetxt(filename, [end-start], fmt = '%d')

            if args.classifiers != None:
                 

                for c in args.classifiers:
                    dir_name = args.output_path + '\\' + "Accuracies" 
                    if not (os.path.isdir(dir_name)):
                        os.mkdir(dir_name)
                    dir_name += r'\{}'.format(d) 
                    if not (os.path.isdir(dir_name)):
                        os.mkdir(dir_name) 
                    dir_name += r'\{}'.format(c)
                    if not (os.path.isdir(dir_name)):
                        os.mkdir(dir_name) 
                    with tqdm(total=len(rank), ncols=80) as t:
                        t.set_description('{} Classification in Progress '.format(c))
                        for k in range(1, len(rank)+1):
                            res = classify(X_train[:,rank[:k]], y_train, X_test[:,rank[:k]], y_test, c, args.metrics)
                            
                            for m in args.metrics: 
                                dir_name_m = dir_name +r'\{}'.format(m)
                                if not (os.path.isdir(dir_name_m)):
                                    os.mkdir(dir_name_m) 
                                filename = dir_name_m +  "\\" +  method +  '.csv'
                                if k == 1:
                                    np.savetxt(filename, [res[m]])
                                else: 
                                    with open(filename, "ab") as f:
                                        np.savetxt(f, [res[m]])


                            t.update(1)

                    

                 





            