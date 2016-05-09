#
# This script gets top 100 speeches' text and videos from americanrhetoric.com
# and gets forced alignment data
#
from __future__ import unicode_literals
from bs4 import BeautifulSoup
from pytube import YouTube
from pprint import pprint
import youtube_dl
import urllib
import shutil
import os
import requests
import json
# convention = ['speeches/convention2004/barackobama2004dnc.htm','speeches/convention2004/algore2004dnc.htm',
#                 'speeches/convention2004/alsharpton2004dnc.htm', 'speeches/convention2004/jimmycarter2004dnc.htm',
#                 'speeches/convention2004/billclinton2004dnc.htm','speeches/convention2004/ilanawexler2004dnc.htm',
#                 'speeches/convention2004/johnkerry2004dnc.htm','speeches/convention2008/barackobama2008dnc.htm',
#                 'speeches/convention2008/wjclinton2008dnc.htm', 'speeches/convention2008/algore2008dnc.htm',
#                 'speeches/convention2008/tedkennedy2008dnc.htm'
#                 ]

videoLinks = []

convention = ['speeches/richardnixoncambodia.html']
# 
# 
# 
# 
# Data collector for transcript, audio, and video
# 
# 
# 
# 

# 0. scrape top 100 speeches that have videos
# 1. download the transcript into txt file
# 2. download the video
# 3. strip the audio from the video, download as mp3

# step 0: getting links from top100 index page
def getLinks():
    url = "http://www.americanrhetoric.com/barackobamaspeeches.htm"
    markup = urllib.urlopen(url)
    soup = BeautifulSoup(markup, "html5lib")
    # first get links from top 100 index page
    allLinks = soup.find_all('a',href=True)
    # valid links is the array of links to speeches
    validLinks = []
    for link in allLinks:
        l = link['href']
        if ((l.find("speeches") == 0) and (".htm" in l)):
            validLinks.append(l)
    return validLinks

def checkForVideo(link):
    url = "http://www.americanrhetoric.com/"+link
    markup = urllib.urlopen(url)
    soup = BeautifulSoup(markup, "html5lib")
    if (soup.find('embed') != None):
        vidSrc = soup.find('embed').get("src")
        return vidSrc
    return None

def getTitle(link):
    url = "http://www.americanrhetoric.com/"+link
    markup = urllib.urlopen(url)
    soup = BeautifulSoup(markup, "html5lib")
    filename = soup.find("meta", {"name":"Title"})['content']
    filename = filename.replace(" ","_")
    filename = filename.replace(".","")
    filename = filename.replace("/","")
    return filename

def downloadVideo(entireUrl,title):
    # get the id part
    part1 = entireUrl.split('http://www.youtube.com/v/',2)[1]
    part2 = part1.split('&',1)[0]
    # part2='FB9OUcPENL0'
    # print(part2)
    realLink = "https://www.youtube.com/watch?v="+part2
    obj = {"title":title,"link":realLink}
    videoLinks.append(obj)
    yt = YouTube(realLink)
    print yt.get_videos()
    fn = yt.filename
    yt.set_filename(title)
    video = yt.get('mp4')
    video.download('videos/')

def downloadAll(listLinks):
    print "downloading..."
    for link in listLinks:
    # link = listLinks[1]
    # step 1,2: download text and video
        vidCheck = checkForVideo(link)
        if (vidCheck != None):
            try:
                title = getTitle(link)
                print title
                print vidCheck
                downloadVideo(vidCheck, title)
            except:
                print("error in downloading video")
            downloadTranscript(link,title)
    print "done"

def downloadTranscript(link,title):
    url = "http://www.americanrhetoric.com/"+link
    markup = urllib.urlopen(url)
    soup = BeautifulSoup(markup, "html5lib")
    words = soup.find_all('font',face="Verdana",size="2")
    obj = open("speeches/"+title+".txt","w")
    for word in words:
        a = word.get_text()
        a = a.strip('\n')
        obj.seek(0,2)
        try:
            obj.write(a)
        except:
            print ("minor: writing error")
            continue
    obj.close()

def downloadAudio():
    for obj in videoLinks:
        link = obj['link']
        name = obj['title']
        ydl_opts = {
        'outtmpl': 'audio/'+name+'.%(ext)s',
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
            }],
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            print("link: ",link)
            ydl.download([link])

# 
# 
# 
# 
# Use Gentle Force Aligner to get jsons of
# when words are spoken 
# 
# 
# 
# 

def gentle(filename):
# Open gentle server and the following with save transcribed data
    url = 'http://localhost:8765/transcriptions?async=false'
    txtFileName = 'speeches/demConvention/'+filename+".txt"
    mp3FileName = 'audio/demConvention/'+filename+".mp3"
    if not(os.path.isfile(txtFileName) and os.path.isfile(mp3FileName)):
        print(filename,"not valid file name.")
        return
    if (os.path.getsize(txtFileName) == 0):
        print (filename, "size 0.")
        return
    print("transcribing ",filename)
    jsonFileName = 'alignedJsons/demConvention/'+filename+".json"
    if (os.path.isfile(jsonFileName)):
        print (filename, "already aligned.")
        return   
    files = {'audio':open(mp3FileName,'r'),'transcript':open(txtFileName,'r')}
    r = requests.post(url, files=files)
    result = r.json()
    with open(jsonFileName,'w') as f:
        json.dump(result,f,indent=4)
    print("done transcribing")


# Routines for collecting data and aligning
def dataCollect():
    # speechLinks = getLinks()
    speechLinks=convention
    downloadAll(speechLinks)
    downloadAudio()

def align():
    # iterate over files and align with mp3
    for i in os.listdir(os.getcwd()+"/speeches/demConvention/"):
        filename = i.split('.txt',1)[0]
        gentle(filename)


# downloadAll(convention)
dataCollect()
# align()

