import pandas as pd
import numpy as np
from flask import Flask, render_template, request, redirect, Response, jsonify

import os
import pandas as pd
from kaggle.api.kaggle_api_extended import KaggleApi
import json
import zipfile

import semopy
from semopy import Model
from semopy import Optimizer
from semopy import gather_statistics
from semopy.inspector import inspect

from pycausal import search as s

api = KaggleApi()
api.authenticate()
datasetName = "LUCAS.csv"
os.environ["PATH"] += os.pathsep + 'C:/Users/slash/Anaconda3/pkgs/graphviz-2.38-hfd603c8_2/Library/bin/graphviz/'

GLOBAL_subgraphs_data = []
GLOBAL_dataframe = []
GLOBAL_data = []
GLOBAL_node_data = []
GLOBAL_initial_nodes = []
GLOBAL_corr_list = []
GLOBAL_tetrad = []


from pycausal.pycausal import pycausal as pc

app = Flask(__name__)
@app.route("/", methods = ['POST', 'GET'])
def index():
	
	#main data dictionary containing all plotting data
	data_dict = {}
	data_dict['fdl_data'] = json.dumps(GLOBAL_data, indent=2);
	data_dict['corr_data'] = json.dumps(GLOBAL_corr_list)
	data_dict['node_data'] = json.dumps(GLOBAL_node_data, indent=2)
	data_dict['node_initial'] = json.dumps(GLOBAL_initial_nodes, indent=2)
	data_dict['subgraphs_data'] = json.dumps(GLOBAL_subgraphs_data)
	data_dict['dataset_name'] = json.dumps(datasetName)
	return render_template("frontend.html", data=data_dict)



@app.route("/getSelectedVariablesGraph/<variables>")
def getSelectedVariablesGraph(variables):
	print("APIString: ")
	print(variables)
	newDataFrame = pd.DataFrame()
	for curVariable in variables.split(","):
		print(curVariable)
		newDataFrame[curVariable] = GLOBAL_dataframe[curVariable]

	GetGraphData(newDataFrame)

	data_dict = {}
	data_dict['fdl_data'] = json.dumps(GLOBAL_data, indent=2);
	data_dict['corr_data'] = json.dumps(GLOBAL_corr_list)
	data_dict['node_data'] = json.dumps(GLOBAL_node_data, indent=2)
	data_dict['subgraphs_data'] = json.dumps(GLOBAL_subgraphs_data)
	return json.dumps(data_dict)

@app.route("/getSemopyEdgeFeedback/<variables>")
def getSemopyEdgeFeedback(variables):
	print("APIString2: ")
	print(variables)
	

	data_dict = {}

	edgeDict = {}
	inputEdges = variables.split(",")
	for edge in inputEdges:
		source = edge.split("-")[1]
		target = edge.split("-")[0]
		edgeDict[source] = edgeDict.get(source, "N/A") + "," + target

	SemopyString = """"""
	for key in edgeDict:
		SemopyString = SemopyString + "\n" + key + " ~ "
		for node in edgeDict[key].split(","):
			if(node == "N/A"):
				continue
			SemopyString = SemopyString + node + "+"

		SemopyString = SemopyString[:-1]
	print(SemopyString)
	SemopyModel = Model(SemopyString)

	SemopyModel.load_dataset(GLOBAL_dataframe)

	opt = Optimizer(SemopyModel)
	objective_function_value = opt.optimize()
	try:
		stats = gather_statistics(opt)
		print(stats)
		print(stats.bic)
		edgeDict["BIC"] = json.dumps(round(stats.bic, 3))
		edgeDict["CHI2"] = json.dumps(round(stats.chi2[0], 3))
		edgeDict["PVALUE"] = json.dumps(round(stats.cfi, 3))
		# edgeDict["PVALUE"] = json.dumps(stats.params[0].pvalue)
		edgeDict["RMSEA"] = json.dumps(round(stats.rmsea, 3))
	except:
		edgeDict["Chi2"] = json.dumps(-1)
		edgeDict["CHI2"] = json.dumps(-1)
		edgeDict["PVALUE"] = json.dumps(-1)
		edgeDict["RMSEA"] = json.dumps(-1)
		print('ERROR')
	return json.dumps(edgeDict)

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
	return ""

def GetGraphData(df):
	
	global GLOBAL_data
	global GLOBAL_subgraphs_data
	global GLOBAL_corr_list
	global GLOBAL_node_data

	pc.start_vm()
	GLOBAL_tetrad = s.tetradrunner()


	GLOBAL_tetrad.run(algoId = 'fges', dfs = df, scoreId = 'sem-bic', dataType = 'continuous',
		   maxDegree = -1, faithfulnessAssumed = True, verbose = True)
	GLOBAL_corr_list = corr_data.tolist()
	col = []
	for c in GLOBAL_dataframe.columns:
		col.append(c)

	all_links = []

	for i in range(len(col)):
		for j in range(len(col)):
			all_links.append({"source": col[i], "target": col[j], "value": GLOBAL_corr_list[i][j]})

	all_nodes = []
	for i in range(len(col)):
		all_nodes.append({"id": col[i], "group": 1})



	GLOBAL_node_data = GLOBAL_tetrad.getNodes()
	edge_dict = {}
	edge_data = GLOBAL_tetrad.getEdges()
	
	for e in edge_data:
		if(" --> " in e):
			pair = e.split(" --> ")	
			if pair[0] in edge_dict:	
				val_list = edge_dict.get(pair[0])
				val_list.append(pair[1])
				edge_dict[pair[0]] = val_list

			edge_dict[pair[0]] = [pair[1]]

	graph_links = []
	for link_dict in all_links:
		if (link_dict.get("source") in edge_dict) and (link_dict.get("target") in edge_dict.get(link_dict.get("source"))):
			graph_links.append(link_dict)
	GLOBAL_data = {"nodes": all_nodes, "links": graph_links}


	subgraphs = []
	i = 0
	while(len(subgraphs) < 5):
		subgraph = []
		while(len(subgraph) < 5):
			subgraph.append(GLOBAL_data['links'][i % len(GLOBAL_data['links'])])
			i = i+1
		subgraphs.append(subgraph)
	GLOBAL_subgraphs_data = subgraphs

if __name__ == "__main__":

	pc = pc()
	pc.start_vm()
	GLOBAL_tetrad = s.tetradrunner()

	# graph data from file							      
	GLOBAL_dataframe = pd.read_csv(datasetName)
	GLOBAL_initial_nodes = list(GLOBAL_dataframe.columns)
	GLOBAL_dataframe = GLOBAL_dataframe.dropna()
	corr_data = GLOBAL_dataframe.corr()
	corr_data = corr_data.to_numpy()
	GetGraphData(GLOBAL_dataframe)
	app.run(debug=True)