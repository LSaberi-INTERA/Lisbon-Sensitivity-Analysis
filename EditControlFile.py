
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


# Create control file ##################################################################################################
tpl_files = ['sa00_flow.bcf.tpl', 'sa00_flow.drn.tpl', 'sa00_flow.hfb.tpl', 'sa00_flow.rch.tpl',
             'sa00_flow.wel.tpl', 'sa00_flow.wl5.tpl', 'sa00_U.bcf.tpl', 'sa00_U.drn.tpl',
             'sa00_U.hfb.tpl', 'sa00_U.rch.tpl', 'sa00_U.wel.tpl', 'sa00_U.wl5.tpl', 'sa00_U.btn.tpl']
in_files = ['sa00_flow.bcf', 'sa00_flow.drn', 'sa00_flow.hfb', 'sa00_flow.rch',
             'sa00_flow.wel', 'sa00_flow.wl5', 'sa00_U.bcf', 'sa00_U.drn',
             'sa00_U.hfb', 'sa00_U.rch', 'sa00_U.wel', 'sa00_U.wl5', 'sa00_U.btn']
ins_files = ['sa00_U.con_processed.csv.ins', 'sa00_U.hds_processed.csv.ins', 'sa00_flow.hds_processed.csv.ins']
out_files = ['sa00_U.con_processed.csv', 'sa00_U.hds_processed.csv', 'sa00_flow.hds_processed.csv']
pst = pyemu.Pst.from_io_files(tpl_files, in_files, ins_files, out_files)
pst.write('lisbon_Final4.pst')

# Edit the Control File and Rewrite it #################################################################################
pst_r = pyemu.Pst('lisbon_Final4.pst')
pst_r.write('lisbon_v7.pst', version=2)

pst_df = pst_r.parameter_data
for i in range(len(pst_df['parval1'])):
    if isinstance(pst_df['parval1'][i], str) == True:
        pst_df['parval1'][i] = float(pst_df['parval1'][i])


#Change parchglim to Relative for params with negative parlbnd
for i in range(len(pst_df.parval1)):
    if pst_df['parval1'].iloc[i] < 0:
        pst_df['parlbnd'].iloc[i] = pst_df['parval1'].iloc[i] * 1.8
        pst_df['parchglim'].iloc[i] = 'relative'

# Update Recharge Values (parval1) for each SP and Zone in the Control File
rch = open(m_name+ ".rch", 'r')
    lines = rch.readlines()
    rch.close()
rch_tpl = open(m_name + ".rch.tpl", 'r')
    linestpl = rch_tpl.readlines()
    rch_tpl.close()

pst_parnme = pst_df['parnme'].tolist()
pst_parval1 = pst_df['parval1'].tolist()

pname = []
pvalue = []
for i in range(4, len(linestpl)):
    for e in range(len(linestpl[i].split())):
        if len(linestpl[i].split()) >= 8 and linestpl[i].split()[e].split('~')[1].lower() in pst_parnme:
            p = linestpl[i].split()[e].split('~')[1].lower()
            v = lines[i-1].split()[e]
            pname.append(p)
            pvalue.append(v)

#
pname_uniqe = []
pvalue_uniqe = []

indexes = [pname.index(x) for x in set(pname)]
for i in indexes:
    pname_uniqe.append(pname[i])
    pvalue_uniqe.append(pvalue[i])

for i in range(len(pname_uniqe)):
    if pname_uniqe[i] in pst_parnme:
        ind = pst_df.index[pst_df['parnme'] == pname_uniqe[i]]
        pst.parameter_data.loc[ind, "parval1"] = pvalue_uniqe[i]

# Update Recharge Values (parval1) for each SP and Zone for U model in the Control File #
rchU = open(m_name_U+ ".rch", 'r')
linesU = rchU.readlines()
rchU.close()
rchU_tpl = open(m_name_U + ".rch.tpl", 'r')
linestplU = rchU_tpl.readlines()
rchU_tpl.close()

# ind = []
pnameU = []
pvalueU = []
for i in range(4, len(linestplU)):
    for e in range(len(linestplU[i].split())):
        if len(linestplU[i].split()) >= 8 and linestplU[i].split()[e].split('~')[1].lower() in pst_parnme:
            # print(i, e, len(linestpl[i].split()), len(linesU[i].split()), linestpl[i].split()[e].split('~')[1].lower(),
            #       lines[i-1].split()[e])
            p = linestplU[i].split()[e].split('~')[1].lower()
            v = linesU[i-1].split()[e]
            pnameU.append(p)
            pvalueU.append(v)

