from bs4 import BeautifulSoup
import requests
from spotipy.oauth2 import SpotifyOAuth
import spotipy
import os
import datetime
import streamlit as st
import time

scope = ('playlist-modify-public playlist-modify-private playlist-read-private user-library-read '
         'user-read-recently-played user-library-modify')
redirect_uri = "https://example.com/"
username = os.getenv('USERNAME')


# with open('token.txt', 'r') as token_file:
#     tokens = json.load(token_file)
#
# access_token = tokens['access_token']
# refresh_token = tokens['refresh_token']


def get_spotify_client():
    auth_manager = SpotifyOAuth(client_id='f81abafcc2dd4d06a07e05560353900a',
                                client_secret='18d25eae7ab24845bf3e1445491b5cca',
                                redirect_uri=redirect_uri,
                                scope=scope,
                                cache_path='token.txt',
                                username='31ovusbqnqayjqgfm2wuhel6tlwi')

    sp1 = spotipy.Spotify(auth_manager=auth_manager)
    return sp1


sp = get_spotify_client()



def create_new_playlist(playlist_name, playlist_description):
    user_id = sp.current_user()['id']
    new_playlist = sp.user_playlist_create(
        user=user_id,
        name=playlist_name,
        public=True,
        description=playlist_description
    )
    return new_playlist['id']


def get_users_playlists():
    pass


def get_users_recently_played_songs():
    pass


def create_new_playlist_of_top_100_songs_of_specific_date(date, playlist_name, playlist_description):
    url = f'https://www.billboard.com/charts/hot-100/{str(date)}'
    header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0"}
    response = requests.get(url=url, headers=header)
    webpage = response.text
    soup = BeautifulSoup(webpage, 'html.parser')

    element = soup.find('div', class_='pmc-paywall')
    list1 = element.find_all('div', class_='o-chart-results-list-row-container')
    songs = []

    for ele in list1:
        item = ele.find('h3', id='title-of-a-story')
        songs.append(item.text.strip())

    playlist_id = create_new_playlist(playlist_name=playlist_name, playlist_description=playlist_description)
    tracks_uris = []
    for song_name in songs:
        search_result = sp.search(q=song_name, type='track', limit=1)
        for track in search_result['tracks']['items']:
            tracks_uris.append(track['external_urls']['spotify'])
    response = sp.playlist_add_items(playlist_id=playlist_id, items=tracks_uris)
    return response


# MAIN SECTION

st.title("Music Time Machine App")
st.divider()

with st.container(height=308):
    col1, col2 = st.columns([0.3, 0.7], gap='medium')
    user = sp.current_user()
    with col1:
        profile_image_html = f'''
        <img src='{user['images'][0]['url']}' 
        style="height:17rem; width:13rem; border-radius:6px;">
'''
        st.markdown(profile_image_html, unsafe_allow_html=True)
    with col2:
        st.markdown(f'''
        <h3 style="padding-left: 2rem">Username: &nbsp; <span style="font-style: italic; color: #02eb88">{user['display_name']}</span></h3>''',
                    unsafe_allow_html=True)
        st.divider()
        st.markdown(f'''<h3 
        style="padding-left: 2rem">Total Followers: &nbsp; <span style="font-style: italic; color: #dc0151">{user['followers']['total']}
        </span></h3>''',
                    unsafe_allow_html=True)


if 'show_create_playlist_form' not in st.session_state:
    st.session_state.show_create_playlist_form = False

if st.button('Create Playlist of Top 100 Songs of Specific Date'):
    st.session_state.show_create_playlist_form = True

if st.session_state.show_create_playlist_form:
    with st.form('Enter Playlist Details'):
        date = st.date_input('Select the Date', datetime.date(2025, 1, 1))
        playlist_name = st.text_input(label='Playlist Name', value='New Playlist')
        playlist_description = st.text_area(label='Playlist Description', value='')
        submit = st.form_submit_button('Create')
        if submit:
            st.session_state.playlist_details = {'date': date,
                                                 'playlist_name': playlist_name,
                                                 'playlist_description': playlist_description}
            st.session_state.show_create_playlist_form = False

    if 'playlist_details' in st.session_state:
        response = create_new_playlist_of_top_100_songs_of_specific_date(date=st.session_state.playlist_details['date'],
                                                                         playlist_name=
                                                                         st.session_state.playlist_details[
                                                                             'playlist_name'],
                                                                         playlist_description=
                                                                         st.session_state.playlist_details[
                                                                             'playlist_description'])
        st.toast('Playlist Created!', icon='🎉')
        st.balloons()
        time.sleep(3)
        st.rerun()

st.divider()
st.markdown(f'<h3>Liked Songs</h2>',unsafe_allow_html=True )
results = sp.current_user_saved_tracks()
for item in results['items']:
    track = item['track']
    with st.container(height=150):
        col1, col2, col3 = st.columns([0.3, 0.3, 0.4], gap='medium')
        with col1:
            html_image = f'''<img src='{track['album']['images'][0]['url']}' style="height: 7rem; width:7rem; border-radius: 8px"> '''
            st.markdown(html_image, unsafe_allow_html=True)
        with col2:
                html_trackname = f'''<h4 style="align: left">{track['name']}</h4>'''
                st.markdown(html_trackname, unsafe_allow_html=True)
                st.write(f'Artist: {track['album']['artists'][0]['name']}')

