#!/usr/bin/env python3

import sys
import pandas as pd


if __name__ == "__main__":
    file_name = sys.argv[1]
    error_ratio_list = [float(i) for i in sys.argv[2:]]
    file_error = pd.read_csv(file_name)

    for error_ratio in error_ratio_list:
        error_count = (file_error['error'].abs() / file_error['actual']<= error_ratio).sum()
        print('Max Rel. Error: ' + str(error_ratio) + '\t-> Error Ratio:\t'  + str(1 - error_count / float(file_error.shape[0])))