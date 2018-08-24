# Teradata Magic


#About
Jupyter enables you to get started quickly on developing and running interactive sql queries on Teradata using ppmagics. You can visualize your results as graphs and charts and share your reports.

# Getting Started <a id='getstart'></a>

Querying Teradata
---

**Opening Notebook:** Open Jupyter Notebook, click `New` --> `Python3` kernel

**Import ppextensions :** Execute the code below to import ppmagics from ppextensions to your notebook
~~~
%load_ext ppextensions.ppmagics
~~~
**Using Teradata magic**

To see available options for Hive Magic run `%teradata?`:
```
%teradata [-c CLUSTER_NAME] [-f CSV] [-t TABLE] [-df DATAFRAME]
                [-h HOST] [-tab TABLEAU] [-pub PUBLISH] [-tde TDE_NAME]
                [-pname PROJECT_NAME]
```
```
optional arguments:
  -c CLUSTER_NAME, --cluster_name CLUSTER_NAME
                        Cluster Name to connect to
  -f CSV, --csv CSV     Local CSV file name to be loaded to hive table. Use
                        this option along with --table
  -t TABLE, --table TABLE
                        Teradata table name for data to be inserted to. Use this
                        option along with --csv
  -df DATAFRAME, --dataframe DATAFRAME
                        DataFrame to be uploaded to a table. Use this option
                        with --table
  -h HOST, --host HOST  Teradata host name to connect to
  -tab TABLEAU, --tableau TABLEAU
                        True to download tableau data
  -pub PUBLISH, --publish PUBLISH
                        Publish Data to Tableau Server
  -tde TDE_NAME, --tde_name TDE_NAME
                        tde Name to be published
  -pname PROJECT_NAME, --project_name PROJECT_NAME
                        project name to be published
```

**Running Teradata query:** 
Establishing a connection to Teradata
```
%%teradata -c <cluster_name>
<your sql code line1>
```

Update `~/.ppextensions/config.json` with named cluster including `host` if a persistent cluster configuration is desired.

```
"teradata": {
  "cluster_name": {
            "host": <host_name>
        },
  "cluster_name_1": {
            "host": <host_name>
        }
}
```

****Updated config will be available after restarting the kernel***


Optionally, it is also possible to connect without a config
  
```buildoutcfg
%%teradata --host <host_name>
 <your one-line sql code>
```

On an established Teradata connection further queries can be run as:


Teradata sql in one-line mode 
~~~~
%teradata <your one-line sql code>
~~~~
To run Teradata sql in multi-line mode 
~~~~
%%teradata
<your sql code line1>
<your sql code line2>
<your sql code lineN>
~~~~

**To insert csv/df data to Teradata**<a id='insert_data'></a>
    
    %teradata -f file.csv -t database.table_name
    
    %teradata -df df_name -t database.table_name

**Publish to tableau**
   
    %teradata --tableau True --publish True --tde_name <tde> --project_name <pname>
    select * from database.table_name limit 10
      
******For tableau configuration refer to [Publish Magic]()******

Please check the official [Teradata documentation] (https://www.info.teradata.com/browse.cfm) for information on using Teradata.