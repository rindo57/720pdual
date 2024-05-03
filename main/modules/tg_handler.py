
import asyncio
import time
import aiohttp
import requests
import aiofiles
import sys
from main.modules.compressor import compress_video
from pymediainfo import MediaInfo
from main.modules.utils import episode_linker, get_duration, get_epnum, status_text, get_filesize, b64_to_str, str_to_b64, send_media_and_reply, get_durationx

from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from main.modules.uploader import upload_video
from main.modules.thumbnail import generate_thumbnail

import os

from main.modules.db import del_anime, save_uploads, is_fid_in_db, is_tit_in_db

from main.modules.downloader import downloader

from main.modules.anilist import get_anilist_data, get_anime_img, get_anime_name

from config import INDEX_USERNAME, UPLOADS_USERNAME, UPLOADS_ID, INDEX_ID, PROGRESS_ID, LINK_ID

from main import app, queue, status

from pyrogram.errors import FloodWait

from pyrogram import filters, enums

from main.inline import button1

status: Message

async def tg_handler():

    while True:

        try:
            if len(queue) != 0:

                i = queue[0]  

                i = queue.pop(0)
                
                id, name, video = await start_uploading(i)
                print("Title: ", i["title"])
                await del_anime(i["title"])
                await save_uploads(i["title"])
                await asyncio.sleep(30)


            else:                

                if "Idle..." in status.text:

                    try:

                        await status.edit(await status_text("Idle..."))

                    except:

                        pass

                await asyncio.sleep(30)

                

        except FloodWait as e:

            flood_time = int(e.x) + 5

            try:

                await status.edit(await status_text(f"Floodwait... Sleeping For {flood_time} Seconds"),reply_markup=button1)

            except:

                pass

            await asyncio.sleep(flood_time)

        except:

            pass


def get_audio_language(video_path):
    try:
        media_info = MediaInfo.parse(video_path)
        for track in media_info.tracks:
            if track.track_type == 'Audio':
                language = track.language
                language = language.replace("ja", "JP")
                language = language.replace("en", "EN")
                return language
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None
        

async def start_uploading(data):

    try:

        title = data["title"]
        dbtit = data["title"]
        link = data["link"]
        size = data["size"]
        nyaasize = data["size"]
        subtitle = data["subtitle"]
        name, ext = title.split(".")

        name += f" [AniDL]." + ext

        KAYO_ID =  -1001895203720
        uj_id = 1159872623
        DATABASE_ID = -1001895203720
        bin_id = -1002062055380
        name = name.replace(f" [AniDL].","").replace(ext,"").strip()
        extit = title.replace("[AniDL] ", "")
        id, img, tit = await get_anime_img(get_anime_name(extit))
        msg = await app.send_photo(bin_id,photo=img,caption=title)

        print("Downloading --> ",title)
        img, caption, alink = await get_anilist_data(title)
        await asyncio.sleep(5)
        await status.edit(await status_text(f"Downloading {title}"),reply_markup=button1)
        file = await downloader(msg,link,size,title)

        await msg.edit(f"Download Complete : {title}")
        print("Encoding --> ",title)

        duration = get_duration(file)
        durationx = get_durationx(file)
        filed = os.path.basename(file)
        filed = filed.replace(filed, title)
        fpath = "downloads/" + filed
        ghostname = title
        subtitle = subtitle.replace("][", ", ")
        subtitle = subtitle.replace("[", "")
        subtitle = subtitle.replace("]", "")     
    
        os.rename(file,"video.mkv")
        main = await app.send_photo(KAYO_ID,photo=img, caption=title)
        video_path="video.mkv"
        
        audio_language = get_audio_language(video_path)
        if audio_language:
            print("Audio Track Language:", audio_language)
        else:
            print("Failed to get audio language.")
        compressed = await compress_video(duration,main,tito)
    

        if compressed == "None" or compressed == None:

            print("Encoding Failed Uploading The Original File")

            os.rename("video.mkv",fpath)

        else:

            os.rename("out.mkv",fpath)
  
        print("Uploading --> ",title)
        video = await upload_video(msg,img,fpath,id,tit,name,size,main,subtitle,nyaasize,audio_language, alink, filed)



        try:

            os.remove("video.mkv")

            os.remove("out.mkv")

            os.remove(file)

            os.remove(fpath)
        except:

            pass     

    except FloodWait as e:

        flood_time = int(e.x) + 5

        try:

            await status.edit(await status_text(f"Floodwait... Sleeping For {flood_time} Seconds"),reply_markup=button1)

        except:

            pass

        await asyncio.sleep(flood_time)
        
    return id, name, video

    
