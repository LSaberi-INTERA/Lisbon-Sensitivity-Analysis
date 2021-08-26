
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
model_ws = os.path.join(os.path.dirname(os.path.realpath("flow")), "Lisbon-Sensitivity-Analysis", "flow")
model_ws_U = os.path.join(os.path.dirname(os.path.realpath("uranium")), "Lisbon-Sensitivity-Analysis", "uranium")
#os.listdir(model_ws)
m_name_U = "sa00_U"

# Read HFB (Horizontal Flow Barrier File) and Write It's Tempelate File #########################################
hfb = open(os.path.join(model_ws + os.sep + m_name + ".hfb"), 'r')

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

#Read in BCF File ############################################################################################
bcf = open(os.path.join(model_ws + os.sep + "sa00_flow.bcf"), "r")
lines = bcf.readlines()
bcf.close()

Zones = open(os.path.join(model_ws + os.sep + "Kzone_matrix.dat"), "r")
linesinZones = Zones.readlines()
Zones.close()

y=[]
for linez in linesinZones:
    lz = linez.split()
    # print(linez)
    for k in lz:
        y.append(k)

line_num = 0
Primary_Storage_index = []
Secondary_Storage_index = []
param_index = []
for line in lines:
    if "1.00000(10e20.12)" in line:
        param_index.append(line_num)
     if "01.0000e-01(10e20.12)" in line or "01.0000e-06(10e12.4)" in line:
         Primary_Storage_index.append(line_num)
    line_num += 1


# matrix_index = []
# for p in param_index:
#     for k in range(279):
#         matrix_index.append(p + (23 * k) + 1)


# Params_Layers = {}
# for i in np.arange(len(param_index)):
#     if i != 59:
#         Params_Layers[i] = lines[param_index[i]+1 : param_index[i+1]]
#     else:
#         Params_Layers[i] = lines[param_index[i]+1: param_index[i]+6418]

def chunkIt(seq, num):
    avg = len(seq) / float(num)
    out = []
    last = 0.0

    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg
    return out

layers_y = chunkIt(y, 12)

zones = ['1', '2', '3', '4', '6', '8', '10', '12', '15', '16', '18', '20', '22', '23']

# Param1_lay1 = []
# for i in range(len(Params_Layers)):
#     for k in m.split():
#         Param1_lay1.append(k)






###########################################################################################

# f = open(os.path.join(model_ws + os.sep + "sa00_flow.bcf"), "r")
# lines = f.readlines()
# f.close()
#
# kz = open(os.path.join(model_ws + os.sep + "Kzone_matrix.dat"), "r")
# linesinZones = kz.readlines()
# kz.close()

# f = open(os.path.join(model_ws + os.sep + "sa00_flow.bcf"), "r")
# lines = f.readlines()
# f.close()

# z = open(os.path.join(model_ws + os.sep + "Kzone_matrix.dat"), "r")
# kz = z.readlines()
# z.close()

f = open(os.path.join(model_ws + os.sep + "sa00_flow.bcf"), "r")
lines = f.readlines()
f.close()

z = open(os.path.join(model_ws + os.sep + "Kzone_matrix.dat"), "r")
kz = z.readlines()
z.close()

param_separator = "1.00000(10e20.12)"
layer_separator = "01.0000e-01(10e20.12)"

y = []
for linez in kz:
    lz = linez.split()
    # print(linez)
    for k in lz:
        y.append(k)


def chunkIt(seq, num):
    avg = len(seq) / float(num)
    out = []
    last = 0.0

    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg
    return out


layers_y = chunkIt(y, 12)

layers = [[] for _ in range(12)]
layer_num = 0
for i, line in enumerate(lines):
    if i > 2:
        if layer_separator in line:
            layer_num = layer_num + 1
        if layer_num < 12:
            layers[layer_num].append(i)

# To access: blocks[layer][parameter][relative_line]=file line number
blocks = [[[] for _ in range(5)] for _ in range(12)]
param_num = 0
for i, layer_num in enumerate(layers):
    for line_num in layer_num:
        if param_separator in lines[line_num]:
            param_num = (param_num + 1) % 5
        blocks[i][param_num].append(line_num)
    # print(i,param_num,line_num)

