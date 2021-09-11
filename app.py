import logging
from flask import Flask, render_template, request, session , redirect, url_for, abort
from pytube import YouTube
import os

logging.basicConfig(filename="application.log", level=logging.INFO)

app= Flask(__name__)
app.secret_key="mysecretkey"


@app.route("/", methods=["GET","POST"])
def index():
    available_resolution_dict = {}
    if request.method=="POST":
        
        get_youtube_url = request.form.get("youtube_url")

        if not get_youtube_url or not get_youtube_url.startswith("https://"):
            app.logger.error("Youtube Url not found")
            abort(401)

        app.logger.info(" Youtube Url is : %s ",get_youtube_url)

        session["video_name"] = get_youtube_url
        yt_video_obj = YouTube(get_youtube_url)

        video_title= yt_video_obj.title
        video_author= yt_video_obj.author
        video_rating = yt_video_obj.rating
        video_thumbnail_url= yt_video_obj.thumbnail_url

        video_list = yt_video_obj.streams.filter(only_video=True,file_extension="mp4")
        for video in video_list:
            available_resolution_dict[video.resolution] = video.itag

        #print(available_resolution_dict)
        session["video_res_tag"] = available_resolution_dict
        return render_template("download.html",available_resolution_list= list(available_resolution_dict.keys()),video_title=video_title,
                                            video_author=video_author,video_rating=video_rating,video_thumbnail_url=video_thumbnail_url)

    return render_template("index.html")


@app.route("/download",methods=["GET","POST"])
def download():
    
    if request.method=="POST":
        if "video_name" and "video_res_tag" in session :
            download_video_name = session["video_name"]
            download_video_tag=session["video_res_tag"]

        requested_youtube_res = request.form.get("selectedLink")

        if not requested_youtube_res or requested_youtube_res == "Select resolution to download" :
            app.logger.error("No Resolution Selected")
            abort(401)
        
        app.logger.info("Video Resolution Selected : %s",requested_youtube_res)
        video_to_download = YouTube(download_video_name).streams.get_by_itag(download_video_tag[requested_youtube_res])
        address = video_to_download.download()
        app.logger.info("Files saved to location %s", address)

        return redirect(url_for("index"))

    return render_template("download.html")


if __name__=="__main__":
    app.run(debug=True)