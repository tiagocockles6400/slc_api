from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect
from urllib.parse import unquote

from sqlalchemy.exc import IntegrityError

from model import Session, Produto, Lista
from logger import logger
from schemas import *
from flask_cors import CORS

info = Info(title="Minha API", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

# definindo tags
home_tag = Tag(name="Documentação", description="Seleção de documentação: Swagger, Redoc ou RapiDoc")
produto_tag = Tag(name="Produto", description="Adição, visualização e remoção de produtos à base")
lista_tag = Tag(name="Lista", description="Adição, visualização e remoção de listas à base")


@app.get('/', tags=[home_tag])
def home():
    """Redireciona para /openapi, tela que permite a escolha do estilo de documentação.
    """
    return redirect('/openapi')


@app.put('/produto', tags=[produto_tag], responses={"200": ProdutoViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def upd_produto(form: ProdutoSchema):
    """Atualiza um Produto na base de dados

    Retorna uma representação dos produtos.
    """
    
    produtoNovo = Produto(
        id_lista=form.id_lista,
        nome=form.nome,
        quantidade=form.quantidade,
        valor=form.valor)

    logger.debug(f"Atualizando produto de nome: '{produtoNovo.nome}'")
    try:
        # criando conexão com a base
        session = Session()
        # buscando o produto
        produtoAntigo = session.query(Produto).filter(Produto.id==form.id).first()

        if produtoAntigo:
            # produtoAntigo.nome = produtoNovo.nome
            produtoAntigo.quantidade = produtoNovo.quantidade
            produtoAntigo.valor = produtoNovo.valor

            # efetivando o comando de update na tabela
            session.commit()
            logger.debug(f"Alterado o produto de nome: '{produtoAntigo.nome}'")
            return apresenta_produto(session.query(Produto).filter(Produto.id==form.id).first()), 200
        else:
            error_msg = "Não foi possível atualizar o item :/"
            logger.warning(f"Erro ao atualizar produto '{produtoAntigo.nome}', {error_msg}")
            return {"mesage": error_msg}, 400
        
    except IntegrityError as e:
        # como a duplicidade do nome é a provável razão do IntegrityError
        error_msg = "Produto de mesmo nome já salvo na base :/"
        logger.warning(f"Erro ao atualizar produto '{produtoNovo.nome}', {error_msg}")
        return {"mesage": error_msg}, 409

    except Exception as e:
        # caso um erro fora do previsto
        error_msg = "Não foi possível salvar o item :/"
        logger.warning(f"Erro ao atualizar produto '{produtoNovo.nome}', {error_msg}")
        return {"mesage": error_msg}, 400

@app.post('/produto', tags=[produto_tag], responses={"200": ProdutoViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_produto(form: ProdutoSchema):
    """Adiciona um novo Produto à base de dados

    Retorna uma representação dos produtos e comentários associados.
    """
    produto = Produto(
        id_lista=form.id_lista,
        nome=form.nome,
        quantidade=form.quantidade,
        valor=form.valor)
    logger.debug(f"Adicionando produto de nome: '{produto.nome}'")
    try:
        # criando conexão com a base
        session = Session()
        # adicionando produto
        session.add(produto)
        # efetivando o comando de adição de novo item na tabela
        session.commit()
        logger.debug(f"Adicionado produto de nome: '{produto.nome}'")
        return apresenta_produto(produto), 200

    except IntegrityError as e:
        # como a duplicidade do nome é a provável razão do IntegrityError
        error_msg = "Produto de mesmo nome já salvo na base :/"
        logger.warning(f"Erro ao adicionar produto '{produto.nome}', {error_msg}")
        return {"mesage": error_msg}, 409

    except Exception as e:
        # caso um erro fora do previsto
        error_msg = "Não foi possível salvar novo item :/"
        logger.warning(f"Erro ao adicionar produto '{produto.nome}', {error_msg}")
        return {"mesage": error_msg}, 400


@app.get('/produto', tags=[produto_tag], responses={"200": ProdutoViewSchema, "404": ErrorSchema})
def get_produto(query: ProdutoBuscaIdSchema):
    """Faz a busca por um Produto cadastrado.

    Retorna uma representação da listagem de produtos.
    """
    logger.debug(f"Coletando produtos")
    # criando conexão com a base
    session = Session()
    # fazendo a busca
    produto = session.query(Produto).filter(Produto.id == query.id_produto).all()

    if not produto:
        # se não há produtos cadastrados
        return {"produto": ""}, 200
    else:
        logger.debug(f"%d produtos encontrados" % len(produto))
        # retorna a representação de produto
        print(produto)
        return apresenta_produtos(produto), 200

@app.get('/produtos', tags=[produto_tag], responses={"200": ListagemProdutosSchema, "404": ErrorSchema})
def get_produtos(query: ProdutoBuscaSchema):
    """Faz a busca por todos os Produto cadastrados de uma determinada lista.

    Retorna uma representação da listagem de produtos.
    """
    logger.debug(f"Coletando produtos")
    # criando conexão com a base
    session = Session()
    # fazendo a busca
    produtos = session.query(Produto).filter(Produto.id_lista == query.id_lista).all()

    if not produtos:
        # se não há produtos cadastrados
        return {"produtos": []}, 200
    else:
        logger.debug(f"%d produtos encontrados" % len(produtos))
        # retorna a representação de produto
        print(produtos)
        return apresenta_produtos(produtos), 200


@app.delete('/produto', tags=[produto_tag], responses={"200": ProdutoDelSchema, "404": ErrorSchema})
def del_produto(query: ProdutoBuscaIdSchema):
    """Deleta um Produto a partir do id de produto informado

    Retorna uma mensagem de confirmação da remoção.
    """
    logger.debug(f"Deletando dados sobre produto #{query.id_produto}")
    # criando conexão com a base
    session = Session()
    # fazendo a remoção
    count = session.query(Produto).filter(Produto.id == query.id_produto).delete()
    session.commit()

    if count:
        # retorna a representação da mensagem de confirmação
        logger.debug(f"Deletado produto #{query.id_produto}")
        return {"mesage": "Produto removido", "id": query.id_produto}
    else:
        # se o produto não foi encontrado
        error_msg = "Produto não encontrado na base :/"
        logger.warning(f"Erro ao deletar produto #'{query.id_produto}', {error_msg}")
        return {"mesage": error_msg}, 404


@app.post('/lista', tags=[lista_tag], responses={"200": ListaViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_lista(form: ListaSchema):
    """Adiciona uma nova Lista à base de dados

    Retorna uma representação das listas.
    """
    lista = Lista(
        nome=form.nome,
        tipo=form.tipo,
        qtd_itens=form.qtd_itens,
        valor_total=form.valor_total)
    logger.debug(f"Adicionando lista de nome: '{lista.nome}'")
    try:
        # criando conexão com a base
        session = Session()
        # adicionando lista
        session.add(lista)
        # efetivando o comando de adição de novo item na tabela
        session.commit()
        logger.debug(f"Adicionado lista de nome: '{lista.nome}'")
        return apresenta_lista(lista), 200

    except IntegrityError as e:
        # como a duplicidade do nome é a provável razão do IntegrityError
        error_msg = "Lista de mesma nome e tipo já salva na base :/"
        logger.warning(f"Erro ao adicionar lista '{lista.nome}', {error_msg}")
        return {"mesage": error_msg}, 409

    except Exception as e:
        # caso um erro fora do previsto
        error_msg = "Não foi possível salvar novo item :/"
        logger.warning(f"Erro ao adicionar lista '{lista.nome}', {error_msg}")
        return {"mesage": error_msg}, 400


@app.get('/listas', tags=[lista_tag], responses={"200": ListagemListasSchema, "404": ErrorSchema})
def get_listas():
    """Faz a busca por todos as listas cadastradas

    Retorna uma representação da Lista de Produtos.
    """
    logger.debug(f"Coletando as listas ")
    # criando conexão com a base
    session = Session()
    # fazendo a busca
    listas = session.query(Lista).all()

    if not listas:
        # se não há listas cadastradas
        return {"listas": []}, 200
    else:
        logger.debug(f"%d listas encontradas" % len(listas))
        # retorna a representação de lista
        print(listas)
        return apresenta_listas(listas), 200


@app.get('/lista', tags=[lista_tag], responses={"200": ListaViewSchema, "404": ErrorSchema})
def get_lista(query: ListaBuscaSchema):
    """Faz a busca por uma lista a partir do id da lista

    Retorna uma representação das listas.
    """
    lista_id = query.id
    logger.debug(f"Coletando dados sobre lista #{lista_id}")
    # criando conexão com a base
    session = Session()
    # fazendo a busca
    lista = session.query(Lista).filter(Lista.id == lista_id).first()

    if not lista:
        # se a lista não foi encontrado
        error_msg = "Lista não encontrado na base :/"
        logger.warning(f"Erro ao buscar lista '{lista_id}', {error_msg}")
        return {"mesage": error_msg}, 404
    else:
        logger.debug(f"Lista encontrada: '{lista.nome}'")
        # retorna a representação de lista
        return apresenta_lista(lista), 200


@app.delete('/lista', tags=[lista_tag], responses={"200": ListaDelSchema, "404": ErrorSchema})
def del_lista(query: ListaBuscaSchema):
    """Deleta uma lista a partir do id da lista informada

    Retorna uma mensagem de confirmação da remoção.
    """
    print(query.id)
    logger.debug(f"Deletando dados sobre lista #{query.id}")
    # criando conexão com a base
    session = Session()
    # fazendo a remoção
    count = session.query(Lista).filter(Lista.id == query.id).delete()
    session.commit()

    if count:
        # retorna a representação da mensagem de confirmação
        logger.debug(f"Deletado lista #{query.id}")
        return {"mesage": "lista removida", "id": query.id}
    else:
        # se a lista_id não foi encontrada
        error_msg = "Lista não encontrada na base :/"
        logger.warning(f"Erro ao deletar lista #'{query.id}', {error_msg}")
        return {"message": error_msg}, 404

    # retorna a representação de lista
    return apresenta_lista(lista), 200
