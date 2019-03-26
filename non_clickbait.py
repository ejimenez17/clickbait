# Sample Python code for user authorization

import os
import json
import csv
import urllib

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

def downloader(image_url, name):
    file_name = name
    full_file_name = file_name + '.jpg'
    urllib.urlretrieve(image_url,full_file_name)
    return full_file_name

def get_videos(response, length):
  with open("non_clickbait.csv", "a") as csvfile:
    for i in range(length):
      if not response['items'][i]['snippet']['title'] == 'Private video' and not response['items'][i]['snippet']['title'] == 'Deleted video':
        videoId = response['items'][i]['contentDetails']['videoId']
        video = videos_list_by_id(client,
          part='snippet,contentDetails,statistics',
          id=videoId)

        channelId = response['items'][i]['snippet']['channelId']
        channelData = get_channel_data(client,
          part='snippet,contentDetails,statistics',
          id=channelId)

        myTitle = video['items'][0]['snippet']['title']
        print myTitle
        myThumbnail = video['items'][0]['snippet']['thumbnails']['default']['url']
        # if myTitle.find('/') == -1:
        #   downloader(myThumbnails, myTitle[0:10])

        videoDislikes = video['items'][0]['statistics']['dislikeCount']
        videoLikes = video['items'][0]['statistics']['likeCount']
        videoViews = video['items'][0]['statistics']['viewCount']
        videoComments = video['items'][0]['statistics']['commentCount']

        # write row to csvfile
        vidWriter = csv.writer(csvfile, delimiter=",", quoting=csv.QUOTE_MINIMAL)
        vidWriter.writerow([channelId.encode('utf-8'), channelData[1].encode('utf-8'), channelData[2].encode('utf-8'), channelData[3].encode('utf-8'),\
          channelData[4].encode('utf-8'), videoComments.encode('utf-8'), videoDislikes.encode('utf-8'), videoId.encode('utf-8'), \
          videoLikes.encode('utf-8'), myTitle.encode('utf-8'), videoViews.encode('utf-8'), myThumbnail.encode('utf-8')])

  csvfile.close()

def get_channel_data(client, **kwargs):
  kwargs = remove_empty_kwargs(**kwargs)

  response = client.channels().list(
    **kwargs
  ).execute()

  myChannelId = response['items'][0]['id']
  myChannelName = response['items'][0]['snippet']['title']
  myChannelSubs = response['items'][0]['statistics']['subscriberCount']
  myChannelVidCount = response['items'][0]['statistics']['videoCount']
  myChannelViews = response['items'][0]['statistics']['viewCount']

  channelData = [myChannelId, myChannelName, myChannelSubs, myChannelVidCount, myChannelViews]
  return channelData

def videos_list_by_id(client, **kwargs):
  kwargs = remove_empty_kwargs(**kwargs)

  response = client.videos().list(
    **kwargs
  ).execute()

  return response

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
      numVids = 10
      playlist_items_list_by_playlist_id(client,
        part='snippet,contentDetails',
        maxResults=numVids,
        playlistId = myPlaylistId)

def playlist_items_list_by_playlist_id(client, **kwargs):
  # See full sample for function
  kwargs = remove_empty_kwargs(**kwargs)

  response = client.playlistItems().list(
    **kwargs
  ).execute()
  

  length = len(response['items'])
  get_videos(response, length)

if __name__ == '__main__':
  # When running locally, disable OAuthlib's HTTPs verification. When
  # running in production *do not* leave this option enabled.
  os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
  client = get_authenticated_service()

  clickbaitChannels = []
  count = 1
  with open(CHANNELS_FILE) as f:
      for line in f:
        if count > 25:
          clickbaitChannels.append(json.loads(line))
        count += 1
  
  for myChannelId in clickbaitChannels:
    playlists_list_by_channel_id(client,
      part='id,snippet,contentDetails',
      channelId=myChannelId,
      maxResults=10)
  # playlists_list_by_channel_id(client,
  #     part='id,snippet,contentDetails',
  #     channelId="UC9ISPZsMaBi5mutsgX6LC1g",
  #     maxResults=10)
