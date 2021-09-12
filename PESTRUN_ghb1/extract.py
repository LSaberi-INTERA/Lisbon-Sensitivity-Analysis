

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
	import numpy as np
	import pandas as pd

	import flopy


	# the results files to process - the extension is important!
	results_files = ["sa00_U.con","sa00_U.hds", "sa00_flow.hds"]

	# the csv files of point locations of interest.
	pts_files = ["sa00_TransportModel_conctargets.csv", "sa00_TransportModel_headtargets.csv",
				 "sa_flow_targets_export.csv",
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

	thres = 0.85 # from Bill; in model units
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
		if results_file.lower().endswith("con"):
			# transpose to get times on the index
			df_kper = df_kper.T

			# set the index to totim values
			df_kper.index = hds.get_times()
			df_kper.index.name = "totim"
			
			# some plotting just for testing
			#import matplotlib.pyplot as plt
			#fig,ax = plt.subplots(1,1)
			#df_kper.loc[:,"name:eastwell_k:11_j:103_k:27"].plot(ax=ax)
			

			# reindex to daily across the full sim range - has lots of nans
			df_reindex = df_kper.reindex(np.arange(0,max(hds.get_times())))
			# now fill those nans with interpolated values - cubic spline looks pretty good...
			df_reindex = df_reindex.interpolate(method="cubicspline")
			# backfill from the first output time to the beginning of the sim
			df_reindex.fillna(method="bfill",inplace=True)

			#df_reindex.loc[:,"name:eastwell_k:11_j:103_k:27"].plot(ax=ax)
			#plt.show()
			with open("time_to_thres.processed.csv",'w') as f:
				f.write("site,days_to_thres\n")
				for site in df_reindex.columns:
					df_site = df_reindex.loc[:,site].copy()
					df_site = df_site.loc[df_site.values>=thres]
					if df_site.shape[0] == 0:
						f.write("{0},{1:15.6E}\n".format(site,0.0))
					else:
						f.write("{0},{1:15.6E}\n".format(site,df_site.index[0]))



if __name__ == "__main__":
	extract_results()


