import os

path = os.path.join(os.getcwd(),"hold")
output = os.path.join(path,"out")
num = 11
path_list = os.listdir(path)
path_list = [file for file in path_list if file.lower().endswith(".jpeg")]
path_list.sort(key=lambda x:int(x[4:-5]))
judge_L = True
for filename in path_list:
    tmp = 'L' if judge_L else 'R'
    os.rename(os.path.join(path,filename),os.path.join(output,f'G{num}_{tmp}.JPEG'))
    judge_L = not judge_L
    num = num + 1 if judge_L else num