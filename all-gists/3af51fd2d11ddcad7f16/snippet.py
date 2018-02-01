import subprocess
from lib.common.dominoUtil import running_on_local
from lib.config import PROJECT_PATH
import time
import psutil
import os
import numpy as np

def _recommended_threads():
    return psutil.cpu_count()-2

def _recommended_memory():
    return psutil.virtual_memory().available/(2*1024*1024)

def _numbers_in_file(fn):
    f = open( fn )
    return [ int(x) for x in f.readlines() ]


def stockfish( fen, seconds=1, threads=None, memory=None ):
    """ Return the evaluation for a position """
    return stockfish_scores( fen=fen, seconds=seconds, threads=threads, memory=memory)[-1]

def is_positional( scores ):
    """ True if the position is positional in nature """
    score_diff      = [ abs(sd) for sd in np.diff( scores ) ]
    return max( score_diff ) < 25

def stockfish_scores(fen, seconds=1, threads=None, memory=None, all_scores=False):
    """ Call stockfish engine and return vector of evaluation score """

    # Defaults
    memory = memory or _recommended_memory()
    threads = threads or _recommended_threads()
    binary = 'mac' if running_on_local() else 'linux'

    # Shell out to Stockfish
    subprocess.call(["chmod", "+x", "stockfish.sh"])
    subprocess.call(["chmod", "+x", "stockfish_"+binary])
    cmd =  ' '.join( ['./stockfish.sh' ,fen, str(seconds) , binary, str(threads), str(memory) ] )
    print cmd
    subprocess.call( cmd, shell=True )

    # Read from score.txt
    time.sleep( 1 )
    try:
        scores_file = os.path.join( PROJECT_PATH,'roardata_stockfish','scores.txt')
        return _numbers_in_file(scores_file)
    except:
        analysis_file = scores_file.replace('score.txt','analysis.txt')
        print "stockfish engine had trouble reading " + scores_file + ", probably because the analysis file did not contain the evaluation string as expected"
        print "Here is the analysis file " + analysis_file
        with open( analysis_file, 'r') as fin:
            print fin.read()


