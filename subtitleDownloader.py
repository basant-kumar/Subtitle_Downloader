#!/usr/bin/python2-3
#---------------------------------------------------------------------------------------
#This scripts download subtitle for your movie or tv series in 5 sec #Enjoy
#created by Basant Kumar

#---------------------------------------------------------------------------------------

import os,sys,zipfile,time,logging,requests,shutil
import urllib2
#import urllib.request
from bs4 import BeautifulSoup

VERSION=sys.version_info[0]
if VERSION==2:
	import urllib2
if VERSION==3:
	import urllib.request

def get_hash(file_path):
	read_size = 64 * 1024
	with open(file_path, 'rb') as f:
		data = f.read(read_size)
		f.seek(-read_size, os.SEEK_END)
		data += f.read(read_size)
	return hashlib.md5(data).hexdigest()


def subtitleDownloader(file_path):
	try:
		#download subtitle from subtitle Database
		logging.info("Searching in Subtitle Database")
		root, extension = os.path.splitext(file_path)
		if extension not in [".mp4",".mkv",".avi",".mov",".3gp",".mpg",".rm",".wmv",".flv",".3g2",".vob",".mpeg"]:
			return
		if os.path.exists(root+".srt"):
			return
		headers={'User-Agent':'SubDB/1.0 (subtitleDownloader/1.0; https://github.com/basant-kumar/Subtitle_Downloader)'}
		url="http://api.thesubdb.com/?action=download&hash="+get_hash(file_path)+"&language=en"
		
		if VERSION==3:
			#for python version 3
			req=urllib.request.Request(url,None,headers)
			response=urllib.request.urlopen(req).read()
		if VERSION==2:
			#for python version 2
			req=urllib2.Request(url,'',headers)
			response=urlib2.urlopen(req).read()
		

		with open(root+".srt",'wb') as subfile:
			subfile.write(response)
			logging.info("Subtitle successfully downloaded for "+ file_path)
	except:
		#if subtitle not found in subdb then download from subscene.com
		subtitleDownloader2(file_path)



def subtitleDownloader2(file_path):
	try:
		logging.info("Started searching in subscene.com database")
		root,extension=os.path.splitext(file_path)
		if extension not in [".mp4",".mkv",".avi",".mov",".3gp",".mpg",".rm",".wmv",".flv",".3g2",".vob",".mpeg"]:
			return
		if os.path.exists(root+".srt"):
			return
		j=-1
		root2=root
		for i in range(0,len(root)):
			if(root[i]=="\\"):
				j=i
		root=root2[j+1:]
		root2=root2[:j+1]
		
		r=requests.get("http://subscene.com/subtitles/release?q="+root);
		soup=BeautifulSoup(r.content,"lxml")
		a_tags=soup.find_all("a")
		href=""
		for i in range(0,len(a_tags)):
			spans=a_tags[i].find_all("span")
			if (len(spans)==2 and spans[0].get_text().strip()=="English"):
				href=a_tags[i].get("href").strip()
		if(len(href)>0):
			r=requests.get("http://subscene.com"+href);
			soup=BeautifulSoup(r.content,"lxml")
			lin=soup.find_all('a',attrs={'id':'downloadButton'})[0].get("href")
			r=requests.get("http://subscene.com"+lin);
			soup=BeautifulSoup(r.content,"lxml")
			subfile=open(root2+".zip",'wb')
			for chunk in r.iter_content(100000):
				subfile.write(chunk)
			subfile.close()
			time.sleep(1)
			#unzip subfile
			zip=zipfile.ZipFile(root2+".zip")
			zip.extractall(root2)
			zip.close()
			os.unlink(root2+".zip")
			shutil.move(root2+zip.namelist()[0],os.path.join(root2,root+".srt"))
			logging.info("subtitle successfully downloaded for "+file_path)		

	except:
		#Ignore Error and then continue
		print("Error in fetching subtitle for "+file_path)
		print("Error",sys.exc_info())
		logging.error("Error in fetching subtitle for "+file_path + str(sys.exc_info()))



def main():
	root , _ = os.path.splitext(sys.argv[0])
	logging.basicConfig(filename=root+'.log',level=logging.INFO)
	logging.info("Started searching subtitles for "+ str(sys.argv))
	if len(sys.argv)==1:
		print("You need to enter at least one parameter")
		sys.exit(1)
	for path in sys.argv:
		if os.path.isdir(path):
			for dir_path ,_, file_names in os.walk(path):
				for filename in file_names:
					file_path=os.path.join(dir_path,filename)
					subtitleDownloader(file_path)
		else:
			subtitleDownloader(path)

if __name__=="__main__":main()
