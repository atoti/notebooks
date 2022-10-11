# Insurance - Customer 360

This use case demonstrates how we can perform customer 360 with mock insurance data.  
There are 3 notebooks in this use case:

1. [01-Dataupload-to-Vertica.ipynb](01-Dataupload-to-Vertica.ipynb)

This notebook shows how CSV files can be loaded into the Vertica database and how we can download data from Vertica database into CSV.

2. [02-main-vertica-db.ipynb](02-main-vertica-db.ipynb)

This notebook connects to the Vertica database and creates a multidimensional data cube.  

3. [03-main-csv.ipynb](03-main-csv.ipynb)

This notebook demonstrates the same analysis as [02-main-vertica-db.ipynb](02-main-vertica-db.ipynb), however with CSV as the main datasource. _Use this notebook if you are interested in the use case but do not have a Vertica database_.  

Alternatively, you can update [01-Dataupload-to-Vertica.ipynb](01-Dataupload-to-Vertica.ipynb) to insert the data into other databases, simply by changing the sqlalchemy dialect. Then modify [02-main-vertica-db.ipynb](02-main-vertica-db.ipynb) to use the correct JDBC URL. 