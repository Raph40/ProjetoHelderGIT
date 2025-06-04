import datetime

class Atividades:
    #Definida os tipos de cada argumento do construtor
    atividade: str = ""
    hora_inicio: datetime
    hora_fim: datetime
    capacidade: int = 0
    tipo_atividade: str = ""
    local_atividade: str = ""

    #Construtor
    def __init__(self, atividade, hora_inicio, hora_fim, local_atividade, capacidade, tipo_atividade):
        if not isinstance(atividade, str):
            raise Exception("O campo Atividades só aceita texto!")
        self.atividade = atividade
        self.hora_inicio = hora_inicio
        self.hora_fim = hora_fim
        self.capacidade = capacidade
        self.tipo_atividade = tipo_atividade
        self.local_atividade = local_atividade
        self.lista_inscritos = []

    #Encapsulamento GET
    def get_atividade(self):
        return self.atividade
    def get_hora_inicio(self):
        return self.hora_inicio
    def get_hora_fim(self):
        return self.hora_fim
    def get_tipo_atividade(self):
        return self.tipo_atividade
    def get_capacidade(self):
        return self.capacidade
    def get_local_atividade(self):
        return self.local_atividade

    #Encapsulamento SET
    def set_atividade(self, atividade):
        if not atividade:
            raise Exception("Campo Atividade obrigatório!")
        if not isinstance(atividade, str):
            raise Exception("O campo Atividades só aceita texto!")
        self.atividade = atividade
    def set_hora_inicio(self, hora_inicio):
        if not hora_inicio:
            raise Exception("Campo Hora de Inicio obrigatório!")
        self.hora_inicio = hora_inicio
    def set_hora_fim(self, hora_fim):
        if not hora_fim:
            raise Exception("Campo Hora do Fim obrigatório!")
        self.hora_fim = hora_fim
    def set_tipo_atividade(self, tipo_atividade):
        self.tipo_atividade = tipo_atividade
    def set_capacidade(self, capacidade):
        self.capacidade = capacidade
    def set_local_atividade(self, local_atividade):
        self.local_atividade = local_atividade

    #Função para inserir participantes ás atividades que estão inscritos
    def AdicionarInscritos(self, inscritos):
        self.lista_inscritos.append(inscritos)