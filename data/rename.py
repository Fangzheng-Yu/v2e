import glob
import os


list = glob.glob("./*.png")
print(list)

idx = 0
for name in list:
    print(name)
    os.rename(name,"./%08d.png"%(idx))
    idx+=1