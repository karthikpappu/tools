# Install EFS volumes
#
# Needs sudo

yum install -y amazon-efs-utils nfs-utils

get_EFSID()
{
    VOL=$1
    [ $VOL = "efs-lightning-staging" ] && EFSID=fs-7366d93a
    [ $VOL = "efs-lightning-encrypted-staging" ] && EFSID=fs-4f9d4f07

}

run_cmd()
{
    CMD=$*
    echo $CMD
    [ $DRURUN = "TRUE" ] && $CMD
}

mount_efs()
{
    VOL=$1
    get_EFSID $VOL

    if [ $VOL = "efs-lightning-staging" ]; then
        [ ! -d /mnt/efs-lightning-staging ] && mkdir /mnt/efs-lightning-staging
        mount -t efs fs-7366d93a:/ /mnt/efs-lightning-staging
    if [ $VOL = "efs-lightning-encrypted-staging" ]; then
        [ ! -d /mnt/efs-lightning-encrypted-staging ] && mkdir /mnt/efs-lightning-encrypted-staging
        mount -t efs fs-4f9d4f07:/ /mnt/efs-lightning-encrypted-staging
    fi

}

mount_efs $1