matrix = [[[[] for _ in range(279)] for _ in range(5)] for _ in range(12)]
for i, layer_num in enumerate(blocks):
    # pdb.set_trace()
    for j, param_num in enumerate(layer_num):
        matrix_num = -1
        for line_num in param_num:
            if len(lines[line_num - 1].split()) == 9 and len(lines[line_num].split()) == 10:
                matrix_num = matrix_num + 1

            if len(lines[line_num - 1].split()) in [2, 3] and len(lines[line_num].split()) == 10:
                matrix_num = matrix_num + 1

            # print(i,j,matrix_num,lines[line_num])
            if not (param_separator in lines[line_num] or layer_separator in lines[line_num]):
                matrix[i][j][matrix_num].append(line_num)

# new_y = y[0]*5 + y[1]*5 + y[2]*5 + y[3]*5 + y[4]*5 + y[5]*5 + y[6]*5 + y[7]*5 + y[8]*5 + y[9]*5 + y[10]*5 + y[11]*5

z = lines.copy()
zones = ['1', '2', '3', '4', '6', '8', '10', '12', '15', '16', '18', '20', '22', '23']
touched_lines = {}
for ly, layer in enumerate(matrix):
    for p, param in enumerate(layer):
        i = 0
        for c, cell in enumerate(param):
            for f, file_line in enumerate(cell):
                update_values = []
                update_indexes = []
                for e, element in enumerate(lines[file_line].split()):

                    # compare
                    yelement = layers_y[ly][i]
                    if yelement in zones:
                        update_indexes.append(e)
                        update_values.append(yelement)
                        temp = lines[file_line].split()
                        for u, update in enumerate(update_indexes):
                            if p == 2:
                                temp[update] = f"#KH_Z{update_values[u]}_L{ly}"
                            if p == 3:
                                temp[update] = f"#KV_Z{update_values[u]}_L{ly}"
                    final = ''
                    for col in temp:
                        if file_line in range(4, 57):
                            final = final + col.rjust(12)
                        else:
                            final = final + col.rjust(20)

                    z[file_line] = final
                    touched_lines[file_line] = True
                    # print(i,file_line)
                    i = i + 1

# print(i)
# open output file
outfile = open(os.path.join(model_ws + os.sep + "sa00_flow.bcf.tpl"), 'w')

for l, line in enumerate(z):
    if l in touched_lines:
        outfile.write(line + '\n')
    else:
        outfile.write(line)

# close file
outfile.close()







# y=[]
# for linez in linesinZones:
#     lz = linez.split()
#     # print(linez)
#     for k in lz:
#         y.append(k)
#
# param_separator = "1.00000(10e20.12)"
# layer_separator = "01.0000e-01(10e20.12)"
#
# zones = ['1', '2', '3', '4', '6', '8', '10', '12', '15', '16', '18', '20', '22', '23']
#
# layers = [[] for _ in range(12)]
# layer_num = 0
# for i, line in enumerate(lines):
#     if i > 2:
#         if layer_separator in line:
#             layer_num = layer_num + 1
#         if layer_num < 12:
#             layers[layer_num].append(i)
#
# # To access: blocks[layer][parameter][relative_line]=file line number
# blocks = [[[] for _ in range(5)] for _ in range(12)]
# param_num = 0
# for i, layer_num in enumerate(layers):
#     for line_num in layer_num:
#         if param_separator in lines[line_num]:
#             param_num = (param_num + 1) % 5
#         blocks[i][param_num].append(line_num)
#     # print(i,param_num,line_num)
#
# matrix = [[[[] for _ in range(279)] for _ in range(5)] for _ in range(12)]
# for i, layer_num in enumerate(blocks):
#     # pdb.set_trace()
#     for j, param_num in enumerate(layer_num):
#         matrix_num = -1
#         for line_num in param_num:
#             if len(lines[line_num - 1].split()) == 9 and len(lines[line_num].split()) == 10:
#                 matrix_num = matrix_num + 1
#
#             if len(lines[line_num - 1].split()) in [2, 3] and len(lines[line_num].split()) == 10:
#                 matrix_num = matrix_num + 1
#
#             # print(i,j,matrix_num,lines[line_num])
#             if not (param_separator in lines[line_num] or layer_separator in lines[line_num]):
#                 matrix[i][j][matrix_num].append(line_num)
#
# for i in range(len(layers_y)):
#     layers_y[i] = layers_y[i]*5
#
# update_indexes = []
# update_values = []
# out = matrix.copy()
# for ly, layer in enumerate(matrix):
#     for p, param in enumerate(layer):
#         for ln, line in enumerate(param):
#             for e, element in enumerate(line):
#                 yelement = layers_y[ly][e]
#
#                 if yelement in zones:
#                     update_indexes.append(e)
#                     update_values.append(yelement)
#                 temp = line.split()
#                 for u, update in enumerate(update_indexes):
#                     temp[update] = f"#Q_Rech{update_values[u]}#"
#                 out[i][j] = ' '.join(temp)













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
#For Flow Model

