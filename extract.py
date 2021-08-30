

def extract_results():
	"""extract the simulation results for locations of interest for all simulation times
	for each identified binary output file

	Note:
		This function is designed to be called during the model forward run process
		from within the directory where the model is being run.  That means the
		point info csv files will need to be in that directory also.

		This function can be called like "python extract.py" from the command line/
		batch file or can be called in a python script by first adding "import extract" to the
		script and then calling "extract.extract_results()"

	"""

	import os
	import pandas as pd
	import flopy
	# the results files to process - the extension is important!
	results_files = ["sa00_U.con","sa00_U.hds"]

	# the csv files of point locations of interest.
	pts_files = ["sa00_TransportModel_conctargets.csv",
				 "sa00_TransportModel_conctargets.csv",
				 "SA_compliancePoints.csv"]
	# rename the columns in each point file to have consistent columns
	rename_dict = {"layer":"lay","column":"col","well":"name","row":"row"}
	keep = list(rename_dict.values())
	keep.sort()
	pts_dfs = [pd.read_csv(pts_file) for pts_file in pts_files]
	keep_dfs = []
	for pts_df in pts_dfs:
		pts_df.columns = pts_df.columns.map(str.lower)
		pts_df.columns = pts_df.columns.map(lambda x: rename_dict.get(x,x))
		pts_df = pts_df.loc[:,keep]
		keep_dfs.append(pts_df)
		print(pts_df.columns)
	# concat all the point file dfs into a single df
	df = pd.concat(keep_dfs)
	# we only want the spatial info for each location, so we dont need multiple entries (one per time)
	df = df.drop_duplicates(subset="name")

	#add cols that we will use to form a more meaningful df index
	df.loc[:,"site_name"] = [str(v).lower() for v in df.name.values]
	df.loc[:, "k"] = df.lay - 1
	df.loc[:, "i"] = df.row - 1
	df.loc[:, "j"] = df.col - 1

	# make that fancy index
	df.index = df.apply(lambda x: "name:{0}_k:{1}_j:{2}_k:{3}".format(x.site_name.lower(),x.k,x.i,x.j),axis=1)
	df.index.name = "site_name"

	# now process each results file
	for results_file in results_files:
		# here is where the extension matters:
		if results_file.lower().endswith("con"):
			hds = flopy.utils.HeadFile(results_file,precision="single",text="conc  m speci 1 ")
		else:
			hds = flopy.utils.HeadFile(results_file, precision="single")

		# get all the data in a one big 4-d array
		data = hds.get_alldata()

		# process each output file in that array
		dfs = []
		for kper in range(data.shape[0]):
			df_kper = df.copy()
			dcol = "kper:{0:03d}".format(kper)
			df_kper.loc[:,dcol] = data[kper,df.k,df.i,df.j]
			dfs.append(df_kper.loc[:,dcol])
		# concat all the output time dfs into one df and save
		df_kper = pd.concat(dfs,axis=1)
		df_kper.to_csv(results_file.lower()+"_processed.csv")





if __name__ == "__main__":
	extract_results()