import boto3 

session = boto3.Session(profile_name='default')

db_client = session.client('dynamodb')

def list_tables():
    response = db_client.list_tables()
    return response.get('TableNames', [])

if __name__ == "__main__":
    print(list_tables())