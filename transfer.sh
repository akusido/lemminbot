#!/bin/bash
rsync -qaW --inplace --remove-source-files --exclude="*.iowait" /tmp/rsyncing/ /media/frames
EILEN=$(date --date="-1 day" +"%Y%m%d")
cd /media/frames/${EILEN}/
tar cjf weather-${EILEN}.tar.bz2 weather/*.json
rm -r weather/
cd /media/frames/
rsync -qaW --password-file /path/to/key --skip-compress=jpg 2017* rsync://user@destination/folder
exit 0

# Note: for best results, this script
# should run nightly after 00:00 UTC!