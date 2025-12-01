import os
import csv
from flask import Flask, render_template, url_for, request

app = Flask(__name__)

#Definindo ambiente para modo desenvolvimento (debug)
os.environ['FLASK_DEBUG'] = 'True'
app.debug = os.environ.get('FLASK_DEBUG', 'True') == 'True'


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/historia')
def historia():
    return render_template("historia.html")

@app.route('/sobre')
def sobre():
    return render_template("sobre.html")

@app.route('/ranking')
def glossario():

    glossario_de_termos = []

    with open('carreiras_tech.csv', newline='', encoding='utf-8') as arquivo:
        reader = csv.reader(arquivo, delimiter=',')
        for linha in reader:
            glossario_de_termos.append(linha)

    return render_template("glossario.html",
                           glossario=glossario_de_termos)

@app.route('/contato')
def contato():
    return render_template("contato.html")

@app.route( "/criar_termo", methods=['POST', ])
def criar_termo():
    nome = request.form['nome']
    email = request.form['email']
    assunto = request.form['assunto']
    mensagem = request.form[mensagem]

    with open()


if __name__ == '__main__':
    app.run()


