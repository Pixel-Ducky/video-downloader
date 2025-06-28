from PySide6.QtWidgets import QApplication , QMainWindow , QPushButton,QLineEdit,QMessageBox
import sys
from PySide6.QtCore import Qt, QThread, Signal
from main_file import MyDownloader
from pathlib import Path
from PySide6.QtGui import  QIcon , QPixmap

class MainGui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("youtube/pinterest dwonloader ")
        self.setGeometry(500, 300, 600, 350)
        self.input_url = QLineEdit(self)
        self.input_url.setGeometry(50,80,500,30)
        self.input_url.setPlaceholderText('Enter the video url')
        
        

        self.setStyleSheet("""

        QMainWindow{
                        background-image: url("beach_eli.jpg");
                        background-repeat: no-repeat;
                        background-position:center;
                        }


        """)

        #initialize
        #self.my_downloader = MyDownloader(user_input)
        
        #button
        self.button = QPushButton(self)
        self.button.setText('search')
        self.button.setGeometry(260,250,70,40)
        self.button.clicked.connect(self.getting_url)

        self.button.setStyleSheet("""
            QPushButton {
                border-radius: 10px;
                padding: 6px;
                background-color: #4CAF50;
                color: white;
                font-weight: bold;       
                font-size: 16px;          
                font-family: "Arial";
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        self.my_downloader = None


    def getting_url(self):
        user_input = self.input_url.text()
        print(user_input)
        if user_input:
            
            self.button.setEnabled(False) #this disables the button while the downoader runs
            self.button.setStyleSheet('background-color : #fcc342;border-radius:10px;padding:6px;color:white;font-weight:bold;font-size:16px;font-family:"Arial"')

            #create the thread
            self.my_downloader = MyDownloader(user_input)
            self.thready = QThread()
            self.my_downloader.moveToThread(self.thready) #this "puts" my_downloader in it's own  background thread
            self.thready.started.connect(self.my_downloader.actual_downloading_function) #this line tells the thread what to do WHEN it starts , aka it will run my downloader yt-dlp logic

            #connect signals KEEP IN MIND THAT WE ONLY MAKE REFERENCES TO FUNCTIONS NOT CALL THEM ex : show_error  NOT show_error()
            #its just like a pointer that points to a function instead of directly running it.
            

            #lambda makes a nameless small function on the fly.self.my_downloader.error.connect() emits only 1 error but my show_error function needs 2 arguments
            #this is why we need to use an instermediary small function that accepts only 1 argument (with the other being hardcoded) and then with that information calls show_error.
            #lambda has a hidden return statement that returns whatever we wrote in it aka show_error 
            # and you might wonder why dosent this crash if it returns ? well it turns out that Pyside ignores returns in this context.

            self.my_downloader.error.connect(self.handle_error)  # connect signal
            self.my_downloader.yey_download_complete.connect(self.yey_download_done)
            

            #now what happens after my_downloader is done downloaidng the video and remuxing.
            self.my_downloader.finished.connect(self.thready.quit) #takes object out of thread
            self.my_downloader.finished.connect(lambda : [self.button.setStyleSheet("""QPushButton{
                                                                                    background-color :#4CAF50 ;
                                                                                     border-radius:10px;
                                                                                    padding:6px;
                                                                                    color:white;
                                                                                    font-weight:bold;
                                                                                    font-size:16px;
                                                                                    font-family:Arial}
                                                                                    QPushButton:hover {
                                                                                    background-color: #45a049;
                                                                                    }
                                                                                    """),self.button.setEnabled(True)])
            #this syntax is just to avoid writing down with def anothher small function.

            self.my_downloader.finished.connect(self.my_downloader.deleteLater) #deletes the individual object from memory after its done its job
            self.thready.finished.connect(self.thready.deleteLater)#deletes the thread from memory . why? because it takes space and may lead to a memory dump.
            
            #actually start thread for real.
            

            self.thready.start()

            
        else:
            print('enter a valid url')
            self.show_error('woops be careful',"enter a valid url!\nYou can't leave the input box blank.\nദ്ദി(ᵔ-ᵔ)   🍀🥥")


    def show_error(self,title, message):
        QMessageBox.critical(self, title, message,QMessageBox.Ok)
         
    def handle_error(self,msg):
        self.show_error('woops be careful',msg)

    def yey_download_done(self, msg):
        cute_box = QMessageBox(self)
        #cute_box.information(self,'yuppy yey!',msg)
        cute_box.setWindowTitle('yuppy congrats!')
        cute_box.setText(msg)
        flower_path = 'flower2.jfif'
        flower_icon = QPixmap(flower_path).scaled(100,100,Qt.KeepAspectRatio , Qt.SmoothTransformation)
        cute_box.setIconPixmap(flower_icon)
        cute_box.exec()
        
        

app = QApplication(sys.argv)
window = MainGui()
window.show()
app.exec()