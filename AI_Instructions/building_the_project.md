

Please read the AI_Instructions/core_design.md to understand the final design of the project. 

We have successfully created the metadata extraction phase. Now we need to handle the next steps. 

Look again at ../nppest2/CSVRawImport.py which demonstrated how to build the CREATE TABLE files for the given csv file.

When we accept the output_dir argument for this stage, lets automatically create a sub-directory in that folder called cache_create_table_sql to save our work. 
Take a look at ../nppest2/cache_create_table_sql/ to see some of the files that we created with MD5 strings in that folder and then renamed. 
The new script should handle the md5 creation and name support in the same way as CSVRawImport whereever possible. 


