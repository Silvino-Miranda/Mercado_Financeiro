import csv

from models.position import Position


class PositionRepository:
    def __init__(self, arquivo_csv='position.csv', delimitador=';'):
        self.arquivo_csv = arquivo_csv
        self.delimitador = delimitador
        self.campos = ['entry_date', 'exit_date', 'ativo', 'position', 'entry_price', 'exit_price']

    def ler_dados(self):
        with open(self.arquivo_csv, mode='r', newline='', encoding='utf-8') as arquivo:
            leitor = csv.DictReader(arquivo, delimiter=self.delimitador)
            return [Position(**linha) for linha in leitor]

    def escrever_dados(self, dados):
        with open(self.arquivo_csv, mode='w', newline='', encoding='utf-8') as arquivo:
            escritor = csv.DictWriter(arquivo, fieldnames=self.campos, delimiter=self.delimitador)
            escritor.writeheader()
            escritor.writerows([vars(posicao) for posicao in dados])

    def criar(self, posicao: Position):
        dados = self.ler_dados()
        dados.append(posicao)
        self.escrever_dados(dados)

    def ler(self, filtro=None):
        dados = self.ler_dados()
        if filtro:
            dados = [
                posicao for posicao in dados
                if all(getattr(posicao, k) == v for k, v in filtro.items())
            ]
        return dados

    def atualizar(self, filtro, atualizacao: dict):
        dados = self.ler_dados()
        for posicao in dados:
            if all(getattr(posicao, k) == v for k, v in filtro.items()):
                for chave, valor in atualizacao.items():
                    setattr(posicao, chave, valor)
        self.escrever_dados(dados)

    def deletar(self, filtro):
        dados = self.ler_dados()
        dados = [
            posicao for posicao in dados
            if not all(getattr(posicao, k) == v for k, v in filtro.items())
        ]
        self.escrever_dados(dados)