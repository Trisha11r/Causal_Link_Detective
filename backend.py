import pandas as pd
import json
import numpy as np
from flask import Flask, render_template, request, redirect, Response, jsonify
import seaborn as sns

import os
import pandas as pd
import pydot
from kaggle.api.kaggle_api_extended import KaggleApi
import json
import zipfile

api = KaggleApi()
api.authenticate()

os.environ["PATH"] += os.pathsep + 'C:/Users/slash/Anaconda3/pkgs/graphviz-2.38-hfd603c8_2/Library/bin/graphviz/'
data_dir = 'C:/Users/slash/Desktop/SBU MATERIAL/Sem2/523 (Klaus Mueller)/Implement/LUCAS.csv'
df = pd.read_table(data_dir, sep=",")

from pycausal.pycausal import pycausal as pc




app = Flask(__name__)
@app.route("/", methods = ['POST', 'GET'])
def index():
	global df
	
	#main data dictionary containing all plotting data
	data_dict = {}
	# data_dict['datasets'] = dataset_list
	data_dict['fdl_data'] = json.dumps(data, indent=2);
	data_dict['corr_data'] = json.dumps(corr_list)
	data_dict['node_data'] = json.dumps(node_data, indent=2)
	print(data_dict['fdl_data'])
	return render_template("frontend.html", data=data_dict)

@app.route("/getDatasetList/<datasetName>")
def getDatasetList(datasetName):
	datasets = api.dataset_list(search = datasetName, file_type = 'csv')
	print("HELLO")
	dataset_list = []
	for dat in datasets:
		print(dat)
		dataset_list.append(str(dat))
	print("DATASET")
	print(dataset_list)
	return json.dumps(dataset_list)

@app.route("/downloadDataset/<datasetName1>/<datasetName2>")
def downloadDataset(datasetName1, datasetName2):
	print("Trying to download")
	datasetFullName = datasetName1 + "/" + datasetName2
	print(datasetName1 + "/" + datasetName2)
	api.dataset_download_files(datasetFullName)
	path = datasetFullName.split("/")
	datasetFile = path[len(path)-1]
	datasetFileName = datasetFile + ".zip"
	datasetCSVName = datasetFile + ".csv"
	archive = zipfile.ZipFile(datasetFileName, 'r')
	files = archive.namelist()
	print(files)
	image_data = archive.read(files[0])
	print(image_data)
	return ""

if __name__ == "__main__":
	#manual data
	# data = {"nodes":[{"id": "Smoking", "group": 1},
	# 								{"id": "Yellow Fingers", "group": 1},
	# 								{"id": "Anxiety", "group": 1}, 
	# 								{"id": "Peer_Pressure", "group": 1},
	# 								{"id": "Genetics", "group": 1}, 
	# 								{"id": "Attention_Disorder", "group": 1},
	# 								{"id": "Allergy", "group": 1}, 
	# 								{"id": "Coughing", "group": 1},
	# 								{"id": "Lung_Cancer", "group": 1},
	# 								{"id": "Car_Accident", "group": 1},
	# 								{"id": "Fatigue", "group": 1}],
	# 						"links":[{"source": "Attention_Disorder", "target": "Car_Accident", "value": 0.5},
	# 						        {"source": "Fatigue", "target": "Car_Accident", "value": 0.6},
	# 						        {"source": "Lung_Cancer", "target": "Fatigue", "value": 0.3},
	# 						        {"source": "Genetics", "target": "Lung_Cancer", "value": 0.2},
	# 						        {"source": "Allergy", "target": "Coughing", "value": 0.9},
	# 						        {"source": "Lung_Cancer", "target": "Car_Accident", "value": -0.9}]}


	# graph data from file							      
	data = pd.read_csv('LUCAS.csv')
	data = data.dropna()
	corr_data = data.corr()
	corr_data = corr_data.to_numpy()
	# corr_data_original = data.corr()

	pc = pc()
	pc.start_vm()

	from pycausal import search as s
	tetrad = s.tetradrunner()
	tetrad.run(algoId = 'fges', dfs = df, scoreId = 'sem-bic', dataType = 'continuous',
		   maxDegree = -1, faithfulnessAssumed = True, verbose = True)

	corr_list = corr_data.tolist()
	col = []
	for c in data.columns:
		col.append(c)

	all_links = []

	for i in range(len(col)):
		for j in range(len(col)):
			all_links.append({"source": col[i], "target": col[j], "value": corr_list[i][j]})

	all_nodes = []
	for i in range(len(col)):
		all_nodes.append({"id": col[i], "group": 1})



	node_data = tetrad.getNodes()
	edge_dict = {}
	edge_data = tetrad.getEdges()
	print("HELLO")
	
	for e in edge_data:
		# print(e)
		if(" --> " in e):
			pair = e.split(" --> ")	
			print(pair)
			if pair[0] in edge_dict:	
				val_list = edge_dict.get(pair[0])
				val_list.append(pair[1])
				edge_dict[pair[0]] = val_list

			edge_dict[pair[0]] = [pair[1]]

	print(edge_dict)
	graph_links = []
	for link_dict in all_links:
		if (link_dict.get("source") in edge_dict) and (link_dict.get("target") in edge_dict.get(link_dict.get("source"))):
			graph_links.append(link_dict)
	data = {"nodes": all_nodes, "links": graph_links}
	print("DATA")
	print(data)

	app.run(debug=True)
