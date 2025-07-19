Support test mode
====================

The ImportExecutor.execute_postgresql_import now supports a test mode. 

And also now requires named parameters. Lets modify src/csviper/postgresql_import_script_generator.py

So use the named parameters in the code it generates, but also support test mode as a pass-through. So that for go.postgresql.py when you pass it import_only_lines as an argument..
it passes this along to the execute_postgresql_import command. Check to make sure that the new argument is a whole positive number. 
