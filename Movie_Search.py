import os

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import urllib.parse
import urllib.request
import json

with open("tmdb_key.txt","r") as f:
    TMDB_KEY=f.readline()

LOGO="logo.ico"


class NotEmpty(Exception):
    pass

class NotInDatabase(Exception):
    pass
class TMDBSearchWidget(QWidget):
    recherche=False
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setStyleSheet("border: 1px solid; border-color:black; background-color:grey;")
        self.setWindowTitle("Movie research")

        self.setWindowIcon(QIcon(LOGO))

        self.uiText = QLabel("Which movie do you want to search?")
        self.uiText.setStyleSheet("border: 0px solid;")

        self.uiSearchButton_text=QLineEdit()
        self.uiSearchButton_text.setStyleSheet("background-color:white;")

        self.uiSearchButton_bouton=QPushButton("Search")
        self.uiSearchButton_bouton.setStyleSheet("QPushButton::hover""{""background-color : red;""}")

        self.uiListe=QListWidget()

        self.uiMovieTitle=QLabel("Title")
        self.uiMovieTitle.setStyleSheet("border: 0px solid;")
        self.uiMovieTitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.uiMovieTitle_text=QLineEdit()

        self.uiSummary=QLabel("Summary")
        self.uiSummary.setStyleSheet("border: 0px solid;")
        self.uiSummary.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.uiSummary_scroll=QScrollArea()

        self.uiSummary_text=QTextEdit("")

        self.uiPicture=QLabel()
        self.uiPicture.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.uiPicture.setStyleSheet("border: 0px solid;")

        self.Error_message=QMessageBox()


        self.uiSearchButton_bouton.clicked.connect(self.update_title)
        self.uiSearchButton_bouton.clicked.connect(self.search_movie)
        self.uiListe.itemSelectionChanged.connect(self.tire_resume_image)


        self.grid=QGridLayout()
        self.grid.setSpacing(10)
        self.grid.setColumnMinimumWidth(0,10)


        self.grid.setColumnStretch(0, 0)
        self.grid.setColumnStretch(1, 0)
        self.grid.setColumnStretch(2,1)
        self.grid.setColumnStretch(3,4)
        self.grid.setRowStretch(0, 1)
        self.grid.setRowStretch(1, 0)
        self.grid.setRowStretch(3,1)
        self.setLayout(self.grid)

        self.grid.addWidget(self.uiText, 0, 0)
        self.grid.addWidget(self.uiSearchButton_text,0,1)
        self.grid.addWidget(self.uiSearchButton_bouton,0,2)

    def keyPressEvent(self, event):
        if event.key()==16777220:
            self.update_title()
            self.search_movie()

    def update_title(self,texte=None):
        if texte is None:
            self.setWindowTitle(f"Results for : {self.uiSearchButton_text.text()}")
        else:
            self.setWindowTitle(f"Details of the movie: {texte}")


    def search_movie(self):
        try:
            movie=self.uiSearchButton_text.text()
            if movie=="":
                raise NotEmpty
            params = urllib.parse.urlencode({"query": movie, "api_key": TMDB_KEY, "language": "eng"})
            r = urllib.request.urlopen(f'https://api.themoviedb.org/3/search/movie?{params}')
            objet = json.load(r)
            if len(objet["results"])==0:
                raise NotInDatabase
            if TMDBSearchWidget.recherche is True:
                self.uiListe.clear()
                self.uiSummary.hide()
                self.uiSummary_text.clear()
                self.uiMovieTitle.hide()
                self.uiMovieTitle_text.clear()
                self.uiSummary_text.hide()
                self.uiPicture.clear()
                self.uiMovieTitle_text.hide()
            for i in range(len(objet["results"])):
                title=objet["results"][i]["title"]
                try:
                    release_date=objet["results"][i]["release_date"]
                except KeyError:
                    continue
                if release_date=="":
                    release_date="unknown"
                description=(f'Movie {i+1}\nTitle : {title}\nRelease_date : {release_date}\n')
                self.uiListe.addItem(description)
                TMDBSearchWidget.recherche=True
            self.grid.addWidget(self.uiListe, 1, 0, 3, 2)
        except NotEmpty:
            self.Error_message.setText(f"Please insert a movie title!")
            self.Error_message.exec()
            self.uiSearchButton_text.clear()
        except NotInDatabase:
            self.Error_message.setText(f"The movie {movie} isn't in our database!")
            self.Error_message.exec()
            self.uiSearchButton_text.clear()
        except urllib.error.URLError:
            self.Error_message.setText(f"Please check your internet connection\nIf this error keep showing then please reinstall requirements.txt\nUse : pip install -r requirements.txt")
            self.Error_message.exec()



    def tire_resume_image(self):
        try:
            film = self.uiSearchButton_text.text()
            params = urllib.parse.urlencode({"query": film, "api_key": TMDB_KEY, "language": "eng"})
            r = urllib.request.urlopen(f'https://api.themoviedb.org/3/search/movie?{params}')
            objet = json.load(r)
            for index in self.uiListe.selectedIndexes():
                titre=str(objet["results"][index.row()]["title"])
                resume=(".\n\n".join(objet["results"][index.row()]["overview"].split(". ")))
                lien_de_l_affiche = objet["results"][index.row()]["poster_path"]
                with open("image.jpg", "wb") as f:
                    f.write(urllib.request.urlopen(f"https://image.tmdb.org/t/p/w500{lien_de_l_affiche}").read())
                image=QPixmap("image.jpg")
                image2=image.scaledToWidth(300)
                self.uiPicture.setPixmap(image2)
                os.remove("image.jpg")
                self.uiMovieTitle_text.setText(titre)
                self.uiSummary_text.setText(resume)
                self.update_title(titre)
            self.grid.addWidget(self.uiMovieTitle, 1, 2)
            self.grid.addWidget(self.uiSummary, 2, 2)
            self.grid.addWidget(self.uiMovieTitle_text, 1, 3)
            self.grid.addWidget(self.uiSummary_text, 2, 3)
            self.grid.addWidget(self.uiPicture, 3, 3)
            if TMDBSearchWidget.recherche is True:
                self.uiSummary.show()
                self.uiMovieTitle.show()
                self.uiSummary_text.show()
                self.uiMovieTitle_text.show()
        except urllib.error.HTTPError:
            self.search_movie()
            self.Error_message.setText(f"Something is wrong with this movie,sorry for the disagreement")
            self.Error_message.exec()

if __name__ == '__main__':
    app=QApplication([])
    w=TMDBSearchWidget()
    w.showMaximized()
    app.exec()



