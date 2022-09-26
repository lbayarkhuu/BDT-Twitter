from nis import cat
from tweepy import Stream
from time import sleep
import sys
import codecs
from kinesis.producer import KinesisProducer
import boto3
import json

STREAM_NAME = "data-stream"
client = boto3.client('kinesis')

def to_bytes(s):
    if type(s) is bytes:
        return s
    elif type(s) is str or (sys.version_info[0] < 3 and type(s) is unicode):
        return codecs.encode(s, 'utf-8')
    else:
        raise TypeError("Expected bytes or string, but got %s." % type(s))

producer = KinesisProducer(stream_name='my-stream')

class StreamListener(Stream):
    def on_connect(self):
        print("You are now connected to the streaming API.")

    def on_error(self, status_code):
        return True

    def on_data(self, data):
        try:
            data = json.loads(data)
            txt = data['text']
            date = data['created_at']
            
            for category in ["Python", "C++", "NodeJS", "Java"]:
                if category in txt:
                    data = json.dumps({
                        'category': category,
                        'txt': txt,
                        'date': date
                    })  
                    response = client.put_record(
                        StreamName=STREAM_NAME,
                        Data=to_bytes(data + '\n'),
                        PartitionKey=category
                    )
                    print({
                        'category': category,
                        'txt': txt,
                        'date': date
                    })
                    print(response)

            sleep(3)

        except Exception as e:
            print(e)
            print('=== Error ===')
            return False
        return True

    def on_timeout(self):
        return True

consumer_key = ''
consumer_secret = ''
access_key = ''
access_secret = ''

stream = StreamListener(consumer_key,
                        consumer_secret,
                        access_key,
                        access_secret)

stream.filter(track=["Python", "C++", "NodeJS", "Java"], languages=["en"])