# Publish Magic </a>

# Prerequisites

Install  [tableau sdk](https://onlinehelp.tableau.com/current/api/sdk/en-us/help.htm#SDK/tableau_sdk_installing.htm%3FTocPath%3D_____3)

# About
Jupyter enables you to publish your data to online tableau server. 
Publish magic allows you to publish the dataframe or result from any query to  online tableau server.

Note: You will need [tabcmd](https://onlinehelp.tableau.com/current/server/en-us/tabcmd.htm) installed and an [online account](https://www.tableau.com/learn/tutorials/on-demand/publishing-tableau-server-and-tableau-online-9) to use this feature


# Getting Started <a id='getstart'></a>

Publish Magic
---

**Opening Notebook:** Open Jupyter Notebook, click `New` --> `Python3` kernel

**Import ppextensions :** Execute the code below to import ppmagics from ppextensions to your notebook
~~~
%load_ext ppextensions.ppmagics
~~~

**Using Publish magic**

To see available options for Publish Magic run `%publish?`:
```
%publish [-tde TDE_NAME] [-p_name PROJECT_NAME]
```

```
 optional arguments:
  -tde TDE_NAME, --tde_name TDE_NAME
                        tde Name to be published
  -p_name PROJECT_NAME, --project_name PROJECT_NAME
                        tde Name to be published
```

**Running Publish Magic:** 

```
%%publish -tde_name <tde> 
<df_name>
```

Update `~/.ppextensions/config.json` with the tableau server details including `site_name`, `user_name` and `password` .

```
{ "tableau":{
           "site_name":"<tableau_website",
           "user_name":"",
            "password": ""
           }
   }
```

****Updated config will be available after restarting the kernel***


 If you do not provide the info in config, you would be prompted to input the information
  
**Publishing with out specific tde name**

~~~~
%publish  <df_name>
~~~~
dataframe would be published with default timestamp


**Publishing  to specific project with specific tde name**

    %%publish --project_name <pname> --tde_name <tde>
    <df_name>


**Publishing results from another magic.

```buildoutcfg
%publish %hive <query>
```
```
%%publish  --tde_name <tde>
%hive <query>
```
Please check the official [Tableau documentation] (https://onlinehelp.tableau.com/current/pro/desktop/en-us/help.htm#concepts.html) for information on using Tableau.