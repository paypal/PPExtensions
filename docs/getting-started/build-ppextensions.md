## Install 
```buildoutcfg
pip install ppextensions
```
## Try ppextensions
```
%load_ext ppextensions.ppmagics
```

Try help to see all the available options
```buildoutcfg
%%help?
```

| Magic               | Usage          | Explanation                                                                                                                    |
|---------------------|----------------|--------------------------------------------------------------------------------------------------------------------------------|
| hive                | %hive?         | Connects to hive engine. Hive magic also gives options to insert csv/dataframe to teradata and publishing data to tableau.     |
| teradata            | %teradata?     | Connects to teradata engine. Teradata magic also gives has to insert csv/dataframe to teradata and publishing data to tableau. |
| presto              | %presto?       | Connects to presto engine. Presto magic also has options to publishing data to tableau.                                        |
| Spark Thrift Server | %sts?          | Connects to Spark Thrift Server. Sts magic also has options to publishing data to tableau.                                     |
| CSV                 | %csv?          | Runs sqls on top of csv files. CSV magic also has options to publishing data to tableau.                                       |
| run                 | %run?          | Runs a notebook from another notebook. Allows for running parameterized notebooks.                                             |
| run_pipeline        | %run_pipeline? | Run notebooks sequentially in a stateful Pipeline.                                                                             |


For more info:
[Github Link](git@github.com:paypal/PPExtensions.git)
