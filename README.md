# What is this?
These few scripts fetch the covid-19 infection data for germany and generate a HTML page that shows a more or less nice graph. It's designed to be placed on a webserver somewhere, but you can put it on your local disk - it will run just as smooth. The fetchdata script will issue at least 413 queries each run to the arcgis server. This may can be done better with a more intelligent query, you're free to suggest one :-)

# Execute
Just run processdata.sh shellscript.

# Create a cronjob
You can run the create-cronjob.sh shellscript to create a cronjob.

# See it in action
You can see it in action at https://eholtz.de/covid19

