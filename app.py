import json
import os
import requests
from flask import Flask, request
from textwrap import wrap
import matplotlib.pyplot as plt
from flask import render_template
from operator import itemgetter
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, \
 	VideoUnavailable, TooManyRequests, TranscriptsDisabled, \
 	NoTranscriptAvailable
from transformers import pipeline
from pytube import YouTube
from flask import Flask, request, render_template

# Create an instance of FLask oject. 
app = Flask(__name__, template_folder='templates',static_folder='static')

# Youtube developer API
api_key = 'AIzaSyCUKN1xNCoHv9W-QYb0e-zrRiRS0CKRoSw'
pwd = os.getcwd()

# Function will take care of transcript related exceptions.
def get_transcript(video_id):
    try: 
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        res = ""
        for i in transcript:
            res += " " + i['text']
        return res
    except VideoUnavailable: 
        error = "Video not available"
        return render_template('summary.html', summary=error)
    except TranscriptsDisabled:
        error = "Transcripts disabled for this video."
        return render_template('summary.html', summary=error)
    except NoTranscriptAvailable:
        error = 'Tanscripts are not available for this video.'
        return render_template('summary.html', summary=error)
    except NoTranscriptFound:
        error = "Transcripts not found for this video."
        return render_template('summary.html', summary=error)
    except:
        error = "Could not find transcript for this video link."
        return render_template('summary.html', summary=error)


# Get Channel Statistics for Data analysis.
def get_stats(channel_id):
    # channel stats url
    stats_url = "https://www.googleapis.com/youtube/v3/channels?part=statistics&id=" \
        + channel_id + "&key=" + api_key

    # Get stats and load in json using requests and json package
    stats_data = requests.get(stats_url).text
    
    json_data = json.loads(stats_data)
    
    try:
        items = json_data['items'][0]
        stats = items['statistics']
    except KeyError:
        return render_template('summary.html', summary= "Unable to fetch stats")

    # video_id url for respective channel.
    channel_url = "https://www.googleapis.com/youtube/v3/search?key=" + api_key \
        + "&channelId=" + channel_id + "&part=snippet,id&order=date"

    # Dict for storing individual video stats 
    video_data = {}

    # Get video id and load in json using requests and json package
    vid_data = requests.get(channel_url).text
    
    json_data = json.loads(vid_data)

 
    # Only go for 10 page is Youtube API rendering capacity might exhaust.
    for index in range(10):
        try:
            for i in json_data['items']:
                # Title of the video.
                title = i['snippet']['title']

                # Publishing data and time of the video.
                published_at = i['snippet']['publishedAt']
                
                # Extract only if id is of video and not playlist.
                if i['id']['kind'] == 'youtube#video':
                    video_id = i['id']['videoId']
                    video_data[video_id] = {'title': title, 'publishedAt': published_at}
        except KeyError:
            return render_template('summary.html', summary="Unable to fetch items")
 
        # See if next page is avilable or not, if avilable save.
        next_page_token = json_data.get("nextPageToken", None)

        # If next page  is not None, append it url.
        if next_page_token is not None:
            # Next page video stats url for respective channel.
            channel_url = channel_url+ "&pageToken=" + next_page_token
         
            # Get video_id and load in json using requests and json package
            vid_data = requests.get(channel_url).text
            
            json_data = json.loads(vid_data)

        else: break

    # Get stats for all videos using video_id.
    for video_id in video_data:
        for part in ["snippet", "statistics"]:
        
            # video stats url for respective channel.
            video_url = "https://www.googleapis.com/youtube/v3/videos?part=" + \
                         part + "&id=" + video_id + "&key=" + api_key
            
            # Get stats and load in json using requests and json package
            vid_data = requests.get(video_url).text
            
            json_data = json.loads(vid_data)

            try:
                items = json_data['items'][0]
                data = items[part]
            except KeyError as e:
                return render_template('summary.html', summary="Unable to fetch")

            video_data[video_id].update(data)

    # Return dict of dict of both channel statistics and video_data.
    return {channel_id: {"channel_statistics": stats, "video_data": video_data}}
            
