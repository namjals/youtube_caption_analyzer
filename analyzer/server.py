

import json
import os
import re
import sys
import time

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import flask
from flask import jsonify
from flask import send_file
from flask import session
from flask import request
from flask import redirect
from flask import url_for
import requests
from werkzeug.serving import run_simple

import indexing
import keywords
import noun
import preprocessing
from lib.utils import get_depth_dict
from lib.utils import load_json, save_json
from lib.utils import path
#from path import path


download_path = path['download']

# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = "key/client_secret.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl", 
          "https://www.googleapis.com/auth/youtubepartner"]
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
app = flask.Flask(__name__)
# Note: A secret key is included in the sample so that it works.
# If you use this code in your application, replace this with a truly secret
# key. See http://flask.pocoo.org/docs/0.12/quickstart/#sessions.
app.secret_key = 'REPLACE ME - this value is here as a placeholder.'


@app.route('/')
def index():
    return print_index_table()

@app.route('/authorize')
def authorize():
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)

    flow.redirect_uri = url_for('oauth2callback', _external=True)
    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')
    
    # Store the state so the callback can verify the auth server response.
    session['state'] = state

    return redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = session['state']
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = url_for('oauth2callback', _external=True)
    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)
    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials    
    session['credentials'] = credentials_to_dict(credentials)    
    return redirect(url_for('index'))


@app.route('/revoke')
def revoke():
    if 'credentials' not in session:
        return ('You need to <a href="/authorize">authorize</a> before ' +
                'testing the code to revoke credentials.')

    credentials = google.oauth2.credentials.Credentials(
      **session['credentials'])

    revoke = requests.post('https://accounts.google.com/o/oauth2/revoke',
        params={'token': credentials.token},
        headers = {'content-type': 'application/x-www-form-urlencoded'})

    status_code = getattr(revoke, 'status_code')
    if status_code == 200:
        return('Credentials successfully revoked.' + print_index_table())
    else:
        return('An error occurred.' + print_index_table())


@app.route('/clear')
def clear_credentials():
    if 'credentials' in session:
        del session['credentials']
    return ('Credentials have been cleared.<br><br>' +
            print_index_table())

def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}


def print_search_list(search_word, search_list, runtime):
    
    html =  '<table>' +             '<tr><td><a href="/">검색하러 가기</a></td></tr>' +             '<tr><td>검색어 '+ str(search_word) + '</td></tr>' +             '<tr><td>검색결과 ' + str(len(search_list))+ '개 ('+ str(round(runtime,6)) +'초)</td></tr>' +             '</table><br><br>'
    
    
    for info in search_list:
        html += '<table>' +             '<tr><td>1. 제목     : ' + info['title'] +'</td></tr>' +             '<tr><td>2. 설명     : ' + info['description'] +'</td></tr>' +             '<tr><td>3. 키워드   : ' + info['keywords'] +'</td></tr>' +             '<tr><td>4. 자막유형 : ' + info['trackKind'] +'</td></tr>' +             '<tr><td><a href="' +info['link']+ '">5. 링크</a></td></tr>' +             '</table>' +             '<br><br>'
    
    return html
    
    
    
def print_index_table():
    return ('<table>' +
            '<tr><td><a href="/authorize">1. Get auth</a></td></tr>' +            
            '<tr><td><a href="/revoke">2. Revoke current credentials</a></td></tr>' +
            '<tr><td><a href="/clear">3. Clear Flask session credentials</a></td></tr>' +
            '<tr><td>4. Download caption information</a></td></tr>' +
            '</table>' +
            '<form action="/caption_download" method="get" enctype="application/x-www-form-urlencoded">' +
            'channel_id : <input type="text" name="channel_id" value="UC63J0Q5huHSlbNT3KxvAaHQ"><br>' +
            'resume : <input type="number" name="resume" min="0" placeholder="이어받을 숫자, ex)300"><br>' +
            '<input type="submit" value="Download">' +
            '</form>' +
            '<table><br><br>' +
            '<tr><td><a href="/train">1. Train</a> : 명사(soynlp+komoran), 키워드(doc2vec) 학습</td></tr>' +            
            '<tr><td><a href="/update">2. Update</a> : 명사, 키워드, 인덱싱 정보 업데이트.</td></tr>' +
            '<tr><td><a href="/forced_update">3. Forced update</a> : 상태 관련없이 모두 업데이트</td></tr>' +
            '</table>' +
            '<form action="/search_word" method="get" enctype="application/x-www-form-urlencoded">' +
            '<input type="text" name="search_word" placeholder="검색어를 입력해주세요." required/> ' +
            '<input type="submit" value="Search">' +
            '</form>'
            
           )


def initalize():
    indexing.Indexer.loader()
initalize()
    
@app.route('/train')
def train():
    preprocessing.normalizing(forced = True)
    noun.train()
    noun.update(forced = True)
    keywords.train()
    return redirect(url_for('index'))

@app.route('/update')
def update():    
    preprocessing.normalizing()
    noun.update()
    keywords.update()
    indexing.IndexerDict().update()
    return redirect(url_for('index'))

@app.route('/forced_update')
def forced_update():
    preprocessing.normalizing(forced = True)
    noun.update(forced = True)
    keywords.update(forced = True)
    indexing.IndexerDict().update(forced = True)
    return redirect(url_for('index'))

