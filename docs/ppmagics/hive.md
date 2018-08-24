# Hive Magic

# About
Jupyter enables you to get started quickly on developing and running interactive hive sql queries using ppmagics. You can visualize your results as graphs and charts and share your reports.

# Getting Started <a id='getstart'></a>

Querying Hive
---

**Opening Notebook:** Open Jupyter Notebook, click `New` --> `Python3` kernel

**Import ppextensions :** Execute the code below to import ppmagics from ppextensions to your notebook
~~~
%load_ext ppextensions.ppmagics
~~~

**Using Hive magic**

To see available options for Hive Magic run `%hive?`:
```
%hive [-c CLUSTER_NAME] [-hs HIVE_SERVER] [-p PORT] [-nn NAME_NODE_URL]
            [-np NAME_NODE_OPTIONS] [-rm RESOURCE_MANAGER_URL] [-a AUTH]
            [-f CSV] [-t TABLE] [-df DATAFRAME] [-tab TABLEAU] [-pub PUBLISH]
            [-tde TDE_NAME] [-pname PROJECT_NAME]
```

```
optional arguments:
  -c CLUSTER_NAME, --cluster_name CLUSTER_NAME
                        Cluster Name to connect to
  -hs HIVE_SERVER, --hive_server HIVE_SERVER
                        Hive server2 host name or ip address.
  -p PORT, --port PORT  Hive Server2 port
  -nn NAME_NODE_URL, --name_node_url NAME_NODE_URL
                        Name node host name
  -np NAME_NODE_OPTIONS, --name_node_options NAME_NODE_OPTIONS
                        Parameters for host
  -rm RESOURCE_MANAGER_URL, --resource_manager_url RESOURCE_MANAGER_URL
                        Resource Manager web ui url
  -a AUTH, --auth AUTH  Authentication type
  -f CSV, --csv CSV     Local CSV file name to be loaded to hive table. Use
                        this option along with --table
  -t TABLE, --table TABLE
                        Hive table name for data to be inserted to. Use this
                        option along with --csv
  -df DATAFRAME, --dataframe DATAFRAME
                        DataFrame to be uploaded to a table. Use this option
                        with --table
  -tab TABLEAU, --tableau TABLEAU
                        True to download tableau data
  -pub PUBLISH, --publish PUBLISH
                        Publish Data to Tableau Server
  -tde TDE_NAME, --tde_name TDE_NAME
                        tde Name to be published
  -pname PROJECT_NAME, --project_name PROJECT_NAME
                        project name to be published
```

**Running Hive query:** 

Establishing a hive server connection to read data from hive 
```
%%hive -c <cluster_name>
<your sql code line1>
```

Update `~/.ppextensions/config.json` with a named cluster including `hive url`, `port number` and `auth` to use `-c` if a persistent cluster configuration is desired.

```
{
  "hive":{
    "cluster_name": {
            "host": <hostname>,
            "port": <port_number>,
            "auth": "plain/gssapi",
        }
    "cluster_name_1": {
            "host": "<hostname">,
            "port": <port_number>,
            "auth": "plain/gssapi",
        }
     }
}
```
For [reading and inserting data](#insert_data) additional configuration is required.

****Updated config will be available after restarting the kernel***


Optionally, it is also possible to connect without a config
  
```buildoutcfg
%%hive --hive_server hive.server.com --port 10000 --auth gssapi
 <your one-line sql code>
```
 
On an established hive server connection further queries can be run as:
 
hive sql in one-line mode: 
~~~~
%hive <your one-line sql code>
~~~~

hive sql in multi-line mode: 
~~~~
%%hive
<your sql code line1>
<your sql code line2>
<your sql code lineN>
~~~~



 **To insert csv/df data to a Hive table**<a id='insert_data'></a>
    
    %hive -f file.csv -t database.table_name
    
    %hive -df df_name -t database.table_name


Update `~/.ppextensions/config.json` with `name_node_url` and `name_node_opts` for the desired cluster to insert and read data 
```
{
  "hive":{
    "cluster_name": {
            "host": <hostname>,
            "port": <port_number>,
            "auth": "plain/gssapi",
            "resource_manager_url": "url_name",
            "name_node_url": "namenodeurl:port",
            "name_node_opts": {"hadoop.security.authentication": "kerberos"}
            }
      }
   }

```

Optionally, it is also possible to connect for inserting/reading without a config
```buildoutcfg
%%hive --hive_server hive.server.com --port 10000 --auth gssapi --name_node_url hive.server.com --name_node_opts {"hadoop.security.authentication": "kerberos"}
<your sql code>
```



    
    
   **Publish to tableau**
   
    %hive --tableau True --publish True --tde_name <tde> --project_name <pname>
    select * from database.table_name limit 10
    
   
   
  
   ******For tableau configuration refer to [Publish Magic](https://github.paypal.com/ppextensions/master/docs/ppextensions-magics/publish.md)******
   
   %hive <query>
```
Please check the official [Hive documentation] (https://hive.apache.org/) for information on using Hive.