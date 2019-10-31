BUCKETS=import-s3-buckets-20191023.log

while read bucket ; do
    echo $bucket
    aws s3api delete-bucket-analytics-configuration --id storage_analysis --bucket $bucket
done < $BUCKETS
