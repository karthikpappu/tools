
get_asg_info()
{
    ASGLOG="asg.log"
}

get_instance_type()
{
    LC=$1
    LC_DESC=$(aws autoscaling describe-launch-configurations --launch-configuration-names $LC)
    INSTTYPE=$(echo $LC_DESC | jq -r '.LaunchConfigurations[0].InstanceType')
    echo "$INSTTYPE"
}

get_instance_type $1
