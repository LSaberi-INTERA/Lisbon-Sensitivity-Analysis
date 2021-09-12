
import pyemu
import os

tpldir = os.path.realpath("PESTRUN_ghb")
pestexe = os.path.join(os.path.realpath("PESTRUN_ghb"), 'pestpp-glm')
pstfile = os.path.join(os.path.realpath("PESTRUN_ghb"), 'lisbon_posterior2.pst')


pyemu.os_utils.start_workers( tpldir, pestexe, pstfile, num_workers=8,
                             master_dir='master')