# Function to show values of each bar on it.
def addlabels(x,y):
    for i in range(len(x)):
        plt.text(i, y[i], y[i], ha = 'center')

def plot_graphs(data):

    #extracting channelIDs and videoIds from json data
    channel_id, stats = data.popitem()
    video_data = stats["video_data"]
    channel_data = stats["channel_statistics"]
    v_data = list(video_data.items())       #converting dictionary to lists, for ease of operations

    #print(v_data[0][1]['title'])

    names_likes = {}
    names_comment = {}
    names_views = {}
    for_ratio = []

    views_to_likes = []
    views_to_comments = []

            #creating dictionaries and lists containing video titles with number of like, views et cetra
    for i in v_data:
        names_likes[i[1]['title']] = int(i[1]['likeCount'])         #dictionary of form {title : number of likes}
        names_comment[i[1]['title']] = int(i[1]['commentCount'])    #dictionary of form {title : number of comments}
        names_views[i[1]['title']] = int(i[1]['viewCount'])         ##dictionary of form {title : number of views}
        # for_ratio[i[1]['title']] = int(i[1]['viewCount'])
        # for_ratio[i[1]['title']] = int(i[1]['likeCount'])
        # for_ratio[i[1]['title']] = int(i[1]['commentCount'])
        for_ratio.append([i[1]['title'], int(i[1]['viewCount']), int(i[1]['likeCount']), int(i[1]['commentCount'])])            #list containing title and corresponding numbers


        #etracting ratio between views, likes, and comments from "for_ratio list" 
    for i in for_ratio:
        try:
            likes_ratio = int(i[1]/i[2])
            comments_ratio = int(i[1]/i[3])
            views_to_comments.append([i[0], comments_ratio])
            views_to_likes.append([i[0], likes_ratio])
        except ZeroDivisionError:
            error = 'Unable to find transcript'
            return render_template('summary.html', summary=error)


        #sorting all the lists to get top 5 entries of use
    names_comment = sorted(names_comment.items(), key=lambda x:x[1], reverse=True)
    names_views = sorted(names_views.items(), key=lambda x:x[1], reverse=True)
    names_likes = sorted(names_likes.items(), key=lambda x:x[1], reverse=True)

    views_to_likes = sorted(views_to_likes, key=itemgetter(1))
    views_to_comments = sorted(views_to_comments, key=itemgetter(1))
    

    top5likes_num = []
    top5likes_titles = []
    top5views_num = []
    top5views_titles = []
    top5comment_num = []
    top5comment_titles = []
    top5likes_ratio = []
    top5comment_ratio = []
    
        #extracting top 5 entries of all lists for graph plotting
    top5likes = names_likes[0:5]
    top5views = names_views[0:5]
    top5comment = names_comment[0:5]

    top5likes_ratio = views_to_likes[0:5]
    top5comment_ratio = views_to_comments[0:5]


        #breaking all the 2D lists into two lists for x-axis and y-axis
    top5comment_num = [i[1] for i in top5comment]
    top5comment_titles = [i[0] for i in top5comment]

    top5views_num = [i[1] for i in top5views]
    top5views_titles = [i[0] for i in top5views]

    top5likes_num = [i[1] for i in top5likes]
    top5likes_titles = [i[0] for i in top5likes]

    top5likes_ratio_num = [i[1] for i in top5likes_ratio]
    top5likes_ratio_titles = [i[0] for i in top5likes_ratio]


    top5comment_ratio_num = [i[1] for i in top5comment_ratio]
    top5comment_ratio_titles = [i[0] for i in top5comment_ratio]


        #wrapping title names to better fit in graphs
    top5comment_titles = ['\n' .join(wrap(l,18)) for l in top5comment_titles]
    top5likes_titles = ['\n' .join(wrap(l,18)) for l in top5likes_titles]
    top5views_titles = ['\n' .join(wrap(l,18)) for l in top5views_titles]
    top5likes_ratio_titles = ['\n' .join(wrap(l,18)) for l in top5likes_ratio_titles]
    top5comment_ratio_titles = ['\n' .join(wrap(l,18)) for l in top5comment_titles]

                #-----------------PLOTTING GRAPHS-------------------------------
    x = [0,1,2,3,4]

    plt.figure(figsize=(10,7))
    plt.bar(top5comment_titles, top5comment_num)
    plt.xticks(x, top5comment_titles)
    plt.title('Top 5 commented videos')
    plt.xlabel("Video Names")
    plt.ylabel("Number of comments")
    addlabels(top5comment_titles, top5comment_num)
    plt.savefig(pwd+"/static/topcommented.png",bbox_inches='tight',dpi=100)
    # plt.show()

    plt.figure(figsize=(10,7))
    plt.bar(top5likes_titles, top5likes_num)
    plt.xticks(x, top5likes_titles)
    plt.title('Most liked videos')
    plt.xlabel("Video Names")
    plt.ylabel("Number of likes")
    addlabels(top5likes_titles, top5likes_num)
    plt.savefig(pwd+"/static/topliked.png",bbox_inches='tight',dpi=100)
    # plt.show()

    plt.figure(figsize=(10,7))
    plt.bar(top5views_titles, top5views_num)
    plt.xticks(x, top5views_titles)
    plt.xlabel("Video Names")
    plt.title('Most Viewed videos')
    plt.ylabel("Number of views")
    addlabels(top5views_titles, top5views_num)
    plt.savefig(pwd+"/static/topviewed.png",bbox_inches='tight',dpi=100)
    # plt.show()

    plt.figure(figsize=(10,7))
    plt.bar(top5likes_ratio_titles, top5likes_ratio_num)
    plt.xticks(x, top5likes_ratio_titles)
    plt.xlabel("Video Names")
    plt.title('Lowest ratio of Views by Likes')
    plt.ylabel("Views by Likes Ratio")
    addlabels(top5likes_ratio_titles, top5likes_ratio_num)
    plt.savefig(pwd+"/static/toplikeratio.png",bbox_inches='tight',dpi=100)
    # plt.show()

    plt.figure(figsize=(10,7))
    plt.bar(top5comment_ratio_titles, top5comment_ratio_num)
    plt.xticks(x, top5comment_ratio_titles)
    plt.xlabel("Video Names")
    plt.title('Lowest ratio of Views by Comments')
    plt.ylabel("Views by Comments Ratio")
    addlabels(top5comment_ratio_titles, top5comment_ratio_num)
    plt.savefig(pwd+"/static/topcommentratio.png",bbox_inches='tight',dpi=100)
    # plt.show()
    

