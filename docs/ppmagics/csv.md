# CSV Magic

# About
Jupyter enables you to get started quickly on developing and running interactive queries on csv using ppmagics. You can visualize your results as graphs and charts and share your reports.

# Getting Started <a id='getstart'></a>

Querying CSV
---

**Opening Notebook:** Open Jupyter Notebook, click `New` --> `Python3` kernel

**Import ppextensions :** Execute the code below to import ppmagics from ppextensions to your notebook
~~~
%load_ext ppextensions.ppmagics
~~~

**Using CSV magic**

To see available options for CSV Magic run `%csv?`:
```

  %csv [-tab TABLEAU] [-pub PUBLISH] [-tde TDE_NAME] [-pname PROJECT_NAME]
  ```


Note: Currently csv magic supports only select sqls and ```return: Dataframe```
```
optional arguments:
  -tab TABLEAU, --tableau TABLEAU
                        True to download tableau data
  -pub PUBLISH, --publish PUBLISH
                        Publish Data to Tableau Server
  -tde TDE_NAME, --tde_name TDE_NAME
                        tde Name to be published
  -pname PROJECT_NAME, --project_name PROJECT_NAME
                        project name to be published
```

**Running CSV query:** 

csv sql in one-line mode: 
~~~~
%csv <your one-line sql code>
~~~~

csv sql in multi-line mode: 
~~~~
%%csv
<your sql code line1>
<your sql code line2>
<your sql code lineN>
~~~~

```buildoutcfg
Example Queries:
1. select * from test.csv
2. select col1 from test.csv where col1=1
3.select * from test.tsv
```    


   **Publish to tableau**
   
    %csv --tableau True --publish True --tde_name <tde> --project_name <pname>
    select * from database.table_name limit 10
    

  
   ******For tableau configuration refer to [Publish Magic]()******