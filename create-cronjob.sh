#!/bin/bash

cronfile="/etc/cron.daily/fetch-rki-covid-archive.sh"

[ -f $cronfile ] && echo "Cronfile $cronfile is already present. Exiting." && exit 1

if touch $cronfile &>/dev/null ; then
  echo "#!/bin/bash" > $cronfile
  echo "cd $(pwd)" >> $cronfile
  echo "./processdata.sh" >> $cronfile
else
  echo "Could not place $cronfile (no permissions?). You could run crontab -e and insert the following line:"
  echo "$(($RANDOM%60)) $(($RANDOM%24)) * * * $(readlink -f processdata.sh)"
fi

