import boto3
import json
from datetime import datetime

SHARED_ON_METADATA_KEY = 'shared-on'
BUCKET_NAME = 'dickie-videos'

s3 = boto3.resource('s3')
bucket = s3.Bucket(BUCKET_NAME)

# Get the date the video was last shared on from the metadata.
# Returns "0000-00-00" if there is no metadata
def get_last_share_date_internal(obj_summaries):
    obj = obj_summaries.Object()
    
    if SHARED_ON_METADATA_KEY not in obj.metadata:
        return "0000-00-00"
        
    return obj.metadata[SHARED_ON_METADATA_KEY]
    
# Get the last share data and print logs
def get_last_share_date(obj_summaries):
    share_date = get_last_share_date_internal(obj_summaries)
    print(obj_summaries.key)
    print(share_date)
    return share_date
    
# Get the candidate video to be shared    
def get_candidate(bucket, src_prefix):
    obj_summaries = bucket.objects.filter(Prefix=src_prefix)
    candidates = sorted(obj_summaries, key=get_last_share_date)
    return candidates[0]

# Update the target to the candidate
# Copies the candidate object, overwriting target.
# It would make more sense to update the html (or just have a backend that picks out today's video)
def update_target(candidate_key, target_key):
    copy_source = {
        'Bucket': BUCKET_NAME,
        'Key': candidate_key
    }

    obj = bucket.Object(target_key)
    obj.copy(copy_source)

    return

# Get today's date in the form "YYYY-MM-DD"
def get_share_date():
    return datetime.utcnow().strftime('%Y-%m-%d')

# Update candidate metadata to the share date
# Metadata is immutable, so really we are copying over the object.
# This is not an efficient way to track the video history, but it works.
def update_share_date(candidate_key, share_date):
    candidate_obj = s3.Object(BUCKET_NAME, candidate_key)
    candidate_obj.metadata.update({SHARED_ON_METADATA_KEY: share_date})
    candidate_obj.copy_from(CopySource={'Bucket': BUCKET_NAME, 'Key': candidate_key}, Metadata=candidate_obj.metadata, MetadataDirective='REPLACE')

# Find the next video to share, and (unless using preview mode) updates the target, plus the candidate shared-on metadata
# Trigger this Lambda via EventBridge schedule to update the site's video
def lambda_handler(event, context):
    src_prefix = event['srcPrefix']
    preview = event.get('preview', "false") == 'true'
    target_key = event['targetKey']
    candidate = get_candidate(bucket, src_prefix)
    last_shared_on = get_last_share_date(candidate)
    share_date = get_share_date()
    
    if not preview:
        print("preview disabled - updating...")
        update_target(candidate.key, target_key)
        update_share_date(candidate.key, share_date)
    else:
        print("preview mode - will not update")

    response = {'candidate_key': candidate.key, 'last_shared_on': last_shared_on, 'today': share_date}

    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }
