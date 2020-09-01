TDCtoKML
--------
Python program to convert TDC Wholesale DSL net data excel to KML

Why?
----
TDCtoKML is made to generate an KML file from an spreadsheet found on the [TDC wholesale](https://wholesale.tdc.dk) website for all TDC centraloffices.

How?
----
Place the spreadsheet in the directory, called 0214_Wholesale_DSL_net_data_{date}.xsls

Run TDCtoKML ```./tdctokml.py -d -i 0214_Wholesale_DSL_net_data_04082020.xlsx``` 

if no output file is given it will output as tdc.kml.
On my laptop it takes about 10 minutes to run through all the sites.
