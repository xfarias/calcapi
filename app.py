from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)
api = Api(app)
app.config['DEBUG'] = True
client = MongoClient("mongodb://localhost:27017/db") # conexao com via socket

db = client.MathDB # criando uma coleção dentro do mongoDB

users = db["Users"] # criando um documento usuário


class Registrar(Resource):
    def post(self):
        data = request.get_json()

        nome = data["nome"]
        senha = data["senha"]

        hash_senha = bcrypt.hashpw(senha.encode('utf8'), bcrypt.gensalt())

        users.insert_one({
            "Nome": nome,
            "Senha": hash_senha,
            "Operacao": "",
            "Resultado": 0,
            "Tokens": 10
        })

        retJson = \
            {
                "Status": 200,
                "Mensagem": "Login cadastrado com sucesso"
            }

        return jsonify(retJson)


def vdados(data):
    if "x" not in data or "y" not in data:
        return 301
    else:
        return 200


def vsenha(usuario, senha):
    hash = users.find({
        "Nome": usuario
    })[0]["Senha"]
    if bcrypt.hashpw(senha.encode('utf8'), hash) == hash:
        return True
    else:
        return False


def ctoken(usuario):
    tokens = users.find({
        "Nome":usuario
    })[0]["Tokens"]
    return tokens


class Soma(Resource): #using class based
    def post(self):

        # Passo 1:  Receber os dados
        data = request.get_json()

        # Passo 2: Verificar os dados
        status_data = vdados(data)

        if status_data != 200:
            error = {
                "Status": 301,
                "Message": "Faltando Variável x ou y"
            }
            return jsonify(error)
        else:

            x = data["x"]
            y = data["y"]
            usuario = data["nome"]
            senha = data["senha"]
            operacao = "Soma"
            resultado = int(x+y)

            senha_correta = vsenha(usuario, senha)

            if not senha_correta:
                json = {
                        "status": 302
                }
                return jsonify(json)

            num_tokens = ctoken(usuario)
            if num_tokens <= 0:
                json = {
                    "status": 302
                }
                return jsonify(json)

            users.update_one({
                "Nome": usuario
            }, {
                "$set": {
                    "Resultado": resultado,
                    "Operacao": operacao,
                    "Tokens": num_tokens - 1
                }
            })

            # criando retorno via dicionario
            json  =\
                {
                "soma": resultado,
                "status": 200
                }
            return jsonify(json)


class Info(Resource):
    def post(self):

        data = request.get_json()

        usuario = data["nome"]
        senha = data["senha"]

        senha_correta = vsenha(usuario, senha)

        if not senha_correta:

            json = {"status": 302,
                    "mensagem": "Credenciais Inválidas"
                    }
            return jsonify(json)

        num_tokens = ctoken(usuario)
        if num_tokens <= 0:
            json = {
                "status": 302,
                "mensagem": "Tokens insuficientes"
            }
            return jsonify(json)

        res = users.find({
                "Nome": usuario
             })[0]['Resultado']

        json = {
            "status": 200,
            "resultado": res,
            "tokens": num_tokens

        }
        return jsonify(json)


class Usuarios(Resource):
    def get(self):
        usuarios = []
        for s in users.find():
            usuarios.append({'nome': s['Nome'], 'resultado': s['Resultado'], 'operacao': s['Operacao'], 'tokens': s['Tokens']})

        return jsonify(usuarios)




api.add_resource(Soma, '/soma') # adicionando a classe/rota
api.add_resource(Registrar, '/registrar')
api.add_resource(Info, '/info')
api.add_resource(Usuarios, '/usuarios')
@app.route('/')
def index():
    return 'Hello World'


if __name__ == "__main__":
    app.run()
