
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

#Define Model Names
m_name_U = "sa00_U"
m_name = "sa00_flow"

# Read HFB (Horizontal Flow Barrier File) and Write It's Tempelate File #########################################
# hfb = open(os.path.join(model_ws + os.sep + m_name + ".hfb"), 'r')
hfb = open(m_name_U + ".hfb", 'r')
lines = hfb.readlines()
hfb.close()

hfb_reach = pd.read_csv(os.path.join('DataTPL' + os.sep, "HFB_reaches.csv"), header=0)

hfb_reach_number = hfb_reach.reach.astype(str)
hfb_R = []
for h in hfb_reach_number:
    hfb_R.append(h.partition('.')[0])
SA = hfb_reach.SA


count = 0
new_lines = lines.copy()
for line in new_lines:
    if len(line.split()) == 1:
        new_lines[count] = line
    elif len(line.split()) == 5:
            new_line = " ".join([line.split()[0].rjust(10), line.split()[1].rjust(9), line.split()[2].rjust(9),
                                line.split()[3].rjust(9), "#HFB_R{}#".format(hfb_R[count]).rjust(9)])
            new_lines[count] = new_line
    count += 1


with open(m_name_U + ".hfb.tpl", 'w') as f:
    f.write("pft #\n")
    for item in new_lines:
        if '\n' in item:
            f.write("%s" % item)
        else:
            f.write("%s\n" % item)
    f.close()


# Read bcf File ###########################################################################################

bcf =  open(m_name + ".bcf", 'r')
lines = bcf.readlines()
bcf.close()

z = open(os.path.join('DataTPL' + os.sep, "Kzone_matrix.dat"), "r")
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

z = lines.copy()
zones = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '12', '13', '14', '15', '16', '18', '19', '20', '22', '23', '24']
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
                            # if p == 1:
                            #     temp[update] = "#Ss#"
                            if p == 2:
                                temp[update] = f"#K_Z{update_values[u]}#"
                            if p == 3:
                                temp[update] = f"#K_Z{update_values[u]}#"
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

# open output file
outfile = open(m_name + ".bcf.tpl", 'w')

for l, line in enumerate(z):
    if l in touched_lines:
        outfile.write(line + '\n')
    else:
        outfile.write(line)

# close file
outfile.close()

# Read .wel file ##################################################################################
#For Flow Model

#Reading Input
wel = open(os.path.join(model_ws + os.sep + m_name + ".wel"), 'r')
lines = wel.readlines()
wel.close()

LTI = pd.read_csv(os.path.join(os.path.join(data_tpl + os.sep, "LTI_forImport_mod_SA_flow.csv")), header=0)
LTI_row = [str(x) for x in LTI.row.to_list()]
LTI_col = [str(x) for x in LTI.co.to_list()]
LTI_lay = [str(x) for x in LTI.layer.to_list()]
UTI = pd.read_csv(os.path.join(os.path.join(data_tpl + os.sep, "UTI_forImport_mod_SA_flow.csv")), header=0)
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

with open(os.path.join(flow_tpl + os.sep + m_name + ".wel.tpl"), 'w') as f:
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


with open(os.path.join(transport_tpl + os.sep + m_name_U + ".wel.tpl"), 'w') as f:
    f.write("pft #\n")
    f.write('       296        50         0\n')
    for item in new_lines:
        if '\n' in item:
            f.write("%s" % item)
        else:
            f.write("%s\n" % item)
    f.close()

# Read .wl5 file ##################################################################################
# For Uranium Model
def wl5_tpl_U():
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


    with open(os.path.join(transport_tpl + os.sep + m_name_U + ".wl5.tpl"), 'w') as f:
        for item in new_lines:
            if '\n' in item:
                f.write("%s" % item)
            else:
                f.write("%s\n" % item)
        f.close()

# For Flow Model
def wl5_tpl_Flow():
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


    with open(os.path.join(flow_tpl + os.sep + m_name + ".wl5.tpl"), 'w') as f:
        for item in new_lines:
            if '\n' in item:
                f.write("%s" % item)
            else:
                f.write("%s\n" % item)
        f.close()

