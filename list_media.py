import os,glob
files=sorted(glob.glob('victim_*'))
for f in files:
    print(f, os.path.getsize(f))
