#snapshots_to_delete=$(aws ec2 describe-snapshots --owner-ids xxxxxxxxxxxx --query 'Snapshots[?StartTime<=`2017-02-15`].SnapshotId' --output text)

DAYS=30
OneMonthAgo=$(date -r $(( $(date '+%s') - 86400 * $DAYS )) +%Y-%m-%d)
echo $OneMonthAgo

OWNERID=$(aws sts get-caller-identity --output text --query 'Account' $*)

SNAPSHOTS_TO_DELETE=$(aws ec2 describe-snapshots --owner-ids $OWNERID --query "Snapshots[?StartTime<=\`$OneMonthAgo\`].SnapshotId" --output text $* )

for snap in $SNAPSHOTS_TO_DELETE ; do
    echo $snap
    aws ec2 delete-snapshot --snapshot-id $snap $*
done

