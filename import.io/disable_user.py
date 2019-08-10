import boto3
import sys
import argparse

def IAMUser(iam, name):
    # Search through all users
    matches = []
    for user in iam.users.all():
        if name in user.name:
            matches.append(user)
    # Find the right user
    if len(matches) == 0:
        print (f"Can't find this user '{name}'")
        user = None
    elif len(matches) == 1:
        print (f"Found user {matches[0].name}")
        user = matches[0]
    else:
        print("Found more than 1, please refine the search")
        print([u.name for u in matches])
        user = None
    return user

# TODO check IAM permission

# parse cli to get user name
parser = argparse.ArgumentParser(description='Disable user')
parser.add_argument('username')
args = parser.parse_args()

# Get the exact user name
iam = boto3.resource('iam')
user = IAMUser(iam, args.username)
if not user:
    sys.exit(1)

# Disable Console password
print("Console password ...")
login_profile = iam.LoginProfile(user.name)
try:
    login_profile.delete()
    print("  disabled console access")
except:
    print("  maybe already disabled")

# Deactive all access keys
print("Access Keys ...")
for ak in user.access_keys.all():
    if ak.status != "Inactive":
        try:
            ak.deactivate()
            print(f"  {ak.id} disabled")
        except Exception as e:
            print(f"  {ak.id} disabling encounter error")
    else:
        print(f"  {ak.id} is already {ak.status}")

# remove MFA devices
print("MFA Devices ...")
for mfa in user.mfa_devices.all():
    try:
        mfa.disassociate()
    except Exception as e:
        print(e)
    print("  removed MFA device")

# remove groups
print("Groups ...")
for group in user.groups.all():
    try:
        group.remove_user(UserName=user.name)
    except Exception as e:
        print(e)
    print(f"  removed from group {group.name}")

# detach policies
print("Policies ...")
for policy in user.attached_policies.all():
    try:
        policy.detach_user(UserName=user.name)
    except Exception as e:
        print(e)
    print(f"  detached policy {policy.policy_name}")

# TODO ask if need to delete the account