# Read Recharge files ##############################################################################################
# For Flow Model
def Recharge_tpl_Flow():
    # rch = open(os.path.join(model_ws + os.sep + m_name + ".rch"), 'r')
    rch = open(m_name + ".rch", 'r')
    lines = rch.readlines()
    rch.close()

    rch_zones = open(os.path.join('DataTPL' + os.sep + "Rzone_matrix.dat"), 'r')
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

    SP_ind = [278, 557 ,836, 1115, 1394,1673,1952,2231,2510,2789,3068,3347,3626,3905,4184,4463,4742,5021,5300,
              5579,5858,6137,6416,6695,6974,7253,7532,7811,8090,8369,8648,8927]
    Zones = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
    update_indexes = []
    update_values = []
    y = lines_RCHzones*32
    out = x.copy()
    count = 1
    for i, m in enumerate(x):
        for j, line in enumerate(m):
            #print("Matrix",i," Line",j)
            update_indexes=[]
            update_values=[]
            for k, xelement in enumerate(line.split()):

                yelement = y[i].split()[10 * j + k ]
                if yelement in Zones:
                    update_indexes.append(k)
                    update_values.append(yelement)
            temp = line.split()
            for u,update in enumerate(update_indexes):
                temp[update]=f"~Q_U_Rech{update_values[u]}_SP{count}~".rjust(20)
            out[i][j]=' '.join(temp)
        # print(i)
        if i in SP_ind :
            count +=1


    # open output file
    # outfile = open(os.path.join(flow_tpl + os.sep + m_name + ".rch.tpl"), 'w')
    outfile = open(m_name + "2.rch.tpl", 'w')
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
            # print(m,line,count)
    # close file
    outfile.close()

# For Transport Model
def Recharge_tpl_U():
    # rch = open(os.path.join(model_ws_U + os.sep + m_name_U + ".rch"), 'r')
    rch = open(m_name_U + ".rch", 'r')
    lines = rch.readlines()
    rch.close()

    rch_zones = open(os.path.join('DataTPL' + os.sep + "Rzone_matrix.dat"), 'r')
    lines_RCHzones = rch_zones.readlines()
    rch_zones.close()

    new_lines = lines[3:].copy()
    matrix = 0
    x = [[] for _ in range(5303)]
    for i, line in enumerate(new_lines):
        # print(i, line, matrix)
        if (len(new_lines[i-1].split()) == 9) and (i > 0):
            matrix = matrix + 1
        # if matrix < 8928:
        if len(line.split()) >= 9:
            x[matrix].append(line)

    SP_ind = [278, 557 ,836, 1115, 1394,1673,1952,2231,2510,2789,3068,3347,3626,3905,4184,4463,4742,5021,5300,
              5579,5858,6137,6416,6695,6974,7253,7532,7811,8090,8369,8648,8927]
    Zones = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
    update_indexes = []
    update_values = []
    y = lines_RCHzones*32
    out = x.copy()
    count =1
    for i, m in enumerate(x):
        for j, line in enumerate(m):
            #print("Matrix",i," Line",j)
            update_indexes=[]
            update_values=[]
            for k, xelement in enumerate(line.split()):
                yelement = y[i].split()[10 * j + k ]
                if yelement in Zones:
                    update_indexes.append(k)
                    update_values.append(yelement)
            temp = line.split()
            for u,update in enumerate(update_indexes):
                temp[update]=f"~QU_Rech{update_values[u]}_SP{count}~".rjust(21)
            out[i][j]=' '.join(temp)
        if i in SP_ind:
            count += 1

    # open output file
    # outfile = open(os.path.join(transport_tpl + os.sep + m_name_U + ".rch.tpl"), 'w')
    outfile = open(m_name_U + "test.rch.tpl", 'w')
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
            # print(m,line,count)
    # close file
    outfile.close()

