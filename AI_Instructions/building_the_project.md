

Please read the AI_Instructions/core_design.md to understand the final design of the project. 

We have successfully created the a working prototype of all the steps. Now lets make the following improvements.
Lets complete these tasks one at a time. Focus only on the top item on this list until it is complete. .

* Currently src/csviper/mysql_import_script_generator.py and src/csviper/postgresql_import_script_generator.py and also src/csviper/postgresql_schema_generator.py and src/csviper/mysql_schema_generator.py are violating DRY principles by having large parts of overlapping functionality. Starting with the schema generators, lets pull as much of the logic as possible into a parent class (still prefering static methods throughout). This should result having three files for each stage instead of two, where the general case is handled in the parent and only the differences between MySQL and PostGreSQL are implemented in the database specific scripts.
* Currently csviper is mostly a package that is focused on being a CLI tool. However, the most of the functions in the generated go.postgresql.py and go.mysql.py should be moved into a single static class, which can then be imported into the respective scripts. This will make the resulting go scripts simply the place where all of the components of the import process are tied together, in a script that might eventually be used to include per-data import tweaks and special features.
* At each stage of the process, there should be the capacity to tweak the auto-generated output, and have that not be overwritten by subsequent runs of the tool-chain. Specifically:
* For the metadata generation, the system should use the hash on the column headers to determine if the signature of the metadata is the same. When the headers change.. there should actually be a new metadata file generated.. but otherwise the last version should be used. This will allow for manual tweaks to the metadata model, especially how database friendly versions of column names to be re-interpreted.
* The same approach should happen for the md5 signatures of the generated SQL. Assuming the same SQL would be generated, the file contents should be loaded instead, this will allow for additions in the SQL sequence to apply including adding indexes or calculating intermediate tables differently.  


