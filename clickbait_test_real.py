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
CLIENT_SECRETS_FILE = "client_secret_webapp.json"
CLICKBAIT_CHANNELS_FILE = "more_clickbait.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

def get_authenticated_service():
  flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
  credentials = flow.run_console()
  return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)

# def print_response(response, length):
#   for i in range(length):
#     print "\n"
#     print response['items'][i]['id']
#     print response['items'][i]['snippet']['title']

def downloader(image_url, name):
    file_name = name
    full_file_name = file_name + '.jpg'
    urllib.urlretrieve(image_url,full_file_name)
    return full_file_name

def videos_list_by_id(client, **kwargs):
  kwargs = remove_empty_kwargs(**kwargs)

  response = client.videos().list(
    **kwargs
  ).execute()

  return response

def get_video_id(path):
  """
  Get video id from a youtube URL
  For now, only of the form https://www.youtube.com/watch?v=VIDEOID
  """
  idIndex = path.find('=') + 1
  videoId = path[idIndex:]
  return videoId

def get_single_video(client, **kwargs):
  """
  Get video and channel data for a SINGLE video
  """
  kwargs = remove_empty_kwargs(**kwargs)

  response = client.videos().list(
    **kwargs
  ).execute()

  if not response['items'][0]['snippet']['title'] == 'Private video' \
    and not response['items'][0]['snippet']['title'] == 'Deleted video':
    videoId = response['items'][0]['id']

    channelId = response['items'][0]['snippet']['channelId']
    channelData = get_channel_data(client,
      part='snippet,contentDetails,statistics',
      id=channelId)

    myTitle = response['items'][0]['snippet']['title']
    myThumbnail = response['items'][0]['snippet']['thumbnails']['default']['url']

    videoDislikes = response['items'][0]['statistics']['dislikeCount']
    videoLikes = response['items'][0]['statistics']['likeCount']
    videoViews = response['items'][0]['statistics']['viewCount']
    videoComments = response['items'][0]['statistics']['commentCount']

    print(videoId, channelId, channelData, myTitle, myThumbnail, videoComments, videoDislikes, videoLikes, videoViews)

def get_videos(response, length):
  """
  Get video dislikes, likes, views, comment count, title, and thumbnail URL
  from a video ID (as well as info from the video's channel as detailed in 
  get_channel_data())
  Also adds rows to clickbaits.csv to store the data gathered
  """
  csvfile = open("clickbaits.csv", "a")
  for i in range(length):
    if not response['items'][i]['snippet']['title'] == 'Private video' and not response['items'][i]['snippet']['title'] == 'Deleted video':
      videoId = response['items'][i]['contentDetails']['videoId']
      video = videos_list_by_id(client,
        part='snippet,contentDetails,statistics',
        id=videoId)

      # myID = response['items'][i]['id']
      channelId = response['items'][i]['snippet']['channelId']
      channelData = get_channel_data(client,
        part='snippet,contentDetails,statistics',
        id=channelId)

      myTitle = video['items'][0]['snippet']['title']
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
  """
  Get channel name, # of subscribers, video count, 
  and view count from a channel ID
  """
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

# Remove keyword arguments that are not set
def remove_empty_kwargs(**kwargs):
  good_kwargs = {}
  if kwargs is not None:
    for key, value in kwargs.iteritems():
      if value:
        good_kwargs[key] = value
  return good_kwargs

def playlists_list_by_channel_id(client, **kwargs):
  """
  get playlist IDs from a channel by inputting a
  channel ID
  """
  kwargs = remove_empty_kwargs(**kwargs)

  response = client.playlists().list(
    **kwargs
  ).execute()

  length = len(response['items'])

  # for playlist in list of playlists in response
  for i in range(length):
    if not len(response['items'][i]) == 0:
      myPlaylistId = response['items'][i]['id']
      numVids = 7
      playlist_items_list_by_playlist_id(client,
        part='snippet,contentDetails',
        maxResults=numVids,
        playlistId = myPlaylistId)

def playlist_items_list_by_playlist_id(client, **kwargs):
  """
  Get videos in a playlist by inputting playlist id
  """
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
  # os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
  client = get_authenticated_service()

  # clickbaitChannels = []
  # count = 1
  # with open(CLICKBAIT_CHANNELS_FILE) as f:
  #     for line in f:
  #         if count > 10:
  #           clickbaitChannels.append(json.loads(line))
  #         count += 1

  # for myChannelId in clickbaitChannels:
  #   playlists_list_by_channel_id(client,
  #     part='id,snippet,contentDetails',
  #     channelId=myChannelId,
  #     maxResults=10)

  vidId = get_video_id("https://www.youtube.com/watch?v=p_4coiRG_BI")
  get_single_video(client,
    part='snippet,contentDetails,statistics',
    maxResults=1,
    id=vidId)
