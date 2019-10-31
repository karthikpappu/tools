find . -type f -mtime +30 -exec rm -f {} \;
find . -type d -empty -delete
#find . -type d -mtime +30 -exec rmdir -f {} \;
