import telebot as tb
import os
import re
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
TARGET_CHANNEL = os.getenv('TARGET_CHANNEL_ID', '@kirisora_test_music_publish_bot')
ADMIN_ID = os.getenv('ADMIN_TG_ID')

SPOTIFY_REGEX = r'^https?:\/\/(open|play)\.spotify\.com\/(track|album|playlist|artist)\/([a-zA-Z0-9]+)'

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

bot = tb.TeleBot(TELEGRAM_TOKEN, parse_mode='Markdown')
bot.send_message(ADMIN_ID, 'Bot up and running!')

@bot.message_handler(regexp=SPOTIFY_REGEX)
def default_handler(message):
    link_match = re.search(SPOTIFY_REGEX, message.text)
    link_type = link_match.group(2)
    link_id = link_match.group(3)

    match link_type:
        case 'track':
            track = sp.track(link_id)
            print(track)
            track_name = track['name']
            track_artists = ", ".join(a['name'] for a in track['artists'])
            track_cover_url = track['album']['images'][0]['url']

            track_main_artist_id = track['artists'][0]['id']
            track_main_artist = sp.artist(track_main_artist_id)
            genres = ' '.join(f"#{genre.replace(' ', '')}" for genre in track_main_artist['genres']) if track_main_artist['genres'] else ''

            caption = f"**[{track_name} - {track_artists}]({message.text})**"
            if genres:
                caption += f"\n\n{genres}"
            
            bot.send_photo(
                chat_id=message.chat.id,
                photo=track_cover_url,
                caption=caption
            )

        case 'album':
            album = sp.album(link_id)
            print(album)
            album_name = album['name']
            album_artists = ", ".join(a['name'] for a in album['artists'])
            album_cover_url = album['images'][0]['url']

            track_main_artist_id = album['artists'][0]['id']
            track_main_artist = sp.artist(track_main_artist_id)
            genres = ' '.join(f"#{genre.replace(' ', '')}" for genre in track_main_artist['genres']) if track_main_artist['genres'] else ''

            caption = f"**[{album_name} - {album_artists}]({message.text})**"
            if genres:
                caption += f"\n\n{genres}"
            
            bot.send_photo(
                chat_id=message.chat.id,
                photo=album_cover_url,
                caption=caption,
                parse_mode='Markdown'
            )
        
        case 'artist':
            track_main_artist = sp.artist(link_id)
            print(track_main_artist)
            artist_name = track_main_artist['name']
            artist_image_url = track_main_artist['images'][0]['url'] if track_main_artist['images'] else None
            genres = ' '.join(f"#{genre.replace(' ', '')}" for genre in track_main_artist['genres']) if track_main_artist['genres'] else ''

            caption = f"**[{artist_name}]({message.text})**"
            if genres:
                caption += f"\n\n{genres}"
            
            if artist_image_url:
                bot.send_photo(
                    chat_id=message.chat.id,
                    photo=artist_image_url,
                    caption=caption,
                    parse_mode='Markdown'
                )
            else:
                bot.send_message(
                    chat_id=message.chat.id,
                    text=caption,
                    parse_mode='Markdown'
                )
        
        case 'playlist':
            playlist = sp.playlist(link_id)
            print(playlist)
            playlist_name = playlist['name']
            playlist_cover_url = playlist['images'][0]['url'] if playlist['images'] else None

            caption = f"**[{playlist_name}]({message.text})**"
            
            if playlist_cover_url:
                bot.send_photo(
                    chat_id=message.chat.id,
                    photo=playlist_cover_url,
                    caption=caption,
                    parse_mode='Markdown'
                )
            else:
                bot.send_message(
                    chat_id=message.chat.id,
                    text=caption,
                    parse_mode='Markdown'
                )

        case _:
            print("empty case", link_type)
            return

bot.infinity_polling()