pnameU_uniqe = []
pvalueU_uniqe = []

indexesU = [pnameU.index(x) for x in set(pnameU)]
for i in indexesU:
    pnameU_uniqe.append(pnameU[i])
    pvalueU_uniqe.append(pvalueU[i])

for i in range(len(pnameU_uniqe)):
    if pnameU_uniqe[i] in pst_parnme:
        ind = pst_df.index[pst_df['parnme'] == pnameU_uniqe[i]]
        pst.parameter_data.loc[ind, "parval1"] = pvalueU_uniqe[i]

#Replace DRN Flow Values in pst file ############################################################################
m_name = 'sa00_flow'
m_name_U = 'sa00_U'
drn = open(m_name+ ".drn", 'r')
lines = drn.readlines()
drn.close()

drnU = open(m_name_U + ".drn", 'r')
linesU = drnU.readlines()
drnU.close()

drn_tpl = open(m_name + ".drn.tpl", 'r')
linestpl = drn_tpl.readlines()
drn_tpl.close()

drn_tplU = open(m_name_U + ".drn.tpl", 'r')
linestplU = drn_tplU.readlines()
drn_tplU.close()

pst_parnme = pst_df['parnme'].tolist()
pst_parval1 = pst_df['parval1'].tolist()

# ind = []
for i in range(3, len(linestpl)):
    if len(linestpl[i].split()) == 5 and linestpl[i].split()[3].split('~')[1].lower() in pst_parnme:
        index = pst_parnme.index(linestpl[i].split()[3].split('~')[1].lower())
        pst_parval1[index] = lines[i-1].split()[3].ljust(16)

for i in range(3, len(linestplU)):
    if len(linestplU[i].split()) == 5 and linestplU[i].split()[3].split('~')[1].lower() in pst_parnme:
        index = pst_parnme.index(linestplU[i].split()[3].split('~')[1].lower())
        pst_parval1[index] = linesU[i-1].split()[3].ljust(16)

# Update QCqp Values in the PST file ###########################################################################
wl5 = open(m_name+ ".wl5", 'r')
    lines = wl5.readlines()
    wl5.close()
wl5_tpl = open(m_name + ".wl5.tpl", 'r')
    linestpl = wl5_tpl.readlines()
    wl5_tpl.close()

for i in range(9, len(linestpl)):
    if len(linestpl[i].split()) == 5 and linestpl[i].split()[4].split('~')[1].lower() in pst_parnme:
        # print(linestpl[i].split()[4].split('~')[1].lower())
        index = pst_parnme.index(linestpl[i].split()[4].split('~')[1].lower())
        # ind.append(index)
        # print(i, linestpl[i].split()[4].split('~')[1].lower(), lines[i-1].split()[4], index, pst_parnme[index])
        pst_parval1[index] = lines[i-1].split()[4].ljust(16)

# To apply the changes to the parvals in dataframe
n = pst_df.columns[3]
t = pst_df.columns[1]
pst_df[n] = pst_parval1
# pst_df[t] = pst_partrans

# Add Partied Section and 2nd Section of Parameter Data Section #######################################################
par = pst.parameter_data
par.loc[:,"partied"] = np.nan

#Set All parametrs to be tied (partran)
pst.parameter_data.loc[:,t] = 'tied'

#Create a separate list of parameters with partrans log, none, or fixed
partran_log = ['q_cap_1_13','dr0u1', 'dr0_1', 'alphal', 'c_u_lti',
                'c_u_uti', 'hfb_r2', 'hfb_r3', 'hfb_r4', 'k_z1', 'k_z10', 'k_z12',
       'k_z15', 'k_z16', 'k_z18', 'k_z2', 'k_z20', 'k_z22', 'k_z23','k_z3', 'k_z4',
       'k_z6', 'k_z8', 'q_lti_in', 'q_lti_out', 'q_uti_in', 'q_uti_out', 'q_rech1_sp1',
       'q_rech2_sp1', 'q_rech3_sp1', 'q_rech6_sp1',
       'q_rech7_sp1', 'qu_rech1_sp1', 'ss', 'qu_rech2_sp1', 'qu_rech3_sp1', 'qu_rech6_sp1',
       'qu_rech7_sp1']

