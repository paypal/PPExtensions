# Run Pipeline Magic



# About
The run_pipeline magic enables sequential stateful execution of notebooks. Additionally, notebooks can include parameters to enable parameterized execution; parameters are assumed to be present in the first code cell of the notebook.

The magic creates a dictionary `_pipeline_workspace` which will be avaliable to all the notebooks in the pipeline during execution. The dictionary is intended to store state. It can contain any python object. Managing and communicating state changes can be achieved using parameterization of notebooks.   
# Getting Started <a id='getstart'></a>
**Opening Notebook:** Open Jupyter Notebook, click `New` --> `Python3` kernel

**Import ppextensions :** Execute the code below to import ppmagics from ppextensions to your notebook
~~~
%load_ext ppextensions.ppmagics
~~~

**Using run_pipeline magic**

To see available options for run_pipeline magic run `%run_pipeline?`:
```
%run_pipeline [-t CELL_TIMEOUT]
```
```
optional arguments:
  -t CELL_TIMEOUT, --cell_timeout CELL_TIMEOUT
                        Cell Execution Timeout. -1 to Disable.
```

Multiple notebooks should be separated with a `;`. If a notebook execution should be saved, the save name can be specified with the run notebook separated by a `:`.


One or more parameters can be specified while executing a parameterized notebook. If a parameter specified during run does not exist in the notebook it will be ignored. All parameters should be part of the first code cell. Parameters can be strings, numbers, lists and dictionaries.

Below are different ways to use the run_pipeline Magic.
```
# simple pipeline
%%run_pipeline
first notebook in pipeline;
second notebook in pipeline;
third notebook in pipeline
```
```
# simple pipeline with saving execution
%%run_pipeline
first notebook in pipeline:savename for first notebook;
second notebook in pipeline:savename for third notebook;
third notebook in pipeline:savename for third notebook
```

```
# pipleine with parameterized notebooks
%%run_pipeline
first notebook in pipeline  key01=int key01=string key02={'key01': param01};
second notebook in pipeline;
third notebook in pipeline:your save name key01=int key02=string key03=[param01, param02]         
```

```
# specify cell timeout in seconds, -1 to disable cell timeout
%%run_pipeline --cel_timeout 600
first notebook in pipeline  key01=int key01=string key02={'key01': param01};
second notebook in pipeline;
third notebook in pipeline:your save name key01=int key02=string key03=[param01, param02]         
```

```
# An example of using state
"""
The first notebook downloads data to a dataframe and saves it to _pipeline_workspace as a key specified by the user as a paramter.
The second notebook takes the key containing data in _pipeline_workspace as a paramter and visualizes the data
"""

%%run_pipeline
download data notebook save_key_name="data_key";
visualize data notebook:save name data_key="data_key"         
```