#Reading Input
wel = open(os.path.join(model_ws + os.sep + m_name + ".wel"), 'r')
lines = wel.readlines()
wel.close()

LTI = pd.read_csv(os.path.join(model_ws + os.sep + "LTI_forImport_mod_SA_flow.csv"), header=0)
LTI_row = [str(x) for x in LTI.row.to_list()]
LTI_col = [str(x) for x in LTI.co.to_list()]
LTI_lay = [str(x) for x in LTI.layer.to_list()]
UTI = pd.read_csv(os.path.join(model_ws + os.sep + "UTI_forImport_mod_SA_flow.csv"), header=0)
UTI_row = [str(x) for x in UTI.row.to_list()]
UTI_col = [str(x) for x in UTI.co.to_list()]
UTI_lay = [str(x) for x in UTI.layer.to_list()]
OUT = ['0.000e+00', '0.7370000']
IN = ['3.7750001']

new_lines = lines.copy()
count = 0
for line in new_lines[1:]:
    if len(line.split()) == 1:
        new_lines[count] = line
    if len(line.split()) == 3:
        new_line = "".join([line.split()[0].rjust(10), line.split()[1].rjust(10), line.split()[2].split('-')[0].rjust(10),
                    line.split()[2].split('-')[1].replace(line.split()[2].split('-')[1], ' #Q_RWELL#').rjust(10)])
        new_lines[count] = new_line
    if len(line.split()) == 4 and line.split()[0] == '10':
        # print(line)
        if line.split()[1] in LTI_row and line.split()[2] in LTI_col and line.split()[3] in OUT:
            new_line = "".join([line.split()[0].rjust(10), line.split()[1].rjust(10), line.split()[2].rjust(10),
                                ' #Q_LTI_OUT#'.rjust(10)])
            new_lines[count] = new_line
        if line.split()[1] in LTI_row and line.split()[2] in LTI_col and line.split()[3] in IN:
            new_line = "".join([line.split()[0].rjust(10), line.split()[1].rjust(10), line.split()[2].rjust(10),
                                ' #Q_LTI_IN#'.rjust(10)])
            new_lines[count] = new_line
        if line.split()[1] in UTI_row and line.split()[2] in UTI_col and line.split()[3] in OUT:
            new_line = "".join([line.split()[0].rjust(10), line.split()[1].rjust(10), line.split()[2].rjust(10),
                                ' #Q_UTI_OUT#'.rjust(10)])
            new_lines[count] = new_line
        if line.split()[1] in UTI_row and line.split()[2] in UTI_col and line.split()[3] in IN:
            new_line = "".join([line.split()[0].rjust(10), line.split()[1].rjust(10), line.split()[2].rjust(10),
                                    ' #Q_UTI_IN#'.rjust(10)])
            new_lines[count] = new_line
            # new_line = "".join([line.split()[0].rjust(10), line.split()[1].rjust(10), line.split()[2].rjust(10), '#Q_LTI_OUT'.rjust(10)])
            # new_lines[count] = new_line
    count += 1