partran_fixed = ['q_w_well', 'q_e_well', 'hfb_r0', 'hfb_r1', 'q_rech5_sp1', 'qu_rech5_sp1', 'k_z5']
partran_none = ['c_u_lti', 'c_u_uti', 'q_lti_in', 'q_lti_out', 'q_uti_in', 'q_uti_out', 'q_cap_1_13', 'sy',
                'dr0_s1', 'dr4_s1', 'dr5_s1', 'dr6_s1', 'dr0u1', 'dr4u1', 'dr5u1', 'dr6u1', 'kd_u']

#Set PARTRAN to log/fixed/none for all parametrs using lists above #####################################################
for parname in pst_df['parnme']:
    if parname not in partran_log and parname not in partran_fixed and parname not in partran_none :
        ind = pst_df.index[pst_df['parnme'] == parname]
        pst.parameter_data.loc[ind, "partied"] = parname

for parname in pst_df['parnme']:
    if parname in partran_log:
        ind = pst_df.index[pst_df['parnme'] == parname]
        pst.parameter_data.loc[ind, "partrans"] = 'log'.ljust(16)

for parname in pst_df['parnme']:
    if parname in partran_fixed:
        ind = pst_df.index[pst_df['parnme'] == parname]
        pst.parameter_data.loc[ind, "partrans"] = 'fixed'.ljust(16)

for parname in pst_df['parnme']:
    if parname in partran_none:
        ind = pst_df.index[pst_df['parnme'] == parname]
        pst.parameter_data.loc[ind, "partrans"] = 'none'.ljust(16)

