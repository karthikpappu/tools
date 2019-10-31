
delete_image ()
{
    ami=$1
    IMAGE_DESCRIPTION=$(aws ec2 describe-images --image-id $ami --profile connotate)
    CREATION_DATE=$(echo $IMAGE_DESCRIPTION | jq -r '.Images[0].CreationDate')
    CREATION_YEAR=$(echo $CREATION_DATE | cut -c 1-4)
    IMAGE_NAME=$(echo $IMAGE_DESCRIPTION | jq -r '.Images[0].Name')

    if ! [[ $IMAGE_NAME == "*Customer*" ]] && [ "${CREATION_YEAR}0" -lt "20180" ] ; then
        echo "$IMAGE_NAME,$CREATION_DATE,$ami"
        aws ec2 deregister-image --image-id $ami --profile connotate
    fi
}

export -f delete_image
cat /tmp/snapshots.ami | xargs -L1 -I{} bash -c ' delete_image "{}"' | tee /tmp/snapshots_images.csv