with open(os.path.join(model_ws + os.sep + m_name + ".wel.tpl"), 'w') as f:
    f.write("pft #\n")
    f.write('       296        50         0\n')
    for item in new_lines:
        if '\n' in item:
            f.write("%s" % item)
        else:
            f.write("%s\n" % item)
    f.close()

#For Uranium Model
wel_U = open(os.path.join(model_ws_U + os.sep + m_name_U + ".wel"), 'r')
lines = wel_U.readlines()
wel_U.close()

new_lines = lines.copy()
count = 0
for line in new_lines[1:]:
    if len(line.split()) == 1:
        new_lines[count] = line
    if len(line.split()) == 4:
        new_line = "".join([line.split()[0].rjust(10), line.split()[1].rjust(10), line.split()[2].split('-')[0].rjust(10),
                    line.split()[2].split('-')[1].replace(line.split()[2].split('-')[1], '#Q_RWELL#').rjust(10),
                            line.split()[3].rjust(10)])
        new_lines[count] = new_line
    if len(line.split()) == 5 and line.split()[0] == '10':
        # print(line)
        if line.split()[1] in LTI_row and line.split()[2] in LTI_col and line.split()[3] in OUT:
            new_line = "".join([line.split()[0].rjust(10), line.split()[1].rjust(10), line.split()[2].rjust(10),
                                ' #Q_LTI_OUT#'.rjust(10), ' #C_U_LTI#'.rjust(10)])
            new_lines[count] = new_line
        if line.split()[1] in LTI_row and line.split()[2] in LTI_col and line.split()[3] in IN:
            new_line = "".join([line.split()[0].rjust(10), line.split()[1].rjust(10), line.split()[2].rjust(10),
                                ' #Q_LTI_IN#'.rjust(10), ' #C_U_LTI#'.rjust(10)])
            new_lines[count] = new_line
        if line.split()[1] in UTI_row and line.split()[2] in UTI_col and line.split()[3] in OUT:
            new_line = "".join([line.split()[0].rjust(10), line.split()[1].rjust(10), line.split()[2].rjust(10),
                                ' #Q_UTI_OUT#'.rjust(10), ' #C_U_UTI#'.rjust(10)])
            new_lines[count] = new_line
        if line.split()[1] in UTI_row and line.split()[2] in UTI_col and line.split()[3] in IN:
            new_line = "".join([line.split()[0].rjust(10), line.split()[1].rjust(10), line.split()[2].rjust(10),
                                    ' #Q_UTI_IN#'.rjust(10), ' #C_U_UTI#'.rjust(10)])
            new_lines[count] = new_line
            # new_line = "".join([line.split()[0].rjust(10), line.split()[1].rjust(10), line.split()[2].rjust(10), '#Q_LTI_OUT'.rjust(10)])
            # new_lines[count] = new_line
    count += 1









# new_lines = lines.copy()
# count = 0
# for line in new_lines[1:]:
#     if len(line.split()) != 5:
#         new_lines[count] = line
#     if len(line.split()) == 5 and line.split()[1] in LTI_row and line.split()[2] in LTI_col:
#         new_line = "".join([line.split()[0].rjust(10), line.split()[1].rjust(10), line.split()[2].rjust(10),
#                             line.split()[3].rjust(10),'#C_U_LTI'.rjust(10)])
#         new_lines[count] = new_line
#     if len(line.split()) == 5 and line.split()[1] in UTI_row and line.split()[2] in UTI_col:
#         new_line = "".join([line.split()[0].rjust(10), line.split()[1].rjust(10), line.split()[2].rjust(10),
#                                 line.split()[3].rjust(10), '#C_U_UTI'.rjust(10)])
#         new_lines[count] = new_line
#     count += 1

with open(os.path.join(model_ws_U + os.sep + m_name_U + ".wel.tpl"), 'w') as f:
    f.write("pft #\n")
    f.write('       296        50         0\n')
    for item in new_lines:
        if '\n' in item:
            f.write("%s" % item)
        else:
            f.write("%s\n" % item)
    f.close()