# Drain Based on Reaches ##############################################################################################
#Flow Model
def DRN_tpl_Flow():
    drn = open(os.path.join(os.path.realpath("FlowTransport_check"), "sa00_flow.drn"), 'r')
    lines = drn.readlines()
    drn.close()

    drn_reaches = pd.read_csv(os.path.join('DataTPL' + os.sep + "sa00_flow_drains.csv"), header=None)

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

    new_lines = lines.copy()
    count = 0
    # k = -1
    c = -1
    for line in lines:
        if len(line.split()) < 5:
            new_line = line
            # k += 1
            c = 0
        if line.split()[0] in lay0 and line.split()[1] in r0 and line.split()[2] in c0:
            new_line = "".join([line.split()[0].rjust(10), line.split()[1].rjust(10), line.split()[2].rjust(10),
                                    "~DR{}_S{}~".format(0,c).rjust(10), line.split()[4].rjust(10)])
            new_lines[count] = new_line
        elif line.split()[0] in lay4 and line.split()[1] in r4 and line.split()[2] in c4:
            new_line = "".join([line.split()[0].rjust(10), line.split()[1].rjust(10), line.split()[2].rjust(10),
                                    "~DR{}_S{}~".format(4,c).rjust(10), line.split()[4].rjust(10)])
            new_lines[count] = new_line
        elif line.split()[0] in lay5 and line.split()[1] in r5 and line.split()[2] in c5:
            new_line = "".join([line.split()[0].rjust(10), line.split()[1].rjust(10), line.split()[2].rjust(10),
                                "~DR{}_S{}~".format(5,c).rjust(10), line.split()[4].rjust(10)])
            new_lines[count] = new_line
        elif line.split()[0] in lay6 and line.split()[1] in r6 and line.split()[2] in c6:
            new_line = "".join([line.split()[0].rjust(10), line.split()[1].rjust(10), line.split()[2].rjust(10),
                                    "~DR{}_S{}~".format(6,c).rjust(10), line.split()[4].rjust(10)])
            new_lines[count] = new_line
        count += 1
        c += 1
        # if len(line) == 1:
        #     c = -1
        # print(count)


    with open(os.path.join(os.path.realpath("FlowTransport_check"), "sa00_flow.drn.tpl"), 'w') as f:
        f.write('ptf ~\n')
        for item in new_lines:
            if '\n' in item:
                f.write("%s" % item)
            else:
                f.write("%s\n" % item)
        f.close()


# Transport Model
def DRN_tpl_U():
    drn = open(os.path.join(os.path.realpath("FlowTransport_check"), "sa00_U.drn"), 'r')
    lines = drn.readlines()
    drn.close()

    drn_reaches = pd.read_csv(os.path.join('DataTPL' + os.sep + "sa00_flow_drains.csv"), header=None)

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

    new_lines = lines.copy()
    count = 0
    c = -1
    for line in lines:
        if len(line.split()) < 5:
            new_line = line
            # k += 1
            c = 0
        if line.split()[0] in lay0 and line.split()[1] in r0 and line.split()[2] in c0:
            new_line = "".join([line.split()[0].rjust(10), line.split()[1].rjust(10), line.split()[2].rjust(10),
                                    "~DR{}U{}~".format(0, c).rjust(10), line.split()[4].rjust(10)])
            new_lines[count] = new_line
        elif line.split()[0] in lay4 and line.split()[1] in r4 and line.split()[2] in c4:
            new_line = " ".join([line.split()[0].rjust(10), line.split()[1].rjust(10), line.split()[2].rjust(10),
                                    "~DR{}U{}~".format(4, c).rjust(10), line.split()[4].rjust(10)])
            new_lines[count] = new_line
        elif line.split()[0] in lay5 and line.split()[1] in r5 and line.split()[2] in c5:
            new_line = "".join([line.split()[0].rjust(10), line.split()[1].rjust(10), line.split()[2].rjust(10),
                                "~DR{}U{}~".format(5, c).rjust(10), line.split()[4].rjust(10)])
            new_lines[count] = new_line
        elif line.split()[0] in lay6 and line.split()[1] in r6 and line.split()[2] in c6:
            new_line = "".join([line.split()[0].rjust(10), line.split()[1].rjust(10), line.split()[2].rjust(10),
                                    "~DR{}U{}~".format(6, c).rjust(10), line.split()[4].rjust(10)])
            new_lines[count] = new_line
        count += 1
        c += 1


    with open(os.path.join(os.path.realpath("FlowTransport_check"), "sa00_U.drn.tpl"), 'w') as f:
        f.write('ptf ~\n')
        for item in new_lines:
            if '\n' in item:
                f.write("%s" % item)
            else:
                f.write("%s\n" % item)
        f.close()