# Summarize transcript using hugging face transformer.
def summary(transcript):
    
    # Pipeline for summarize transcript.
    summarizer = pipeline('summarization')

    # Transformer accpets 1024 words for summarization, 
    # Hence spltiing the transcript according to requirement.
    num_iters = int(len(transcript)/1000)
    summarized_text = []
 
    if (num_iters == 0):
        return transcript
 
    # Summarize every split and append to create complete summaziration.
    for i in range(0, num_iters + 1):
        start = 0
        start = i * 1000
        end = (i + 1) * 1000
        
        out = summarizer(transcript[start:end])
        out = out[0]
        out = out['summary_text']
        
        summarized_text.append(out)

    # Return complete summarization.
    return summarized_text
    

final_result = []

# Defining resource endpoints, Flask call start() on invoking /api/summarize
@app.route('/api/summarize', methods = ['GET'])
def start():

    # Save youtube_url fetched from chrome extention
    youtube_url = request.args.get("youtube_url")
    yotube_url = youtube_url.split("=")
 
    # Fetch video_id from url.
    try:
        video_id = yotube_url[1]
        youtube_obj = YouTube(youtube_url)
    except IndexError:
        return render_template('summary.html', summary="URL not compatible.")

    # Fetch channel_id for channel stats. 
    channel_id = youtube_obj.channel_id

    # Call get_stats for channel and video stats required for data analysis. 
    data = get_stats(channel_id)
    plot_graphs(data)

    # Fetch transcript using video_id.
    transcript = get_transcript(video_id)
    # print(transcript)
    result = summary(transcript)
    final_result = result

    # Render summary.html.
    return render_template('summary.html', summary=result)

# server the app when this file is run
if __name__ == '__main__':
    app.run()