# Set PARTIED based on what parameters is tied to what
for partie in pst_df['partied']:
    if str(partie).startswith('dr') and str(partie)[2] == '0' and str(partie)[3] == 'u':
        ind = pst_df.index[pst_df['partied'] == partie]
        pst.parameter_data.loc[ind, "partied"] = 'dr0u1'
    if str(partie).startswith('dr') and str(partie)[2] == '4' and str(partie)[3] == 'u':
        ind = pst_df.index[pst_df['partied'] == partie]
        pst.parameter_data.loc[ind, "partied"] = 'dr4u1'
    if str(partie).startswith('dr') and str(partie)[2] == '5' and str(partie)[3] == 'u':
        ind = pst_df.index[pst_df['partied'] == partie]
        pst.parameter_data.loc[ind, "partied"] = 'dr5u1'
    if str(partie).startswith('dr') and str(partie)[2] == '6' and str(partie)[3] == 'u':
        ind = pst_df.index[pst_df['partied'] == partie]
        pst.parameter_data.loc[ind, "partied"] = 'dr6u1'
    if str(partie).startswith('dr') and str(partie)[2] == '0' and str(partie)[3] == '_':
        ind = pst_df.index[pst_df['partied'] == partie]
        pst.parameter_data.loc[ind, "partied"] = 'dr0_s1'
    if str(partie).startswith('dr') and str(partie)[2] == '4' and str(partie)[3] == '_':
        ind = pst_df.index[pst_df['partied'] == partie]
        pst.parameter_data.loc[ind, "partied"] = 'dr4_s1'
    if str(partie).startswith('dr') and str(partie)[2] == '5' and str(partie)[3] == '_':
        ind = pst_df.index[pst_df['partied'] == partie]
        pst.parameter_data.loc[ind, "partied"] = 'dr5_s1'
    if str(partie).startswith('dr') and str(partie)[2] == '6' and str(partie)[3] == '_':
        ind = pst_df.index[pst_df['partied'] == partie]
        pst.parameter_data.loc[ind, "partied"] = 'dr6_s1'
    if str(partie).startswith('q') and str(partie).split('_')[1] == 'rech1':
        ind = pst_df.index[pst_df['partied'] == partie]
        pst.parameter_data.loc[ind, "partied"] = 'q_rech1_SP1'
    if str(partie).startswith('q') and str(partie).split('_')[1] == 'rech2':
        ind = pst_df.index[pst_df['partied'] == partie]
        pst.parameter_data.loc[ind, "partied"] = 'q_rech2_SP1'
    if str(partie).startswith('q') and str(partie).split('_')[1] == 'rech3':
        ind = pst_df.index[pst_df['partied'] == partie]
        pst.parameter_data.loc[ind, "partied"] = 'q_rech3_SP1'
    if str(partie).startswith('q') and str(partie).split('_')[1] == 'rech4':
        ind = pst_df.index[pst_df['partied'] == partie]
        pst.parameter_data.loc[ind, "partied"] = 'q_rech4_SP1'
    if str(partie).startswith('q') and str(partie).split('_')[1] == 'rech5':
        ind = pst_df.index[pst_df['partied'] == partie]
        pst.parameter_data.loc[ind, "partied"] = 'q_rech5_SP1'
    if str(partie).startswith('q') and str(partie).split('_')[1] == 'rech6':
        ind = pst_df.index[pst_df['partied'] == partie]
        pst.parameter_data.loc[ind, "partied"] = 'q_rech6_SP1'
    if str(partie).startswith('q') and str(partie).split('_')[1] == 'rech7':
        ind = pst_df.index[pst_df['partied'] == partie]
        pst.parameter_data.loc[ind, "partied"] = 'q_rech7_SP1'
    if str(partie).startswith('q') and str(partie).split('_')[1] == 'rech8':
        ind = pst_df.index[pst_df['partied'] == partie]
        pst.parameter_data.loc[ind, "partied"] = 'q_rech8_SP1'
    if str(partie).startswith('q') and str(partie).split('_')[1] == 'rech9':
        ind = pst_df.index[pst_df['partied'] == partie]
        pst.parameter_data.loc[ind, "partied"] = 'q_rech9_SP1'
    if str(partie).startswith('alpha'):
        ind = pst_df.index[pst_df['partied'] == partie]
        pst.parameter_data.loc[ind, "partied"] = 'alphal'
    if str(partie).startswith('q') and str(partie).split('_')[1] == 'cap':
        ind = pst_df.index[pst_df['partied'] == partie]
        pst.parameter_data.loc[ind, "partied"] = 'q_cap_1_13'
    if str(partie).startswith('q') and str(partie).split('_')[1] == 'cap' and str(partie).split('_')[2] == '2' :
        ind = pst_df.index[pst_df['partied'] == partie]
        pst.parameter_data.loc[ind, "partied"] = 'q_cap_2_1'
    if str(partie).startswith('q_u') and str(partie).split('_')[2] == 'rech1':
        ind = pst_df.index[pst_df['partied'] == partie]
        pst.parameter_data.loc[ind, "partied"] = 'q_u_rech1_sp1'
    if str(partie).startswith('q_u') and str(partie).split('_')[2] == 'rech2':
        ind = pst_df.index[pst_df['partied'] == partie]
        pst.parameter_data.loc[ind, "partied"] = 'q_u_rech2_sp1'
    if str(partie).startswith('q_u') and str(partie).split('_')[2] == 'rech3':
        ind = pst_df.index[pst_df['partied'] == partie]
        pst.parameter_data.loc[ind, "partied"] = 'q_u_rech3_sp1'
    if str(partie).startswith('q_u') and str(partie).split('_')[2] == 'rech4':
        ind = pst_df.index[pst_df['partied'] == partie]
        pst.parameter_data.loc[ind, "partied"] = 'q_u_rech4_sp1'
    if str(partie).startswith('q_u') and str(partie).split('_')[2] == 'rech5':
        ind = pst_df.index[pst_df['partied'] == partie]
        pst.parameter_data.loc[ind, "partied"] = 'q_u_rech5_sp1'
    if str(partie).startswith('q_u') and str(partie).split('_')[2] == 'rech6':
        ind = pst_df.index[pst_df['partied'] == partie]
        pst.parameter_data.loc[ind, "partied"] = 'q_u_rech6_sp1'
    if str(partie).startswith('q_u') and str(partie).split('_')[2] == 'rech7':
        ind = pst_df.index[pst_df['partied'] == partie]
        pst.parameter_data.loc[ind, "partied"] = 'q_u_rech7_sp1'
    if str(partie).startswith('q_u') and str(partie).split('_')[2] == 'rech8':
        ind = pst_df.index[pst_df['partied'] == partie]
        pst.parameter_data.loc[ind, "partied"] = 'q_u_rech8_sp1'
    if str(partie).startswith('q_u') and str(partie).split('_')[2] == 'rech9':
        ind = pst_df.index[pst_df['partied'] == partie]
        pst.parameter_data.loc[ind, "partied"] = 'q_u_rech9_sp1'
    if str(partie).startswith('qc'):
        ind = pst_df.index[pst_df['partied'] == partie]
        pst.parameter_data.loc[ind, "partied"] = 'q_cap_1_13'

#Re-write the updated control file
pst.write('lisbon_Final4.pst')

