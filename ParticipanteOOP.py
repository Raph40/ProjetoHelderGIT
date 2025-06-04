import random
import re

class Participante:
    #Definida os tipos de cada argumento do construtor
    nome: str = ""
    idade: int = 0
    nif: int = 0
    telefone: int = 0

    #Construtor
    def __init__(self, nome, idade, nif, telefone):
        if not nome:
            raise Exception("Campo Nome obrigatório!")
        if not isinstance(nome, str):
            raise Exception("O campo Nome só aceita texto!")

        if not idade:
            raise Exception("Campo Idade obrigatório!")
        if not isinstance(idade, int):
            raise Exception("O campo Idade só aceita texto!")
        if idade < 0:
            raise Exception("Idade tem que ser maior que 0!")

        if not nif:
            raise Exception("Campo NIF obrigatório!")
        if not re.match(r"\d{9}", str(nif)):
            raise Exception("NIF contem 9 numeros!")
        if not isinstance(nif, int):
            raise Exception("O campo NIF só aceita texto!")

        if not telefone:
            raise Exception("Campo Telefone obrigatório!")
        if not re.match(r"\d{9}", str(telefone)):
            raise Exception("Telefone contem 9 numeros!")
        if not isinstance(telefone, int):
            raise Exception("O campo Telefone só aceita texto!")

        self.nome = nome
        self.idade = idade
        self.nif = nif
        self.telefone = telefone
        self.codigo_gerado = self.codigo_acesso()
        self.comentario = ""
        self.comentario_emocao = ""

    #Encapsulamento GET
    def get_nome(self):
        return self.nome
    def get_idade(self):
        return self.idade
    def get_nif(self):
        return self.nif
    def get_telefone(self):
        return self.telefone
    def get_comentario(self):
        return self.comentario
    def get_comentario_emocao(self):
        return self.comentario_emocao

    #Encapsulamento SET
    def set_nome(self, nome):
        if not nome:
            raise Exception("Campo Nome obrigatório!")
        if not isinstance(nome, str):
            raise Exception("O campo Nome só aceita texto!")
        self.nome = nome
    def set_idade(self, idade):
        if not idade:
            raise Exception("Campo Idade obrigatório!")
        if idade < 0:
            raise Exception("Idade tem que ser maior que 0!")
        if not isinstance(idade, int):
            raise Exception("O campo Idade só aceita texto!")
        self.idade = idade
    def set_nif(self, nif):
        if not nif:
            raise Exception("Campo NIF obrigatório!")
        if not re.match(r"\d{9}", str(nif)):
            raise Exception("NIF contem 9 numeros!")
        if not isinstance(nif, int):
            raise Exception("O campo NIF só aceita texto!")
        self.nif = nif
    def set_telefone(self, telefone):
        if not telefone:
            raise Exception("Campo Telefone obrigatório!")
        if not re.match(r"\d{9}", str(telefone)):
            raise Exception("Telefone contem 9 numeros!")
        if not isinstance(telefone, int):
            raise Exception("O campo Telefone só aceita texto!")
        self.telefone = telefone

    #Função para gerar o codigo de acesso aos eventos quando é criado um objeto evento
    def codigo_acesso(self):
        return random.sample(range(1000, 10000), k=1)[0]

    #Função para adicionar o comentario no contrutor
    def adicionar_comentario(self, comentario):
        self.comentario = comentario

    #Função para adicionar o comentario_emocao no construtor
    def adicionar_comentario_emocao(self, comentario_emocao):
        self.comentario_emocao = comentario_emocao

