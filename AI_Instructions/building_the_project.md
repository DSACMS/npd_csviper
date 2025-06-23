

Please read the AI_Instructions/core_design.md to understand the final design of the project. 

We have successfully created the a working prototype of all the steps. Now lets make the following improvements.
Lets complete these tasks one at a time. Focus only on the top item on this list until it is complete. .

* Add a new stage of the sql import process that happens after data upload, which is the "post_import_sql" stage. This will allow for tasks like data calculations, indexing and data transformations to occur. This should take the form of a new directory, full of numerically ordered SQL files, using the REPLACE_ME_DATABASE_NAME and REPLACE_ME_TABLE_NAME templating approach. Look in ./nppest2/post_import_sql/nppes_npidata_21f8c89f23754346123596e3f6c66417 for an example. When the numeric prefix of the files are the same, then can be run in an order, larger numbers should be run later on. So all of the 01_something steps, should complete before the 05_something steps, which are in front of the 12_something steps etc.
* Create a single csviper command that is a gateway to the others. Lets call this step the 'full_compile' version.
* Currently src/csviper/mysql_import_script_generator.py and src/csviper/postgresql_import_script_generator.py and also src/csviper/postgresql_schema_generator.py and src/csviper/mysql_schema_generator.py are violating DRY principles by having large parts of overlapping functionality. Starting with the schema generators, lets pull as much of the logic as possible into a parent class (still prefering static methods throughout). This should result having three files for each stage instead of two, where the general case is handled in the parent and only the differences between MySQL and PostGreSQL are implemented in the database specific scripts.
* Currently csviper is mostly a package that is focused on being a CLI tool. However, the most of the functions in the generated go.postgresql.py and go.mysql.py should be moved into a single static class, which can then be imported into the respective scripts. This will make the resulting go scripts simply the place where all of the components of the import process are tied together, in a script that might eventually be used to include per-data import tweaks and special features.
* At each stage of the process, there should be the capacity to tweak the auto-generated output, and have that not be overwritten by subsequent runs of the tool-chain. Specifically:
* For the metadata generation, the system should use the hash on the column headers to determine if the signature of the metadata is the same. When the headers change.. there should actually be a new metadata file generated.. but otherwise the last version should be used. This will allow for manual tweaks to the metadata model, especially how database friendly versions of column names to be re-interpreted.
* The same approach should happen for the md5 signatures of the generated SQL. Assuming the same SQL would be generated, the file contents should be loaded instead, this will allow for additions in the SQL sequence to apply including adding indexes or calculating intermediate tables differently.  