# Read Pumping Rates from .wl5 file ##################################################################################
# For Uranium Model
def wl5_tpl():
    wl5 = open(os.path.join(model_ws_U + os.sep + m_name_U + ".wl5"), 'r')
    lines = wl5.readlines()
    wl5.close()

    new_lines = lines
    count = 0
    for line in lines:
        if len(line.split()) == 6:
            new_line = " ".join([line.split()[0].rjust(10), line.split()[1].rjust(10), line.split()[2].rjust(10),
                                line.split()[3].rjust(10), '#Q_CAP_{}#'.format(line.split()[0]).rjust(10),
                                 line.split()[5].rjust(10)])
            new_lines[count] = new_line
        count += 1


    with open(os.path.join(model_ws_U + os.sep + m_name_U + ".wl5.tpl"), 'w') as f:
        for item in new_lines:
            if '\n' in item:
                f.write("%s" % item)
            else:
                f.write("%s\n" % item)
        f.close()

# For Flow Model
def wl5_tpl():
    wl5 = open(os.path.join(model_ws + os.sep + m_name + ".wl5"), 'r')
    lines = wl5.readlines()
    wl5.close()

    new_lines = lines
    count = 0
    for line in lines:
        if len(line.split()) == 5:
            new_line = " ".join([line.split()[0].rjust(10), line.split()[1].rjust(10), line.split()[2].rjust(10),
                                line.split()[3].rjust(10), '#Q_CAP_{}#'.format(line.split()[0]).rjust(10)])
            new_lines[count] = new_line
        count += 1


    with open(os.path.join(model_ws + os.sep + m_name + ".wl5.tpl"), 'w') as f:
        for item in new_lines:
            if '\n' in item:
                f.write("%s" % item)
            else:
                f.write("%s\n" % item)
        f.close()

# Read Recharge files ##############################################################################################
rch = open(os.path.join(model_ws + os.sep + "sa00_flow.rch"), 'r')
lines = rch.readlines()
rch.close()

rch_zones = open(os.path.join(model_ws + os.sep + "Rzone_matrix.dat"), 'r')
lines_RCHzones = rch_zones.readlines()
rch_zones.close()

new_lines = lines[3:].copy()
matrix = 0
x = [[] for _ in range(8928)]
for i, line in enumerate(new_lines):
    # print(i, line, matrix)
    if (len(new_lines[i-1].split()) == 9) and (i > 0):
        matrix = matrix + 1
    # if matrix < 8928:
    if len(line.split()) >= 9:
        x[matrix].append(line)

Zones = ['1', '2', '3', '6', '7']
update_indexes = []
update_values = []
y = lines_RCHzones*32
out = x.copy()
for i, m in enumerate(x):
    for j, line in enumerate(m):
        #print("Matrix",i," Line",j)
        update_indexes=[]
        update_values=[]
        for k, xelement in enumerate(line.split()):

            yelement = y[i].split()[10 * j + k ]
            #print("Element index",k,"Element",yelement)
            #if yelement=='2': #enter maping comparison logic here
            #if yelement == '2' or yelement == '1' or yelement == '3' or yelement == '6' or yelement == '7':
            if yelement in Zones:
                update_indexes.append(k)
                update_values.append(yelement)
        temp = line.split()
        for u,update in enumerate(update_indexes):
            temp[update]=f"#Q_Rech{update_values[u]}#"
        out[i][j]=' '.join(temp)
        #print(yelement)
        #if line.split()[k] ==

# open output file
outfile = open(os.path.join(model_ws + os.sep + "sa00_flow.rch.tpl"), 'w')
z=[]
final=''
z.append('         1        50         0         0\n')
outfile.write('         1        50         0         0\n')
z.append('         1         0         0         0\n')
outfile.write('         1         0         0         0\n')
z.append('        13   1.00000(10e20.12)                  -1\n')
outfile.write('        13   1.00000(10e20.12)                  -1\n')
count=3
for m,matrix in enumerate(out):
    for line in matrix:
        z.append(line) #write to file
        temp_list = line.split()
        final = ''
        for col in temp_list:
            final=final + col.rjust(20)
        outfile.write(final + '\n')
        count += 1
    if (m+1) % 279==0:
        z.append('         1         0         0         0\n')
        outfile.write('         1         0         0         0\n')
        z.append('        13   1.00000(10e20.12)                  -1\n')
        outfile.write('        13   1.00000(10e20.12)                  -1\n')
        count += 2
        print(m,line,count)
