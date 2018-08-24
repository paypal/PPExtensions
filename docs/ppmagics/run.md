# Run Magic



# About
The Run Magic enables sequential or parallel execution of notebooks. Additionally, notebooks can include parameters to enable parameterized execution; parameters are assumed to be present in the first code cell of the notebook.  
# Getting Started <a id='getstart'></a>
**Opening Notebook:** Open Jupyter Notebook, click `New` --> `Python3` kernel

**Import ppextensions :** Execute the code below to import ppmagics from ppextensions to your notebook
~~~
%load_ext ppextensions.ppmagics
~~~

**Using Run magic**

To see available options for Run Magic run `%run?`:
```
%run [-p PARALLEL] [-e ALLOW_ERRORS] [-pbar ENABLE_PROGRESS_BAR]
           [-t CELL_TIMEOUT]
```
```
optional arguments:
  -p PARALLEL, --parallel PARALLEL
                        Run Notebooks in Parallel
  -e ALLOW_ERRORS, --allow_errors ALLOW_ERRORS
                        Ignore errors and execute whole notebook
  -pbar ENABLE_PROGRESS_BAR, --enable_progress_bar ENABLE_PROGRESS_BAR
                        Show Progress Bar
  -t CELL_TIMEOUT, --cell_timeout CELL_TIMEOUT
                        Cell Execution Timeout. -1 to Disable.
```

Multiple notebooks should be separated with a `;`. If a notebook execution should be saved, the save name can be specified with the run notebook separated by a `:`.


One or more parameters can be specified while executing a parameterized notebook. If a parameter specified during run does not exist in the notebook it will be ignored. All parameters should be part of the first code cell. Parameters can be strings, numbers, lists and dictionaries.

Below are different ways to use the Run Magic.         

```
# simple run
%run your notebook
```
```
# Save execution after run
%run your notebook:your save notebook
```
```                
# Allow errors during execution of cells
%%run -e True
your notebook
```
```
# sequential run   
%%run
your notebook 01;
your notebook 02
```
```
# parallel run 
%%run -p True
your notebook 01;
your notebook 02
```
```
# Show progress bar during execution of notebook
%%run -pbar True
your notebook
```
```
# specify cell timeout in seconds, -1 to disable cell timeout
%%run -t 600
your notebook 01;
your notebook 02
```
```
# parameterized run                
%%run
your notebook with prameters 01 key01=int key01=string key02={'key01': param01};
your notebook with paramters 02 key01=int key02=string key03=[param01, param02];
your notebook with parameters 01
```
