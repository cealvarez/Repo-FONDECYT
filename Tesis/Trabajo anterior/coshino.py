import json
import webbrowser
import httplib2
import sys
import argparse
import requests

from oauth2client.tools import argparser
from apiclient import discovery
from oauth2client import client
from oauth2client.file import Storage


#Busca los videos de YouTube que calcen con la palabra options
def youtube_search(options, youtube):
  search_response = youtube.search().list(
    q=options.jiji,
    part="id,snippet",
    maxResults=options.max_results
  ).execute()
  videos = []
  channels = []
  playlists = []

  for search_result in search_response.get("items", []):
    if search_result["id"]["kind"] == "youtube#video":
      tupla = (search_result["snippet"]["title"], search_result["id"]["videoId"])
      videos.append(tupla)
  return videos[0]


#Crea una lista de reproduccion de nombre playlist_name, que se encuentre en el archivo .json
def youtube_playlist(youtube, playlist_name):
  with open("listas_de_reproduccion.json", 'r') as jiji:
    coshino = json.load(jiji)
  if playlist_name in coshino['playlists']:
    my_title = coshino['playlists'][playlist_name]['name']

  # crea playlist
  playlists_insert_response = youtube.playlists().insert(
    part="snippet,status",
    body=dict(
      snippet=dict(
        title=my_title,
        description="Playlist de " + my_title
      ),
      status=dict(
        privacyStatus="private"
      )
    )
  ).execute()
  playListId = playlists_insert_response["id"]
  for cancion in coshino['playlists'][playlist_name]["tracks"]:
    parser=argparse.ArgumentParser()
    parser.add_argument("--jiji", help="Search term", default=cancion['name'])
    parser.add_argument("--max-results", help="Max results", default=25)
    args = parser.parse_args()

    #tupla (nombre_video, id_video)
    video = youtube_search(args, youtube)
    playlistitem_insert_response = youtube.playlistItems().insert(
      part="snippet,status",
      body=dict(
        snippet=dict(
          playlistId=playListId,
          resourceId=dict(
            kind="youtube#video",
            videoId=video[1]
            ),
          position=0
        ),
        status=dict(
          privacyStatus="private"
        )
      )
    ).execute()

#ingresa el comentario comentario al video video_id 
def youtube_comment(youtube, video_id, comentario):
  comment_response = youtube.commentThreads().insert(
    part="snippet",
    body=dict(
      snippet=dict(
        videoId=video_id,  
        topLevelComment=dict(
          snippet=dict(
            textOriginal=comentario
          )
        )
      )
    )
  ).execute()
  print('Comentario:', comment_response["snippet"]["topLevelComment"]["snippet"]["textDisplay"])

#Obtiene comentarios, likes, dislikes y reproducciones de todos los videos de la lista de 
#reproduccion playlist_id.
def youtube_statistics(youtube, playlist_ID):

  playlistitems_list_request = youtube.playlistItems().list(
    playlistId=playlist_ID,
    part="snippet",
    maxResults=50
  )

  while playlistitems_list_request:
    playlistitems_list_response = playlistitems_list_request.execute()

    # Print information about each video.
    for playlist_item in playlistitems_list_response["items"]:
      title = playlist_item["snippet"]["title"]
      video_id = playlist_item["snippet"]["resourceId"]["videoId"]
      
      video_request = youtube.videos().list(
        part="snippet,statistics",
        id=video_id
      ).execute()

      print(title, video_id)
      print("likes:", video_request["items"][0]["statistics"]["likeCount"])
      print("dislikes:", video_request["items"][0]["statistics"]["dislikeCount"])
      print("view:", video_request["items"][0]["statistics"]["viewCount"])
      print("comment:", video_request["items"][0]["statistics"]["commentCount"])

    playlistitems_list_request = youtube.playlistItems().list_next(
      playlistitems_list_request, playlistitems_list_response)

#Con esto puedes hacer los requests
def login():
  flow = client.flow_from_clientsecrets(
    'client_secrets.json',
    scope='https://www.googleapis.com/auth/youtube',
    redirect_uri='urn:ietf:wg:oauth:2.0:oob')
  auth_uri = flow.step1_get_authorize_url()
  webbrowser.open(auth_uri)
  auth_code = raw_input('Enter the auth code: ')
  credentials = flow.step2_exchange(auth_code)
  http_auth = credentials.authorize(httplib2.Http())
  video_service = discovery.build('youtube', 'v3', http_auth)

  flow2 = client.flow_from_clientsecrets(
    'client_secrets.json',
    scope='https://www.googleapis.com/auth/youtube.force-ssl',
    redirect_uri='urn:ietf:wg:oauth:2.0:oob')
  auth_uri2 = flow2.step1_get_authorize_url()
  webbrowser.open(auth_uri2)
  auth_code2 = raw_input('Enter the auth code: ')
  credentials2 = flow.step2_exchange(auth_code2)
  http_auth2 = credentials2.authorize(httplib2.Http())
  comment_service = discovery.build('youtube', 'v3', http_auth2)

  return video_service, comment_service  


if __name__ == '__main__':
  
  #video_service: videos
  #comment_service: comentarios
    
  my_video_service, my_comment_service = login()

  #playlist_name = "Mi lista de reproduccion a crear"
  #youtube_playlist(my_video_service, playlist_name)
  #youtube_comment(my_comment_service, "WLjMqK7hedI", "Un comentario bueno")
  #youtube_statistics(my_video_service, "PLATdwpMEAXbFgmxIhRyna0MWhWbbvOa5u")

  #VIDEO: WLjMqK7hedI
  #LISTA: PLATdwpMEAXbFgmxIhRyna0MWhWbbvOa5u


  GET

  {
    current: 1
    success
  }


  POST

  {
    new_current: 1
    success
  }