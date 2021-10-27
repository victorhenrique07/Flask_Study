from flask import Flask, request, Response
from flask_sqlalchemy import SQLAlchemy
import json

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mariadb+pymysql://root:94082@localhost/API_Filmes'
db = SQLAlchemy(app)


class Filmes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filme = db.Column(db.String(80), unique=True, nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    genero = db.Column(db.String(80), nullable=False)

    def to_json(self):
        return {"ID": self.id, "filme": self.filme, "ano": self.ano, "genero": self.genero}


@app.route('/home', methods=["GET"])
def home():
    return {"Home": "Home"}


# rota para cadastro de filmes.
@app.route("/home/cadastro-filme", methods=["POST"])
def cadastraFilme():
    body = request.get_json()

    # Validar  se veio os parametros
    try:
        filmes = Filmes(filme=body["filme"], ano=body["ano"], genero=body["genero"])
        db.session.add(filmes)
        db.session.commit()
        return gera_response(201, "filmes", filmes.to_json(), "Criado com sucesso")
    except Exception as e:
        print(e)
        return gera_response(400, "filmes", {}, "Erro")


# rota para retornar todos os filmes cadastrados.
@app.route('/home/filmes', methods=["GET"])
def retornatodosFilmes():
    filmes_classe = Filmes.query.all()
    filmes_json = [filmes.to_json() for filmes in filmes_classe]

    return gera_response(200, "filmes", filmes_json)


# rota para retornar um filme especifico
@app.route('/home/filmes/<id>', methods=["GET"])
def retornaUmFilme(id):
    filmes_classe = Filmes.query.filter_by(id=id).first()
    filmes_json = filmes_classe.to_json()
    return gera_response(200, "filmes", filmes_json)


# rota para deletar um filme
@app.route('/home/delete/<id>', methods=["DELETE"])
def deletaFilme(id):
    filmes_classe = Filmes.query.filter_by(id=id).first()
    try:
        db.session.delete(filmes_classe)
        db.session.commit()
        return gera_response(200, "filmes", filmes_classe.to_json(), "Filme deletado com sucesso.")
    except Exception as e:
        print("Erro: ", e)
        return gera_response(200, "filmes", {}, "Erro ao deletar.")


# rota para atualizar um filme.
@app.route('/home/refresh/<id>', methods=["PUT"])
def atualizaFilme(id):
    filmes_classe = Filmes.query.filter_by(id=id).first()
    body = request.get_json()
    try:
        if 'filme' in body:
            filmes_classe.filme = body['filme']
        if 'ano' in body:
            filmes_classe.ano = body['ano']
        if 'genero' in body:
            filmes_classe.genero = body['genero']
        db.session.add(filmes_classe)
        db.session.commit()
        return gera_response(200, 'Filme', {}, 'Dados atualizados com sucesso.')
    except Exception as e:
        print(e)
        return gera_response(304, 'filmes', {}, 'Os dados não foram atualizados.')


def gera_response(status, nome_do_conteudo, conteudo, mensagem=False):
    body = {nome_do_conteudo: conteudo}
    if mensagem:
        body["mensagem"] = mensagem

    return Response(json.dumps(body), status=status, mimetype="application/json")


if __name__ == '__main__':
    app.run(debug=True)
