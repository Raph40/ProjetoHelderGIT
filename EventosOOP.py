import datetime

class Evento:
    #Definida os tipos de cada argumento do construtor
    nome: str = ""
    descricao: str = ""
    data_inicio: datetime
    data_fim: datetime
    organizador: str = ""
    tipo: str = ""
    capacidade: int = 0
    condicao_idade: int = 0

    #Construtor
    def __init__(self, nome, descricao, data_inicio, data_fim, organizador, tipo, capacidade, condicao_idade):
        if not nome:
            raise Exception("Campo Nome obrigatório!")
        if not isinstance(nome, str):
            raise Exception("O campo Nome só aceita texto!")

        if not descricao:
            raise Exception("Campo Descrição obrigatório!")
        if not isinstance(descricao, str):
            raise Exception("O campo Descrição só aceita texto!")

        if not data_inicio:
            raise Exception("Campo Data de Inicio obrigatório!")

        if not data_fim:
            raise Exception("Campo Data do Fim obrigatório!")

        if not organizador:
            raise Exception("Campo Organizador obrigatório!")
        if not isinstance(organizador, str):
            raise Exception("O campo Organizador só aceita texto!")

        if not tipo:
            raise Exception("Campo Tipo obrigatório!")
        if not isinstance(tipo, str):
            raise Exception("O campo Tipo só aceita texto!")

        if not condicao_idade:
            raise Exception("Campo Condição da Idade de Participação obrigatório!")
        if not isinstance(condicao_idade, int):
            raise Exception("O campo Condição da Idade de Participação só aceita numeros inteiros!")
        if condicao_idade < 0:
            raise Exception("Condição da Idade de Participação tem que ser maior que 0!")

        if not capacidade:
            raise Exception("Campo Capacidade obrigatório!")
        if not isinstance(capacidade, int):
            raise Exception("O campo Capacidade de Participantes só aceita numeros inteiros!")
        if capacidade < 0:
            raise Exception("Capacidade de Participantes tem que ser maior que 0!")

        self.nome = nome
        self.descricao = descricao
        self.data_inicio = data_inicio
        self.data_fim = data_fim
        self.organizador = organizador
        self.tipo = tipo
        self.capacidade = capacidade
        self.condicao_idade = condicao_idade
        self.atividades = []
        self.lista_entradas = []

    #Encapsulamento GET
    def get_nome(self):
        return self.nome
    def get_descricao(self):
        return self.descricao
    def get_data_inicio(self):
        return self.data_inicio
    def get_data_fim(self):
        return self.data_fim
    def get_organizador(self):
        return self.organizador
    def get_tipo(self):
        return self.tipo
    def get_capacidade(self):
        return self.capacidade
    def get_condicao_idade(self):
        return self.condicao_idade
    def get_atividades(self):
        return self.atividades
    def get_lista_entradas(self):
        return self.lista_entradas

    #Encapsulamento SET
    def set_nome(self, nome):
        if not nome:
            raise Exception("Campo Nome obrigatório!")
        if not isinstance(nome, str):
            raise Exception("O campo Nome só aceita texto!")
        self.nome = nome
    def set_descricao(self, descricao):
        if not descricao:
            raise Exception("Campo Descrição obrigatório!")
        if not isinstance(descricao, str):
            raise Exception("O campo Descrição só aceita texto!")
        self.descricao = descricao
    def set_data_inicio(self, data_inicio):
        if not data_inicio:
            raise Exception("Campo Data de Inicio obrigatório!")
        self.data_inicio = data_inicio
    def set_data_fim(self, data_fim):
        if not data_fim:
            raise Exception("Campo Data do Fim obrigatório!")
        self.data_fim = data_fim
    def set_organizador(self, organizador):
        if not organizador:
            raise Exception("Campo Organizador obrigatório!")
        if not isinstance(organizador, str):
            raise Exception("O campo Organizador só aceita texto!")
        self.organizador = organizador
    def set_tipo(self, tipo):
        if not tipo:
            raise Exception("Campo Tipo obrigatório!")
        if not isinstance(tipo, str):
            raise Exception("O campo Tipo só aceita texto!")
        self.tipo = tipo
    def set_atividades(self, atividades):
        self.atividades = atividades
    def set_capacidade(self, capacidade):
        if not capacidade:
            raise Exception("Campo Capacidade obrigatório!")
        if capacidade < 0:
            raise Exception("Capacidade de Participantes tem que ser maior que 0!")
        if not isinstance(capacidade, int):
            raise Exception("O campo Capacidade de Participantes só aceita numeros inteiros!")
        self.capacidade = capacidade
    def set_condicao_idade(self, condicao_idade):
        if not condicao_idade:
            raise Exception("Campo Condição da Idade de Participação obrigatório!")
        if not isinstance(condicao_idade, int):
            raise Exception("O campo Condição da Idade de Participação só aceita numeros inteiros!")
        if condicao_idade < 0:
            raise Exception("Condição da Idade de Participação tem que ser maior que 0!")
        self.condicao_idade = condicao_idade
    def set_lista_entradas(self, lista_entradas):
        self.lista_entradas = lista_entradas

    #Função para adicionar atividades á lista de atividades no construtor
    def adicionar_atividades(self, atividades):
        self.atividades.append(atividades)