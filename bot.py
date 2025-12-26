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
            track_name = track['name']
            track_artists = ", ".join(artist['name'] for artist in track['artists'])
            track_cover_url = track['album']['images'][0]['url']
            
            bot.send_photo(
                chat_id=message.chat.id,
                photo=track_cover_url,
                caption=f"[{track_name} - {track_artists}]({message.text})"
            )

        case 'album':
            album = sp.album(link_id)
            album_name = album['name']
            album_artists = ", ".join(artist['name'] for artist in album['artists'])
            album_cover_url = album['images'][0]['url']
            
            bot.send_photo(
                chat_id=message.chat.id,
                photo=album_cover_url,
                caption=f"[{album_name} - {album_artists}]({message.text})",
                parse_mode='Markdown'
            )
        
        case 'artist':
            artist = sp.artist(link_id)
            artist_name = artist['name']
            artist_image_url = artist['images'][0]['url'] if artist['images'] else None
            
            if artist_image_url:
                bot.send_photo(
                    chat_id=message.chat.id,
                    photo=artist_image_url,
                    caption=f"[{artist_name}]({message.text})",
                    parse_mode='Markdown'
                )
            else:
                bot.send_message(
                    chat_id=message.chat.id,
                    text=f"[{artist_name}]({message.text})",
                    parse_mode='Markdown'
                )
        
        case 'playlist':
            playlist = sp.playlist(link_id)
            playlist_name = playlist['name']
            playlist_cover_url = playlist['images'][0]['url'] if playlist['images'] else None
            
            if playlist_cover_url:
                bot.send_photo(
                    chat_id=message.chat.id,
                    photo=playlist_cover_url,
                    caption=f"[{playlist_name}]({message.text})",
                    parse_mode='Markdown'
                )
            else:
                bot.send_message(
                    chat_id=message.chat.id,
                    text=f"[{playlist_name}]({message.text})",
                    parse_mode='Markdown'
                )

        case _:
            print("empty case", link_type)
            return

bot.infinity_polling()