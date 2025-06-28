
from yt_dlp import YoutubeDL
import os
from pathlib import Path
import ffmpeg
import logging
from yt_dlp.utils import DownloadError
from PySide6.QtCore import Signal, QObject
from yt_dlp.utils import DownloadError



logger = logging.getLogger('yt_download_app')

#downloader for mp4
class MyDownloader(QObject):

    error = Signal(str)#this is how we send the error to pyside
    finished = Signal()
    yey_download_complete = Signal(str)
    def __init__(self,url):
        super().__init__() #calls the constuctor of QObject , aka the QObject __init__()
        logging.basicConfig(filename='yt_errors.log' , level = logging.DEBUG, format='%(levelname)s : %(message)s : %(filename)s')
        

        self.url = url
        self.home_path = Path.home()
        self.downloads_path  = os.path.join(self.home_path,'Desktop','Downloaded_videos_yt') #C:\Users\Buzzer Tea\Desktop\Downloaded_videos_yt   is a string
        self.options_for_video = {'format':'bestvideo',
                        'outtmpl':'b',
                         'quiet': True ,
                         'cachedir': False}
        
        self.options_for_audio = {'format':'bestaudio',
                        'outtmpl':'k',
                         'quiet': True,
                          'cachedir': False,
                           'merge_output_format': None, }
        
        self.path_and_name_of_video_file = self.options_for_video['outtmpl']
        self.path_and_name_of_audio_opus_file = self.options_for_audio['outtmpl']

        self.only_opus_audio_name = os.path.basename(self.path_and_name_of_audio_opus_file)
        self.list_of_options = [self.options_for_video , self.options_for_audio]

        
        

        
      

    def check_if_video_folder_exists(self):
        downloads_path_object = Path(self.downloads_path)
        if downloads_path_object.exists() and downloads_path_object.is_dir(): #works only on path objects
            return True
        return False

    def the_with_block(self,option):
        with YoutubeDL(option) as ydl:
            try:
                ydl.download([self.url])

            except DownloadError:
                self.error.emit("Invalid URL. Please enter a valid link.")
                self.finished.emit()
            except DownloadError:
                self.error.emit("conexiunea ta la internet are viteza melcului turbat. Please try again later!")
                logger.error('internet is too slow ---> %s', 'sorries :( please try again')
                self.finished.emit()
            except Exception as e:
                logger.error('something went very wrong---> %s',e)
                self.error.emit('something went wrong ,maybe its your internet.\n call me if it persists!')
                self.finished.emit()
            
        

    def convert_audio_to_mp3(self):#youtube has opus format for audio by default 
        #actually to aac
        try:
            path_to_mp3_file_output = os.path.join(self.downloads_path,'final_mp3.mp4')
            (               #parantheses for long method calls instead of ffmpeg.imput(x).output(y).overwrite_output().run(k)

            ffmpeg.input(self.path_and_name_of_audio_opus_file)
            .output(path_to_mp3_file_output, acodec='aac')
            .overwrite_output()
            .run() #run only returns after the conversion is complete . it will throw an error if it couldnt convert for example input file dosent exist etc
            )

            os.remove(self.path_and_name_of_audio_opus_file) #delete opus file after successful conversion
            return path_to_mp3_file_output

        except ffmpeg.Error as e:
            #print(f"Conversion failed: {e}")
            logger.error('conversion failed opus --> mp3 %s' , self.only_opus_audio_name)
        except OSError as e:
            #print(f"Failed to delete opus file: {e}")
            logger.error('failed to detele opus file %s' , self.only_opus_audio_name)
    

        
    def joining_video_and_mp3(self,video ,audio, output_path_and_name):
        """
        this is how the below code acts but we dont need to assing the variabe 'stream' anymore because we call run() directly after:
           stream = ffmpeg.output(...).overwrite_output()
           ffmpeg.run(stream)"""
        
        (                                   #parantheses for long method calls instead of ffmpeg.imput(x).output(y).overwrite_output().run(k)
            ffmpeg
            .output(                        #its a rule in ffmpeg output. the first 2 arguments are inputs , 3rd argument is output_path and the rest are codecs , filters etc
                     ffmpeg.input(video), 
                     ffmpeg.input(audio),
                     output_path_and_name,
                     **{'c:a': 'copy','c:v' :'copy' } #c_v = video codec , v_a = audio codec
                     ) 
            
            .overwrite_output() #overwrite if file already exists I wont use os.remove(video) because ill set the output file path to the filepath&name of the video file so it will get overwritten my ffmpeg with the combined video + audio file.
            .run()
        )
        
        os.remove(audio)
        os.remove(video)
        logger.info('this file was combined! and audio single file deleted %s' ,output_path_and_name )
        #i dont have to return anything , the file was already stored

    def getting_metadata(self):
        not_allowed_carachters = '<>:"/\\|?*\0 -;6@#!`~%&()+=}{[]'
        sanitized_title_video = ""
        with YoutubeDL({'quiet':True}) as getting_meta_food :
            try:
                info = getting_meta_food.extract_info(self.url , download=False) #only gets a dictionary of metadata
            except Exception:
                self.error.emit("Invalid URL. Please enter a valid link! \n⸜(｡˃ ᵕ ˂)⸝♡ \n🌷☆🍵⋆｡°🍡°⋆. ࿔*:🥞")
                self.finished.emit()
                return None,None



            title = info.get('title','default_fallback_title')
            formats = info['formats']

            #metadata for video only , best possible resolution

            best_video = None #at first we dont have any value for any format so we set it to None for the first iteration
            best_audio=None
            for char in title:
                    if char not in not_allowed_carachters:
                        sanitized_title_video += char
            
            for f in formats : #we search through all formats for video-only format
                if f.get('vcodec') != 'none' and f.get('acodec') == 'none': #this is a video-only format (stream)
                    if best_video == None:
                        best_video = f
                    else:
                        if f.get('height', 0) > best_video.get('height', 0):
                            best_video = f # here we set the best_format to the highest quality video-only format, aka now it hold the entire individual format dictionary with the highest resolution
            
            #metadata for audio only
                if f.get('vcodec') == 'none' and f.get('acodec') != 'none':
                            if best_audio == None:
                                best_audio = f

            if best_video : # the dictionary of the individual format  contains a key for extension , but info dic also contains a key for extension but we use the one from format.
                ext_video = best_video.get('ext','mp4') #if an extension dosent exists it falls back to .mp4, .get() is cool !
                final_video_filename_ok = f"{sanitized_title_video}.{ext_video}"
            else:
                print('VIDEO STREAM DOSENT EXIST GUSY ------------------')


            if best_audio:
                ext_audio = best_audio.get('ext','mp3') 
                final_audio_filename_ok = f"{sanitized_title_video}1.webm"
            else:
                print('AUDIO STREAM DOSENT EXIST GUSY ------------------')



                
        return final_video_filename_ok , final_audio_filename_ok       




           

            
    

    def actual_downloading_function(self):
        
        vidyo,audyo = self.getting_metadata()
        if vidyo ==None and audyo ==None:
            return 
        self.options_for_video['outtmpl'] = os.path.join(self.downloads_path,vidyo)
        self.options_for_audio['outtmpl'] = os.path.join(self.downloads_path,audyo)
        self.path_and_name_of_video_file = self.options_for_video['outtmpl']
        self.path_and_name_of_audio_opus_file = self.options_for_audio['outtmpl']
        self.only_opus_audio_name = audyo
        full_mp3_path_fo_pathlib = Path(self.path_and_name_of_audio_opus_file)
        path_and_filename_for_mp3_no_extension = full_mp3_path_fo_pathlib.with_suffix('')
        path_and_filename_for_mp3_webm_extension =f'{path_and_filename_for_mp3_no_extension}_final.mp4'
        final_path = f'{path_and_filename_for_mp3_no_extension}_meow.mp4'
        


        if self.check_if_video_folder_exists():
            for optiony in self.list_of_options:
                self.the_with_block(optiony)

            mp3_path = self.convert_audio_to_mp3()
            self.joining_video_and_mp3(self.path_and_name_of_video_file ,mp3_path,path_and_filename_for_mp3_webm_extension)#self.path_and_name_of_audio_opus_file aka .webm . opus is just the codec
            
        else:
            os.makedirs(self.downloads_path)
            # if self.check_if_video_folder_exists():
            for optiony in self.list_of_options:
                    self.the_with_block(optiony)

            mp3_path = self.convert_audio_to_mp3()
            self.joining_video_and_mp3(self.path_and_name_of_video_file ,mp3_path,path_and_filename_for_mp3_webm_extension)

        self.yey_download_complete.emit('🎀🎉Yey download complete!!!🌷🍰\n                        (๑>◡<๑)')
        self.finished.emit()
           
            







#downloader_object = MyDownloader('https://www.youtube.com/watch?v=qDcFryDXQ7U')
#downloader_object.actual_downloading_function()