# Set the Upper and Lower Bounds for all Params in the Control file ###################################################
pstfile = os.path.join(os.path.realpath("PESTRUN_check"), 'lisbon_posterior.pst')
pst_r = pyemu.Pst(pstfile)

pst_df = pst_r.parameter_data

for i in range(len(pst_df['parval1'])):
    if isinstance(pst_df['parval1'][i], str) == True:
        pst_df['parval1'][i] = float(pst_df['parval1'][i])

for i in range(len(pst_df.parnme)):
    if str(pst_df['parnme'].iloc[i]).startswith('qcp') or str(pst_df['parnme'].iloc[i]).startswith('q_cp') and pst_df['parval1'].iloc[i]<0:
        pst_df['parlbnd'].iloc[i] = pst_df['parval1'].iloc[i] * 1.2
        pst_df['parubnd'].iloc[i] = pst_df['parval1'].iloc[i] * 0.8

for i in range(len(pst_df.parnme)):
    if str(pst_df['parnme'].iloc[i]).startswith('dr'):
        pst_df['parlbnd'].iloc[i] = pst_df['parval1'].iloc[i] -5
        pst_df['parubnd'].iloc[i] = pst_df['parval1'].iloc[i] +5

for i in range(len(pst_df.parnme)):
    if str(pst_df['parnme'].iloc[i]).startswith('q_rech1') or str(pst_df['parnme'].iloc[i]).startswith('qu_rech1') :
        pst_df['parlbnd'].iloc[i] = pst_df['parval1'].iloc[i] * 0.5
        pst_df['parubnd'].iloc[i] = pst_df['parval1'].iloc[i] * 2

for i in range(len(pst_df.parnme)):
    if str(pst_df['parnme'].iloc[i]).startswith('q_rech2') or str(pst_df['parnme'].iloc[i]).startswith('qu_rech2') :
        pst_df['parlbnd'].iloc[i] = pst_df['parval1'].iloc[i] * 0.5
        pst_df['parubnd'].iloc[i] = pst_df['parval1'].iloc[i] * 2

for i in range(len(pst_df.parnme)):
    if str(pst_df['parnme'].iloc[i]).startswith('q_rech3') or str(pst_df['parnme'].iloc[i]).startswith('qu_rech3') :
        pst_df['parlbnd'].iloc[i] = pst_df['parval1'].iloc[i] * 0.5
        pst_df['parubnd'].iloc[i] = pst_df['parval1'].iloc[i] * 2

for i in range(len(pst_df.parnme)):
    if str(pst_df['parnme'].iloc[i]).startswith('q_rech4') or str(pst_df['parnme'].iloc[i]).startswith('qu_rech4') :
        pst_df['parlbnd'].iloc[i] = pst_df['parval1'].iloc[i] * 0.5
        pst_df['parubnd'].iloc[i] = pst_df['parval1'].iloc[i] * 2

for i in range(len(pst_df.parnme)):
    if str(pst_df['parnme'].iloc[i]).startswith('q_rech5') or str(pst_df['parnme'].iloc[i]).startswith('qu_rech5') :
        pst_df['parlbnd'].iloc[i] = pst_df['parval1'].iloc[i]
        pst_df['parubnd'].iloc[i] = pst_df['parval1'].iloc[i]

for i in range(len(pst_df.parnme)):
    if str(pst_df['parnme'].iloc[i]).startswith('q_rech6') or str(pst_df['parnme'].iloc[i]).startswith('qu_rech6') :
        pst_df['parlbnd'].iloc[i] = pst_df['parval1'].iloc[i] * 0.5
        pst_df['parubnd'].iloc[i] = pst_df['parval1'].iloc[i] * 2

for i in range(len(pst_df.parnme)):
    if str(pst_df['parnme'].iloc[i]).startswith('q_rech7') or str(pst_df['parnme'].iloc[i]).startswith('qu_rech7') or str(pst_df['parnme'].iloc[i]).startswith('q_rech8') or str(pst_df['parnme'].iloc[i]).startswith('qu_rech8') or str(pst_df['parnme'].iloc[i]).startswith('q_rech9') or str(pst_df['parnme'].iloc[i]).startswith('qu_rech9') :
        pst_df['parlbnd'].iloc[i] = pst_df['parval1'].iloc[i] * 0.54
        pst_df['parubnd'].iloc[i] = pst_df['parval1'].iloc[i] * 3.01

pst_r.write(os.path.join(os.path.realpath("PESTRUN_check"), 'lisbon_posterior2.pst'), version=2)

