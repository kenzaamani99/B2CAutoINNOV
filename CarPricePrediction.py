
from flask import Flask, render_template,request,send_file
from flask_wtf import FlaskForm
from wtforms import FileField , SubmitField
from werkzeug.utils import secure_filename
from wtforms.validators import InputRequired
import os
import pandas as pd
import pickle
import numpy as np


app=Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['UPLOAD_FOLDER']='static\\files'

ML_model = pickle.load(open("XGBoostModel2.pkl",'rb'))
ML_model_File = pickle.load(open("XGBoostModelFile.pkl",'rb'))
car = pd.read_csv("CleanedData.csv")

class UploadFileForm(FlaskForm):
    file=FileField("File",validators=[InputRequired()])
    submit = SubmitField("Upload File")

@app.route('/File',methods=['GET','POST'])
def loadfile(): 
    form = UploadFileForm()
    if form.validate_on_submit():
        file=form.file.data
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file.filename)))
        data=pd.read_excel(file,skiprows=6)
        data['Date d\'immatriculation'] = pd.to_datetime(data['Date d\'immatriculation'], format='%d/%m/%Y')
        for i in data.index: 
            data['Kilométrage'][i] = "".join(data['Kilométrage'][i].split())
        Estimated_price = []
        for i in data.index: 
           Marque = data["Marque"][i]
           Model = data["Modèle"][i]
           Carburant = data["Carburant"][i]
           Kilometrage = int(data["Kilométrage"][i])
           Type= data["Carrosserie"][i]
           Annee= int((pd.DatetimeIndex(data['Date d\'immatriculation']).year)[i])
           Puissance = int(data["Puissance en Ch(Din)"][i])
           prediction = ML_model_File.predict(pd.DataFrame([[Marque,Model,Carburant,Kilometrage,Type,Puissance,Annee]],columns=['Marque', 'Modèle', 'Carburant', 'Kilométrage',
            'Typevéhicule', 'PuissanceDIN', 'Année']))
           Estimated_price.append(str(np.round(prediction[0],2)))
           
        print(Estimated_price)
        #data["Prix estimé"]=Estimated_price
        data.insert(2, 'Prix estimé', Estimated_price)
        data = data.drop(['Unnamed: 0','Unnamed: 17','Unnamed: 18'],axis=1)
        data.to_excel("static\\files\\output.xlsx")
        
        
    return render_template("file.html",form=form)

@app.route("/download")
def download_file():
    p="static\\files\\output.xlsx"
    return send_file(p,as_attachment=True)


@app.route('/Formulaire')
def index():
    Marques=sorted(car['Marque'].unique())
    Models=sorted(car['Modèle'].unique())
    Carburant=car['Carburant'].unique()
    Boitedevitesse=car['Boitedevitesse'].unique()    
    return render_template("index.html",Marques=Marques,Models=Models,Carburant=Carburant,BoiteVitesse=Boitedevitesse)

@app.route('/')
def home():    
    return render_template("home.html")

@app.route('/Test')
def testfichier():    
    return render_template("fichier.html")

@app.route('/predict',methods=['POST'])
def predict():
   

        marque = request.form.get('marque')
        model =  request.form.get('car_model')
        annee = int(request.form.get('annee')) 
        carburant = request.form.get('carburant')
        boite = request.form.get('boite')
        kilom = int(request.form.get('km'))
        puissancef =int(request.form.get('pf')) 
        prediction = ML_model.predict(pd.DataFrame([[marque,model,carburant,kilom,boite,puissancef,annee]],columns=['Marque', 'Modèle', 'Carburant', 'Kilométrage',
       'Boitedevitesse', 'Puissancefiscale', 'Année']))
       
        return str(np.round(prediction[0],2))
   
    
    

    

if __name__=="__main__":
    app.run(debug=True)