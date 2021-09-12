import os
import shutil
import pyemu

org_d = "PESTRUN_ghb1"
new_d = "repaired"

if os.path.exists(new_d):
	shutil.rmtree(new_d)
shutil.copytree(org_d,new_d)

pst = pyemu.Pst(os.path.join(new_d,"lisbon_posterior2.pst"))
pst.model_output_data.loc[:,"pest_file"] = pst.model_output_data.loc[:,"pest_file"].apply(str.lower)
print(pst.model_output_data.pest_file)
out_files = []
for ins_file in pst.instruction_files:
	ins_file = ins_file.lower()
	pst.drop_observations(os.path.join(new_d,ins_file),pst_path=".")
	os.remove(os.path.join(new_d,ins_file))

for out_file in [f for f in os.listdir(new_d) if f.endswith("_processed.csv")]:
	print(out_file)
	prefix = out_file.split("_")[1].replace(".","-")
	pyemu.pst_utils.csv_to_ins_file(os.path.join(new_d,out_file),prefix=prefix,longnames=True)
	pst.add_observations(os.path.join(new_d,out_file+".ins"))

pst.write(os.path.join(new_d,"repaired.pst"))