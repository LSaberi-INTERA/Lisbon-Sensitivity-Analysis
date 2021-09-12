

import extract
import os.path

#Remove the output from the previous run
flow_out = ['sa00_flow.out', 'sa00_flow.cbb', 'sa00_flow.cw5', 'sa00_flow.ddn', 'sa00_flow.hds']
U_out = ['sa00_U.out', 'sa00_U.hds', 'sa00_U.con', 'sa00_U.ddn', 'sa00_U.cw5', 'sa00_U.cbb']

for f in flow_out:
    try:
        os.remove(f)
    except:
        print('No Flow Output File')

for u in U_out:
    try:
        os.remove(u)
    except:
        print('No U Output File')

# pyemu.os_utils.run('run_flow.bat.exe')
os.system('run_flow.bat')
# pyemu.os_utils.run('run_transport.bat.exe')
os.system('run_transport.bat')
extract.extract_results()

