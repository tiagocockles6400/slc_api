from pydantic import BaseModel
from typing import Optional, List
from model.lista import Lista
from sqlalchemy import Date


class ListaSchema(BaseModel):
    """ Define como uma nova lista a ser inserido deve ser representado
    """
    id: int = 1
    nome: str  = "Lista de 2020-01-01"
    tipo: int = 1
    qtd_itens: int = 9
    valor_total: float = 150

class ListaBuscaSchema(BaseModel):
    """ Define como deve ser a estrutura que representa a busca. Que será
        feita apenas com base no id da lista.
    """
    id: str = "1"


class ListagemListasSchema(BaseModel):
    """ Define como uma listagem de lista será retornada.
    """
    listas:List[ListaSchema]


def apresenta_listas(listas: List[Lista]):
    """ Retorna uma representação da lista seguindo o schema definido em
        ListaViewSchema.
    """
    result = []
    for lista in listas:
        result.append({
            "id": lista.id,
            "nome": lista.nome,
            "tipo": lista.tipo,
            "qtd_itens": lista.qtd_itens,
            "valor_total": lista.valor_total,
        })

    return {"listas": result}


class ListaViewSchema(BaseModel):
    """ Define como uma lista será retornado: lista.
    """
    id: int = 1
    nome: str = "Lista de 2020-01-01"
    tipo: int = 1
    qtd_itens: int = 12
    valor_total: float = 550.50


class ListaDelSchema(BaseModel):
    """ Define como deve ser a estrutura do dado retornado após uma requisição
        de remoção.
    """
    mesage: str
    nome: str

def apresenta_lista(lista: Lista):
    """ Retorna uma representação da lista seguindo o schema definido em
        ListaViewSchema.
    """
    return {
        "id": lista.id,
        "nome": lista.nome,
        "tipo": lista.tipo,
        "qtd_itens": lista.qtd_itens,
        "valor_total": lista.valor_total
    }
