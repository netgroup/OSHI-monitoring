import time
import sys

MYPRINT_DEBUG = 1
MYPRINT_INFO  = 2
MYPRINT_ALERT = 3 

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[0m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def myPrint(style,who,what,new_line=True):
        when = time.strftime("[%H:%M:%S]", time.gmtime())
        who+='        '
        if style == MYPRINT_INFO:
                color = bcolors.OKGREEN
        elif style == MYPRINT_DEBUG:
                color = bcolors.OKBLUE
        elif style == MYPRINT_ALERT:
                color = bcolors.FAIL 
        if new_line:
            print bcolors.HEADER+'['+who[:8]+'] '+bcolors.ENDC+color+what+bcolors.ENDC
        else:
            print bcolors.HEADER+when+'['+who[:8]+'] '+bcolors.ENDC+color+what+bcolors.ENDC+'\r',
            sys.stdout.flush()