How to run the tool:
-Extract the CausalGame.zip file's contents
-Go to the folder containing "backend.py" and open command prompt
-Enter "python backend.py"
-Once the localhost is up and running, go to a web browser (preferably Google Chrome) and enter the following URL:
-http://127.0.0.1:5000/

Environment tested on:
Python version: 3.7.4
Operating System: Windows 10

Python packages required:
-kaggle
-json
-pandas
-numpy
-flask
-os
-zipfile
-pycausal (requires the following packages: pydot, javabridge, GraphViz, pydot, numpy, pandas)
-Semopy (1.1.2) 


Javabridge installation steps: 
1. install C compiler on system (python and jdk "bit" should be same, that is x64+x64, or x84+x84)
2. open 'x64 Native Tools Command Prompt for VS 2019' and enter the commands 3 and 4:
3. set MSSdk=1
4. set DISTUTILS_USE_SDK=1
5. in the same cmd window, enter "pip install javabridge"