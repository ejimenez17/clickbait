# Sample Python code for user authorization

import os
import json
import csv

import google.oauth2.credentials

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret.
CLIENT_SECRETS_FILE = "client_secret.json"
CHANNELS_FILE = "non_clickbait.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

def get_authenticated_service():
  flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
  credentials = flow.run_console()
  return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)

def print_response(response, length):
  for i in range(length):
    print "\n"
    print response['items'][i]['id']
    print response['items'][i]['snippet']['title']

def get_videos(response, length):
  csvfile = open("non_clickbait.csv", "a")
  videos = []
  for i in range(length):
    if not response['items'][i]['snippet']['title'] == 'Private video' and not response['items'][i]['snippet']['title'] == 'Deleted video':
      myID = response['items'][i]['id']
      myTitle = response['items'][i]['snippet']['title']
      myThumbnails = response['items'][i]['snippet']['thumbnails']['default']['url']
      videos += [(myID, myTitle, myThumbnails)]
      # write row to csvfile
      vidWriter = csv.writer(csvfile, delimiter=",", quoting=csv.QUOTE_MINIMAL)
      vidWriter.writerow([myID.encode('utf-8'), myTitle.encode('utf-8'), myThumbnails.encode('utf-8')])

  csvfile.close()
  return videos

# Remove keyword arguments that are not set
def remove_empty_kwargs(**kwargs):
  good_kwargs = {}
  if kwargs is not None:
    for key, value in kwargs.iteritems():
      if value:
        good_kwargs[key] = value
  return good_kwargs

def channels_list_by_username(service, **kwargs):
  results = service.channels().list(
    **kwargs
  ).execute()
  
  print('This channel\'s ID is %s. Its title is %s, and it has %s views.' %
       (results['items'][0]['id'],
        results['items'][0]['snippet']['title'],
        results['items'][0]['statistics']['viewCount']))

def videos_list_by_channel_id(service, **kwargs):
    results = service.videos().list(
        **kwargs
    ).execute()

    print("This Video is %s." %
        (results['items'][0]['snippet']['title']))

def playlists_list_by_channel_id(client, **kwargs):
  kwargs = remove_empty_kwargs(**kwargs)

  response = client.playlists().list(
    **kwargs
  ).execute()

  length = len(response['items'])

  # for playlist in list of playlists in response
  for i in range(length):
    if not len(response['items'][i]) == 0:
      myPlaylistId = response['items'][i]['id']
      numVids = 3
      playlist_items_list_by_playlist_id(client,
        part='snippet',
        maxResults=numVids,
        playlistId = myPlaylistId)

def playlist_items_list_by_playlist_id(client, **kwargs):
  # See full sample for function
  kwargs = remove_empty_kwargs(**kwargs)

  response = client.playlistItems().list(
    **kwargs
  ).execute()
  

  length = len(response['items'])
  videos = get_videos(response, length)
  return videos

if __name__ == '__main__':
  # When running locally, disable OAuthlib's HTTPs verification. When
  # running in production *do not* leave this option enabled.
  os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
  client = get_authenticated_service()

  clickbaitChannels = []
  with open(CHANNELS_FILE) as f:
      for line in f:
          clickbaitChannels.append(json.loads(line))
  
  for myChannelId in clickbaitChannels:
    print "channel ID: ", myChannelId
    playlists_list_by_channel_id(client,
      part='id,snippet,contentDetails',
      channelId=myChannelId,
      maxResults=5)