@app.route('/search_word')
def search_word():
    search_word = request.args.get('search_word')
    
    import timeit
    start = timeit.default_timer()
    search_list = indexing.IndexerDict().search(search_word)
    stop = timeit.default_timer()

    return print_search_list(search_word, search_list, stop - start )
    
    
@app.route('/caption_download', methods=['GET'])
def caption_download():
    if 'credentials' not in session:
        return redirect('authorize')
    credentials = google.oauth2.credentials.Credentials(
        **session['credentials'])

    youtube = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)
    
    channel_id = request.args.get('channel_id')    
    resume = request.args.get('resume', 0)
    resume = int(resume) if resume else 0

    max_results = 50  
    
    try:
        #1. page 정보 추출
        search_list = youtube.search().list(
            part = 'id',
            channelId = channel_id,
            maxResults = 1,
            type = 'video',
            fields = 'items,pageInfo'
        ).execute()    
    except Exception as e:
        print(e)
        return jsonify({ 'error' : str(e)}) 

    caption_count = 0
    total_results = search_list['pageInfo']['totalResults']
    sys.stdout.write('\rprogress... {:4}/{:4} '.format(caption_count,total_results))
    
    pages = total_results // max_results + 1    
    next_page_token = ''
    
    caption_time_pattern = re.compile('\d:\d\d:\d\d.\d\d\d,\d:\d\d:\d\d.\d\d\d')
    
    for page in range(pages):
        #2. video id, title, description 추출
        search_list = youtube.search().list(
            part = 'snippet',
            channelId = channel_id,
            maxResults = max_results,   
            pageToken = next_page_token,
            type = 'video',
            fields = 'items(etag,id,snippet(description,title)),nextPageToken'            
        ).execute() 
        
        next_page_token = search_list.get('nextPageToken' ,None)
        
        for item in search_list['items']:   
            caption_count += 1
            
            if caption_count < resume:
                sys.stdout.write('\rprogress... {:4}/{:4} '.format(caption_count,total_results))
                continue
            
            caption_dump = load_json(download_path)
            
            video_id = get_depth_dict(item, ('id', 'videoId'), None)
            if not video_id:
                print('error : There is no video_id.')
                sys.stdout.write('\rprogress... {:4}/{:4} '.format(caption_count,total_results))
                continue
            title = get_depth_dict(item, ('snippet', 'title'), None)
            description = get_depth_dict(item, ('snippet', 'description'), None)
                        
            #3. caption id 추출
            caption_list = youtube.captions().list(
                part = 'snippet',
                videoId = video_id,
                fields= 'items(etag,id,snippet(language,trackKind,lastUpdated))'
            ).execute()
            
            caption_kind = {}            
            for item in caption_list['items']:
                track_kind = item['snippet']['trackKind']
                caption_kind[track_kind] = {'id' : item['id'], 'lastUpdated' : item['snippet']['lastUpdated']}
                
            #4. 선호하는 trackKind 추출 
            caption_id = None
            track_kind_preference = ['standard', 'ASR', 'forced']
            for preference in track_kind_preference:
                if caption_kind.get(preference, None):
                    caption_id = caption_kind[preference]['id']
                    new_last_updated = caption_kind[preference]['lastUpdated']
                    track_kind = preference
                    break
                    
            if not caption_id:
                print('error : There is no caption. video_id : ',video_id)
                update_info = {
                'title' : title,
                'description' : description,
                'error' : 'There is no caption.'
                }
                if caption_dump.get(video_id, None):
                    update_info['state'] = 'new'
                else:
                    update_info['state'] = 'update'                   
                caption_dump[video_id] = update_info
                save_json(caption_dump, download_path) 
                sys.stdout.write('\rprogress... {:4}/{:4} '.format(caption_count,total_results))
                continue
                
            #5. caption lastUpdated 체크
            old_last_updated = get_depth_dict(caption_dump, (video_id, 'lastUpdated'), None)
            if old_last_updated and new_last_updated == old_last_updated:
                sys.stdout.write('\rprogress... {:4}/{:4} '.format(caption_count,total_results))
                continue    
                
            #6. download
            try:
                caption = youtube.captions().download(
                    id = caption_id,
                    tfmt= 'sbv'
                ).execute().decode("utf-8")
            except Exception as e:
                print(e)
                print('video_id : ', video_id)
                update_info = {
                'title' : title,
                'description' : description,
                'error' : str(e)
                }
                if caption_dump.get(video_id, None):
                    update_info['state'] = 'update'
                else:
                    update_info['state'] = 'new'   
                caption_dump[video_id] = update_info
                save_json(caption_dump, download_path)  
                sys.stdout.write('\rprogress... {:4}/{:4} '.format(caption_count,total_results))
            else:               
                caption = caption_time_pattern.sub('',caption)
                update_info = {
                    'lastUpdated' : new_last_updated,
                    'trackKind' : track_kind,
                    'caption' : caption,
                    'title' : title,
                    'description' : description
                }
                if caption_dump.get(video_id, None):
                    update_info['state'] = 'update'
                else:
                    update_info['state'] = 'new'   
                caption_dump[video_id] = update_info
                save_json(caption_dump, download_path) 
                sys.stdout.write('\rprogress... {:4}/{:4} '.format(caption_count,total_results))
                
            time.sleep(0.5)
    
    return redirect(url_for('index', _exteranl=True))
    


# When running locally, disable OAuthlib's HTTPs verification.
# ACTION ITEM for developers:
#     When running in production *do not* leave this option enabled.
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

run_simple('localhost', 8080, app, use_reloader =False)


