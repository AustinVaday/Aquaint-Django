import gc
import json

import pymysql
import boto3
import awsconfig
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
import time
from datetime import datetime
import calendar
import timeline
#import sqlconf

import collections
import decimal

import socket, errno

DYNAMO_MAX_BYTES = 3500
USER_TABLE = 'aquaint-users'
ACCESS_ID = awsconfig.aws_access_key_id
ACCESS_KEY = awsconfig.aws_secret_access_key

class DynamoUser:
    username=""
    realname=""
    accounts=[]
    isprivate=0 

# Return unix timestamp UTC time
def get_current_timestamp():
    utc = datetime.utcnow()
    return calendar.timegm(utc.utctimetuple())

# Instantiate DynamoDB connection
def dynamo_table(table_name):
    return boto3.resource(
        'dynamodb',
        aws_access_key_id=ACCESS_ID,
        aws_secret_access_key=ACCESS_KEY,
        region_name='us-east-1'
    #return boto3.client('dynamodb', region_name='us-east-1'
    ).Table(table_name)

# Scan DynamoDB table for field and handle oversized reads
def dynamo_scan(table, field):
    ret = []
    last_key = None
    
    while True:
        opts = { 'ProjectionExpression': field }
        if last_key is not None:
            opts.update({'ExclusiveStartKey': last_key})
        
        result = table.scan(**opts)
        
        # Join arrays from multiple reads
        ret += map(
            lambda item: item[field],
            result['Items']
        )
        
        # Handle oversized read
        if 'LastEvaluatedKey' in result:
            last_key = result['LastEvaluatedKey']
        else:
            break
    
    return ret

# Fetch event list for user
def read_eventlist(db, user):
    # Get raw data
    response = db.get_item(Key={ 'username': user })
    
    # No Events handler
    if 'Item' not in response: return []
    
    # Convert raw data to Event objects
    events = response['Item']['newsfeedList']
    return map(
        lambda event: timeline.Event.from_dynamo(user, event),
        events
    )

## Fetch notificaiton-timestamp for user
#def read_eventlist_notif(db, user):
#    # Get raw data
#    response = db.get_item(Key={ 'username': user })
#    
#    # No Events handler
#    if 'Item' not in response: return 0 
#    
#	# If no notificationTimestamp, we create one. 
#    if 'notificationTimestamp' not in response['Item']:
#        write_eventlist_notif(db, user, 0)	
#        return 0
#
#    # Convert raw data to integer val 
#    return response['Item']['notificationTimestamp']

# Get all user data from dynamo
def read_user_dynamo_data(db, user):
    # Get raw data
    response = db.get_item(Key={ 'username': user })
    
    # No Events handler
    if 'Item' not in response: return [] 
     
    # If no username, we're getting wrong data 
    if 'username' not in response['Item']: return []

    data = DynamoUser()
    data.username = user
    if 'realname' in response['Item']:
        data.realname = response['Item']['realname'] 
    if 'accounts' in response['Item']:
        data.accounts = response['Item']['accounts'] 
    if 'isprivate' in response['Item']:
        data.isprivate= response['Item']['isprivate'] 

    # return dynamo data in a selfmade class object
    return data 

## Instantiate MySQL connection
#def mysql_db():
#    return pymysql.connect(
#        sqlconf.endpoint,
#        sqlconf.username,
#        "",
#        sqlconf.dbname
#    ).cursor()
    
## Get followees for user
#def get_followees(cursor, user):
#    cursor.execute(
#        'SELECT followee FROM username_follows WHERE follower = %s;',
#        (user)
#    )
#    return map(
#        lambda row: row[0],
#        cursor.fetchall()
#    )

## Get all followers of user after a particular point in time
## Note that we do not include followers that were user-approved. This will be separate
#def get_recent_public_follows(cursor, user, start_timestamp):
#    cursor.execute(
#        'SELECT follower FROM username_follows WHERE followee = %s AND ' + \
#        'UNIX_TIMESTAMP(timestamp) > %s AND userapproved = 0 ORDER BY timestamp DESC;',
#        (user,
#         start_timestamp)
#    )
#    return [i[0] for i in cursor.fetchall()]
    
## Get all users that have sent this user a follow request after a particular point in time
## (Still have to consider the case where user goes from private -> public in the future)
#def get_recent_follow_requests(cursor, user, start_timestamp):
#    cursor.execute(
#        'SELECT follower FROM username_follow_requests WHERE followee = %s AND ' + \
#        'UNIX_TIMESTAMP(timestamp) > %s ORDER BY timestamp DESC;',
#        (user,
#         start_timestamp)
#    )
#    return [i[0] for i in cursor.fetchall()]

## Get all users that have recently accepted this user's follow reuqest after a particular point in time 
#def get_recent_follow_accepts(cursor, user, start_timestamp):
#    cursor.execute(
#        'SELECT followee FROM username_follows WHERE follower = %s AND ' + \
#        'UNIX_TIMESTAMP(timestamp) > %s AND userapproved = 1 ORDER BY timestamp DESC;',
#        (user,
#         start_timestamp)
#    )
#    return [i[0] for i in cursor.fetchall()]

# Convert events to json with to_jsonnable function and paginate
def json_chunk(events, to_jsonnable, max_size, max_num_events):
    # No events handler
    if len(events) == 0: return ['[]']

    # Estimate page JSON size
    total_len = len(
        json.dumps(
            map(to_jsonnable, events)
        )
    )
    avg_event_len = int(total_len / len(events))
    events_per_record = int(max_size / avg_event_len) - 1
    events_per_record = min(events_per_record, max_num_events)    

    # Paginate events based on JSON size estimate
    event_partitions = [
        events[i:i+events_per_record] for i in range(
            0,
            len(events),
            events_per_record
        )
    ]
    
    # Convert pages to json
    return map(
        lambda events: json.dumps(
            map(
                to_jsonnable,
                events
            )
        ),
        event_partitions
    )

# Converts UTF dictionary strings from dynamo to regular
def convert(data):
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(convert, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert, data))
    else:
        return data

def get_scancode_s3_url(username):
    #s3 = boto3.client('s3')
    #return s3.generate_presigned_url('get_object', Params = {'Bucket': 'aquaint-userfiles-mobilehub-146546989', 'Key': 'public/scancodes/'+username})
    return "http://aquaint-userfiles-mobilehub-146546989.s3.amazonaws.com/public/scancodes/" + username    

def get_user_data(username):
    user_db = dynamo_table(USER_TABLE)
    print('Connected databases')
    print('Attempting to get data for user ' + username)

    data = read_user_dynamo_data(user_db, username)

    if data == []: return []

    data.scancodeimgurl = get_scancode_s3_url(username)	

    print('img url: ' + data.scancodeimgurl)
    print('username: ' + data.username)
    print('realname: ' + data.realname)
    print('accounts from dynamo: ')
    print(data.accounts)

    # Convert Dynamo json to regular json
    data.accounts = convert(data.accounts)
	
    print('accounts converted: ')
    print(data.accounts)

    print('isprivate: ')
    print(data.isprivate)
	
    print('Done')
    return data


