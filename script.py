import boto3 

session = boto3.Session(profile_name='default')

rds_client = session.client('rds')

def list_rds_instances():
    response = rds_client.describe_db_instances()
    instances = response['DBInstances']
    for instance in instances:
        print(f"DB Instance Identifier: {instance['DBInstanceIdentifier']}, DB Instance Class: {instance['DBInstanceClass']}, Engine: {instance['Engine']}")
    return instances


if __name__ == "__main__":
    list_rds_instances()