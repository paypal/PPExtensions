# Presto Magic

# About
Jupyter enables you to get started quickly on developing and running interactive presto sql queries using ppmagics. You can visualize your results as graphs and charts and share your reports.

# Getting Started <a id='getstart'></a>

Querying Presto
---

**Opening Notebook:** Open Jupyter Notebook, click `New` --> `Python3` kernel

**Import ppextensions :** Execute the code below to import ppmagics from ppextensions to your notebook
~~~
%load_ext ppextensions.ppmagics
~~~

**Using Presto magic**

To see available options for Presto Magic run `%presto?`:
```
  %presto [-c CLUSTER_NAME] [-h HOST] [-p PORT] [-a AUTH] [-tab TABLEAU]
              [-pub PUBLISH] [-tde TDE_NAME] [-pname PROJECT_NAME]
```

```
optional arguments:
  -c CLUSTER_NAME, --cluster_name CLUSTER_NAME
  -h HOST, --host HOST  Host name or ip address of presto server
  -p PORT, --port PORT  Port of presto server
  -a AUTH, --auth AUTH  Authentication type
  -tab TABLEAU, --tableau TABLEAU
                        True to download tableau data
  -pub PUBLISH, --publish PUBLISH
                        Publish Data to Tableau Server
  -tde TDE_NAME, --tde_name TDE_NAME
                        tde Name to be published
  -pname PROJECT_NAME, --project_name PROJECT_NAME
                        project name to be published
```

**Running Presto query:** 

Establishing a presto server connection to read data from presto 
```
%%presto -c <cluster_name>
<your sql code line1>
```

Update `~/.ppextensions/config.json` with a named cluster including `presto url`, `port number` and `auth` to use `-c` if a persistent cluster configuration is desired.

```
{
  "presto":{
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
****Updated config will be available after restarting the kernel***


Optionally, it is also possible to connect without a config
  
```buildoutcfg
%%presto --host presto.server.com --port 10000 --auth gssapi
 <your one-line sql code>
```
 
On an established presto server connection further queries can be run as:
 
presto sql in one-line mode: 
~~~~
%presto <your one-line sql code>
~~~~

presto sql in multi-line mode: 
~~~~
%%presto
<your sql code line1>
<your sql code line2>
<your sql code lineN>
~~~~


   **Publish to tableau**
   
    %presto --tableau True --publish True --tde_name <tde> --project_name <pname>
    select * from database.table_name limit 10
    
   
   
  
   ******For tableau configuration refer to [Publish Magic]()******