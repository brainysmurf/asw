import appscript
import os

path1 = "/Users/brainysmurf/Documents/"
path2 = "/Users/brainysmurf/Documents/About Stacks.pdf"
print(path1.split(os.sep))
print(path2.split(os.sep))
for which in [path1, path2]:
    ref = appscript.app("Finder").startup_disk
    path_divided = path.split(os.sep)
    for i in range(len(path_divided)):
        item = path_divided[i]
        if item:
            if i == len(path_divided)-1:
                ref = ref.document_files[item]
            else:
                ref = ref.folders[item]