# close file
outfile.close()




# Drain Based on Reaches ##############################################################################################
def DRN_tpl():
    drn = open(os.path.join(model_ws + os.sep + "sa00_flow.drn"), 'r')
    lines = drn.readlines()
    drn.close()

    drn_reaches = pd.read_csv(os.path.join(model_ws + os.sep + "sa00_flow_drains.csv"), header=None)

    reach_numbers = [0, 4, 5, 6]

    lay0 = []
    lay4 = []
    lay5 = []
    lay6 = []

    r0 = []
    r4 = []
    r5 = []
    r6 = []

    c0 = []
    c4 = []
    c5 = []
    c6 = []

    for i in range(len(drn_reaches)):
        if drn_reaches[3][i] == 0:
            lay0.append(drn_reaches[0][i])
            r0.append(drn_reaches[1][i])
            c0.append(drn_reaches[2][i])
        elif drn_reaches[3][i] == 4:
            lay4.append(drn_reaches[0][i])
            r4.append(drn_reaches[1][i])
            c4.append(drn_reaches[2][i])
        elif drn_reaches[3][i] == 5:
            lay5.append(drn_reaches[0][i])
            r5.append(drn_reaches[1][i])
            c5.append(drn_reaches[2][i])
        else:
            lay6.append(drn_reaches[0][i])
            r6.append(drn_reaches[1][i])
            c6.append(drn_reaches[2][i])

    lay0 = [str(x) for x in lay0]
    r0 = [str(x) for x in r0]
    c0 = [str(x) for x in c0]

    lay4 = [str(x) for x in lay4]
    r4 = [str(x) for x in r4]
    c4 = [str(x) for x in c4]

    lay5 = [str(x) for x in lay5]
    r5 = [str(x) for x in r5]
    c5 = [str(x) for x in c5]

    lay6 = [str(x) for x in lay6]
    r6 = [str(x) for x in r6]
    c6 = [str(x) for x in c6]

    new_lines = lines
    count = 0
    for line in lines:
        if len(line.split()) < 5:
            new_line = line
        if line.split()[0] in lay0 and line.split()[1] in r0 and line.split()[2] in c0:
            new_line = " ".join([line.split()[0].rjust(10), line.split()[1].rjust(10), line.split()[2].rjust(10),
                                    "#Drn_R{}_HEAD#".format(0).rjust(10), "#Drn_R{}_Cond#".format(0).rjust(10)])
            new_lines[count] = new_line
        elif line.split()[0] in lay4 and line.split()[1] in r4 and line.split()[2] in c4:
            new_line = " ".join([line.split()[0].rjust(10), line.split()[1].rjust(10), line.split()[2].rjust(10),
                                    "#Drn_R{}_HEAD#".format(4).rjust(10), "#Drn_R{}_Cond#".format(4).rjust(10)])
            new_lines[count] = new_line
        elif line.split()[0] in lay5 and line.split()[1] in r5 and line.split()[2] in c5:
            new_line = " ".join([line.split()[0].rjust(10), line.split()[1].rjust(10), line.split()[2].rjust(10),
                                "#Drn_R{}_HEAD#".format(5).rjust(10), "#Drn_R{}_Cond#".format(5).rjust(10)])
            new_lines[count] = new_line
        elif line.split()[0] in lay6 and line.split()[1] in r6 and line.split()[2] in c6:
            new_line = " ".join([line.split()[0].rjust(10), line.split()[1].rjust(10), line.split()[2].rjust(10),
                                    "#Drn_R{}_HEAD#".format(6).rjust(10), "#Drn_R{}_Cond#".format(6).rjust(10)])
            new_lines[count] = new_line
        count += 1


    with open(os.path.join(os.path.join(model_ws + os.sep + "sa00_flow.drn.tpl")), 'w') as f:
        f.write('pft #\n')
        for item in new_lines:
            if '\n' in item:
                f.write("%s" % item)
            else:
                f.write("%s\n" % item)
        f.close()








