from pymongo import MongoClient

class Conexao:
    client: None
    db: None
    TrabalhoHelder_Eventos: None
    TrabalhoHelder_Utilizadores: None

    @staticmethod
    def estabelecer():
        Conexao.client = MongoClient('mongodb://localhost:27017/')
        db = Conexao.client['Eventos_Helder']
        Conexao.TrabalhoHelder_Eventos = db['collEventos']
        Conexao.TrabalhoHelder_Utilizadores = db['collUtilizadores']

    #Encapsulamento GET
    def get_client(self):
        return self.client
    def get_db(self):
        return self.db
    def get_TrabalhoHelder_Eventos(self):
        return self.TrabalhoHelder_Eventos
    def get_TrabalhoHelder_Utilizadores(self):
        return self.TrabalhoHelder_Utilizadores

    #Encapsulamento SET
    def set_client(self, client):
        self.client = client
    def set_db(self, db):
        self.db = db
    def set_TrabalhoHelder_Eventos(self, TrabalhoHelder_Eventos):
        self.TrabalhoHelder_Eventos = TrabalhoHelder_Eventos
    def set_TrabalhoHelder_Utilizadores(self, TrabalhoHelder_Utilizadores):
        self.TrabalhoHelder_Utilizadores = TrabalhoHelder_Utilizadores