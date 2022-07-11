## using flask to implement database and use it in a real website 

from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
AUTH_KEY="5587864edf6014223e0aa550dbd614ff"
##creating our app
app = Flask(__name__)
## we need it when we use  wTffroms
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
## optimizing our app with bootsrap so we can use it templates
Bootstrap(app)
## creating the first form that responsible for adding a rating and a review to our movie
class Myform(FlaskForm):
    review =StringField("  Review",validators=[DataRequired()])
    rating=StringField("  Rating eg 7",validators=[DataRequired()])
    submit=SubmitField()
## creating the second form that is responsible for add a movie to our database
class addform(FlaskForm):
    movie_name =StringField("Movie Name",validators=[DataRequired()])
    submit=SubmitField("Enter")

## creating our db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
## creating or table :
class Movie(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year=db.Column(db.Integer,nullable=False)
    description = db.Column(db.String(250),nullable=False)
    rating=db.Column(db.FLOAT,nullable=True)
    ranking=db.Column(db.Integer,nullable=True)
    review=db.Column(db.String(250),nullable=True)
    img_url=db.Column(db.String(250),nullable=False)
    def __repr__(self):
        return f'<Book {self.title}>'
db.create_all()
##---------------------------------------------  add a new item in the database            -------------------------------------------------------------
# new_movie = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )
# db.session.add(new_movie)
# db.session.commit()

## first route is the home when we can see our movies from the database ,we can delete update and add a movie from here
@app.route("/",methods=["POST","GET"])
def home():
    ## checking in we want to delete that
    if request.args.get('del')=="True":
        movie_id=request.args.get('id')
        print(movie_id)
        ## get  the id and then get the movie and delete it from the data base
        movie=Movie.query.get(movie_id)
        db.session.delete(movie)
        db.session.commit()
    ## read all movies from the database
    all_movies = Movie.query.order_by(Movie.rating.desc()).all()
    i=1
    ## ranking them based on their ranking
    for movie in all_movies:
        movie.ranking=i
        i+=1
    #revise
    db.session.commit()
    return render_template("index.html",movies=all_movies)
## our next route  responsible for adding a new movie into the database by using it name and send it as a paramatere to themovietdb api and get all the movies linked with that name and then send the important data to the chosen html file
@app.route("/add",methods=["POST","GET"])
def add():
    #creating our form to pass it into the html file to render it 
    form=addform()
    ## if he submited the form
    if form.validate_on_submit():
        #we get the movie name
        movie=request.form.get("movie_name")
        all_editions=requests.get(f"https://api.themoviedb.org/3/search/movie?api_key={AUTH_KEY}&query={movie}").json()["results"]
        #we get the list of movies linked with that name
        return render_template("select.html",editions=all_editions)
    return render_template("add.html",form=form)  
## this route responsible for editing a review or rating in a movie   
@app.route("/edit",methods=["POST","GET"])
def edit():
    # creating a new form object to render it into  our html file
    form=Myform()
    ## getting a  the movie id we want to get
    movie_id=request.args.get("id")
    movie_to_update = Movie.query.get(movie_id)
    ## if he submitted the form
    if form.validate_on_submit():
        ## updating our database with the new values 
        new=request.form.get("review")
        new1=request.form.get("rating")
        movie_to_update.rating = new1
        movie_to_update.review=new
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html",form=form,movie=movie_to_update)

## this route is responsible for show to the user all the movies that linked with name and he need to choose one of them 
@app.route("/choose",methods=["POST","GET"])
def choose():
    ## get the id of the movie in the website that the user choosed  to get a detailled informations  about it
    movie_id=request.args.get("id")
    info=requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={AUTH_KEY}").json()
    poster_path=f"https://image.tmdb.org/t/p/w500{info['poster_path']}"
    mov_description=info["overview"]
    mov_year=info["release_date"].split("-")[0]
    mov_title=info["title"]
    ## create a new row in the database which is basically a Movie object and then add it into it 
    new_movie=Movie(
        title = mov_title,
        year=mov_year,
        description =mov_description,
        img_url=poster_path,
    )
    db.session.add(new_movie)
    db.session.commit()
    movie_id = Movie.query.filter_by(title=mov_title).first().id
    print(movie_id)
    return redirect(url_for('edit',id=movie_id))

## run our server
if __name__ == '__main__':
    app.run(debug=True,host='192.168.56.1')

