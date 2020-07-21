from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from pymongo import MongoClient


app = Flask(__name__)
api = Api(app)
app.config['DEBUG'] = True
client = MongoClient("mongodb://db:27017") # conexao com via socket

db = client.MathDB # criando uma coleção dentro do mongoDB

users = db["Users"] # criando um documento usuário


def vdados(data):
    if "x" not in data or "y" not in data:
        return 301
    else:
        return 200


class Sum(Resource): #using class based
    def post(self):

        # Passo 1:  Receber os dados
        data = request.get_json()


        # Passo 2: Verificar os dados
        status_data = vdados(data)

        if status_data != 200:
            mapError = {
                "Status": 301,
                "Message": "Faltando Variável x ou y"
            }
            return jsonify(mapError)
        else:

            x = data["x"]
            y = data["y"]
            soma = int(x+y)
            # criando retorno via dicionario
            retJson  =\
                {
                "soma": soma,
                "status": 200
                }
            return jsonify(retJson)


api.add_resource(Sum, '/sum') # adicionando a classe/rota


@app.route('/')
def index():
    return 'Hello World'


if __name__ == "__main__":
    app.run()
