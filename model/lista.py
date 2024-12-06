from sqlalchemy import Column, String, Integer, Float, Date
from typing import Union

from  model import Base


class Lista(Base):
    __tablename__ = 'lista'

    id = Column("pk_lista", Integer, primary_key=True)
    tipo = Column(Integer)
    nome = Column(String(120), unique=True)
    valor_total = Column(Float)
    qtd_itens = Column(Integer)

    def __init__(self, tipo:str, qtd_itens:int, valor_total:float, nome:str):
        """
        Cria uma Lista

        Arguments:
            tipo: tipo de lista.
            quantidade: quantidade total somada da lista
            valor_total: valor total somado da lista
            data: data de quando a lista foi inserido à base
        """
        self.nome = nome
        self.tipo = tipo
        self.qtd_itens = qtd_itens
        self.valor_total = valor_total
            
