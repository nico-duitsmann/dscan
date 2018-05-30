import os,sys;f=sys.argv[1];p=sys.argv[2]; # Usage: dscan_min.py <FILE> <PATTERN> | Basic dscan minified | @3v1l_un1c0rn
for x,l in enumerate(open(f,'r+'),1):print("\033[35m%s\033[0m %s:\n%s"%(os.path.abspath(f),x+1,l.replace(p,'\033[1m\033[91m'+p+'\033[0m').replace('\n',''))) if p in l else print("")
