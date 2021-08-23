
import re
import pandas as pd
import numpy as np
import flopy
import flopy.utils.binaryfile as bf
import matplotlib.pyplot as plt
import pyemu
import os
import shutil
from shutil import copyfile
import flopy.utils.binaryfile as bf
import warnings
warnings.filterwarnings('ignore')

#Load Model Dir
model_ws = os.path.join(os.path.dirname(os.path.realpath("ModelFiles_2")), "ModelFiles_2")
#os.listdir(model_ws)
m_name = "sa00_U"
#Load Model
#m = flopy.modflow.Modflow.load("sa00_flow.nam",model_ws=model_ws, verbose=True, )
#m


# Read HFB (Horizontal Flow Barrier File) and Write It's Tempelate File #########################################
copyfile(os.path.join(model_ws + os.sep + m_name + ".hfb"), os.path.join(model_ws + os.sep + m_name + ".hfb.tpl"))
HFB_tempelate = open(os.path.join(model_ws + os.sep + m_name + ".hfb.tpl"), 'r')

HYDCHR = []
Unique_HYDCHR = []
HYDCHR_PARAM = []

for line in HFB_tempelate:
    columns = line.split()
    if len(columns) == 1:
        continue
    HYDCHR.append(columns[4])

for KH in HYDCHR:
    if KH not in Unique_HYDCHR:
        Unique_HYDCHR.append(KH)
HFB_tempelate.close()

KHPARAMS_Name = ['#KHFBONE', '#KHFBTWO', '#KHFBTHREE']
KHPARAMS_dict = dict(zip(Unique_HYDCHR, KHPARAMS_Name))

float(list(KHPARAMS_dict.keys())[0])

with open(HFB_tempelate.name, 'r+') as f:
    tpl = f.read()
    for i in range(len(KHPARAMS_dict)):
        tpl = re.sub(list(KHPARAMS_dict.keys())[i], list(KHPARAMS_dict.values())[i], tpl)
    f.seek(0)
    f.write(tpl)
    f.truncate()

src=open(HFB_tempelate.name,"r")
fline="pft #\n"    #Prepending string
oline=src.readlines()
oline.insert(0,fline)
src.close()
#We again open the file in WRITE mode
src=open(HFB_tempelate.name,"w")
src.writelines(oline)
src.close()

# Read in BCF File ############################################################################################
bcf = open(os.path.join(model_ws + os.sep + m_name + ".bcf"), "r")
lines = bcf.readlines()
bcf.close()

line_num = 0
layer_index = []
param_index = []
for line in lines:
    if "1.00000(10e20.12)" in line:
        param_index.append(line_num)
    if "01.0000e-01(10e20.12)" in line:
        layer_index.append(line_num)
    line_num += 1

matrix_index = []

for p in param_index:
    for k in range(279):
        matrix_index.append(p + (23 * k) + 1)

ParamsforLayer = [[] for _ in range(12)]

# for i in range(11):
#     ParamsforLayer[i].append(lines[layer_index[i]:layer_index[i + 1]])

paramsonLayers

Param_Layers = {}

param1_layer1 = lines[param_index[0]:param_index[1]]
param1_layer2 = lines[param_index[1]+1 : param_index[2]]
for i np.arange(param_inde

for i in range()







# bcf = open(os.path.join(model_ws + os.sep + m_name + ".bcf"), 'r')
#
# bcf_dict = []
#
# for line in bcf:
#     columns = line.split()
#     if not len(columns) in [9, 10]:
#         continue
#     if len(columns) == 10:
#         bcf_dict.append(columns)
#     else:
#         columns = list(np.append(columns, np.repeat(np.nan, 1)))
#         bcf_dict.append(columns)
#
#
# for i in np.arange(0, len(bcf_dict[51:])/23):


# Read the btn file ##########################################################################################
btn_template = open(os.path.join(model_ws + os.sep + m_name + ".btn.tpl"), 'r')

btn_dict = []

for line in btn_template:
    columns = line.split()
    if not len(columns) in [9, 10]:
        continue
    if len(columns) == 10:
        btn_dict.append(columns)
    else:
        columns = list(np.append(columns, np.repeat(np.nan, 1)))
        btn_dict.append(columns)
btn_dict = btn_dict[2:]

btn_dict_merged = []
for i in btn_dict:
    btn_dict_merged +=i


btn_Rows = {}
k=0
for i in np.arange(0, len(btn_dict_merged)):
    btn_Rows[i] = btn_dict_merged[k:k+230]
    k +=230

# Read TSF Rate&Conc from .wel file ##################################################################################
wel = open(os.path.join(model_ws + os.sep + m_name + ".wel"), 'r')
lines = wel.readlines()
wel.close()

new_lines = lines
count = 0
for line in lines:
    if len(line.split()) > 3:
        if line.split()[0] == '10':
            new_line = "".join([line.split()[0].rjust(10), line.split()[1].rjust(10), line.split()[2].rjust(10),
                                 '#TSFQRate'.rjust(10), '#Ur_Conc'.rjust(10)])
            new_lines[count] = new_line
    count += 1

with open(os.path.join(model_ws + os.sep + m_name + ".wel.tpl"), 'w') as f:
    for item in new_lines:
        if '\n' in item:
            f.write("%s" % item)
        else:
            f.write("%s\n" % item)
    f.close()

#y = x[0:29] + ' #WellQRate' + x[40:] Split by Character


# Read Pumping Rates from .wl5 file ##################################################################################
wl5 = open(os.path.join(model_ws + os.sep + m_name + ".wl5"), 'r')
lines = wl5.readlines()
wl5.close()

new_lines = lines
count = 0
for line in lines:
    if len(line.split()) == 6:
        new_line = " ".join([line.split()[0].rjust(10), line.split()[1].rjust(10), line.split()[2].rjust(10),
                            line.split()[3].rjust(10), '#WlPumpRate'.rjust(10), line.split()[5].rjust(10)])
        new_lines[count] = new_line
    count += 1


with open(os.path.join(model_ws + os.sep + m_name + ".wel.tpl"), 'w') as f:
    for item in new_lines:
        if '\n' in item:
            f.write("%s" % item)
        else:
            f.write("%s\n" % item)
    f.close()


# Read Recharge files ##############################################################################################
copyfile(os.path.join(m.model_ws + os.sep + m.name + ".rch"), os.path.join(m.model_ws + os.sep + m.name + ".rch.tpl"))
rch_template = open(os.path.join(m.model_ws + os.sep + m.name + ".rch.tpl"), 'r')