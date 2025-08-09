Prevent Metadata Override
==============

In the npd_csviper process, the metadata json file determines how the csv file is mapped into the import, including the creation of later CREATE TABLE statements with column names etc. 

however, once this file has been modified, it frequently should no longer be overridden by the compile process. 

There should be a json value in the file called allow_recompile_to_overwrite = True which should be the first variable in the json file. 
The compile process should load the json file and when it sees that variable set to False, it should not do any more processing of the csv file to extract the data... 
And just stop. If the --trample parameters have been set, then they should be ignored.. the metadata file should still not be overwritten... 
Whic will make the metadata.json file the authoritative place which will determine if npd_csviper will overwrite it. 

However, if trample is set and the overwrite is prevented by this variable. Then the compiler should generate an error saying "You are asking me to trample but the metadata file is saying no". 

The csv metadata is a complex process.. but start looking in src/npd_csviper/metadata_extractor.py for where to make these modifcations.
