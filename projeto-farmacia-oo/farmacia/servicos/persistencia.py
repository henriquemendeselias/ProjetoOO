import json
import os
from farmacia.servicos.estoque import Estoque
from farmacia.entidades.pessoa import Cliente, Funcionario
from farmacia.entidades.produto import Produto
from farmacia.servicos.venda import HistoricoVendas, Venda, Orcamento
from typing import List, Dict, Tuple

CAMINHO_DADOS = "dados"
CLIENTES_FILE = os.path.join(CAMINHO_DADOS, "clientes.json")
FUNCIONARIOS_FILE = os.path.join(CAMINHO_DADOS, "funcionarios.json")
ESTOQUE_FILE = os.path.join(CAMINHO_DADOS, "estoque.json")
HISTORICO_FILE = os.path.join(CAMINHO_DADOS, "historico.json")
ORCAMENTOS_FILE = os.path.join(CAMINHO_DADOS, "orcamentos.json")
VENDAS_PAUSADAS_FILE = os.path.join(CAMINHO_DADOS, "vendas_pausadas.json")


def _garantir_diretorio_dados():
    if not os.path.exists(CAMINHO_DADOS):
        os.makedirs(CAMINHO_DADOS)

def salvar_pessoas(clientes: List[Cliente], funcionarios: List[Funcionario]):
    _garantir_diretorio_dados()
    
    try:
        dados_clientes = [cliente.to_dict() for cliente in clientes]
        with open(CLIENTES_FILE, 'w', encoding='utf-8') as f:
            json.dump(dados_clientes, f, indent=4, ensure_ascii=False)
    except IOError as e:
        print(f"Erro ao salvar clientes: {e}")
    except Exception as e:
        print(f"Erro inesperado ao processar clientes: {e}")

    try:
        dados_funcionarios = [func.to_dict() for func in funcionarios]
        with open(FUNCIONARIOS_FILE, 'w', encoding='utf-8') as f:
            json.dump(dados_funcionarios, f, indent=4, ensure_ascii=False)
    except IOError as e:
        print(f"Erro ao salvar funcionários: {e}")
    except Exception as e:
        print(f"Erro inesperado ao processar funcionários: {e}")

def salvar_estoque(estoque: Estoque):
    _garantir_diretorio_dados()
    
    try:
        dados_estoque = estoque.to_dict()
        with open(ESTOQUE_FILE, 'w', encoding='utf-8') as f:
            json.dump(dados_estoque, f, indent=4, ensure_ascii=False)
    except IOError as e:
        print(f"Erro ao salvar estoque: {e}")
    except Exception as e:
        print(f"Erro inesperado ao processar dados do estoque: {e}")

def salvar_historico(historico: HistoricoVendas):
    _garantir_diretorio_dados()
    
    try:
        dados_historico = historico.to_dict()
        with open(HISTORICO_FILE, 'w', encoding='utf-8') as f:
            json.dump(dados_historico, f, indent=4, ensure_ascii=False)
    except IOError as e:
        print(f"Erro ao salvar histórico: {e}")
    except Exception as e:
        print(f"Erro inesperado ao processar dados do histórico: {e}")

def salvar_orcamentos(orcamentos: List[Orcamento]):
    _garantir_diretorio_dados()
    try:
        dados_orcamentos = [orc.to_dict() for orc in orcamentos]
        with open(ORCAMENTOS_FILE, 'w', encoding='utf-8') as f:
            json.dump(dados_orcamentos, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erro inesperado ao processar dados dos orçamentos: {e}")

def salvar_vendas_pausadas(vendas: List[Venda]):
    _garantir_diretorio_dados()
    try:
        dados_vendas = [venda.to_dict() for venda in vendas]
        with open(VENDAS_PAUSADAS_FILE, 'w', encoding='utf-8') as f:
            json.dump(dados_vendas, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erro inesperado ao processar dados das vendas pausadas: {e}")

def carregar_pessoas() -> Tuple[List[Cliente], List[Funcionario]]:
    _garantir_diretorio_dados()
    
    clientes_carregados = []
    funcionarios_carregados = []

    try:
        if os.path.exists(CLIENTES_FILE):
            with open(CLIENTES_FILE, 'r', encoding='utf-8') as f:
                dados_clientes = json.load(f)
                
                max_id_cliente = 0
                for dados in dados_clientes:
                    cliente = Cliente.from_dict(dados)
                    clientes_carregados.append(cliente)
                    
                    if cliente.id_cliente > max_id_cliente:
                        max_id_cliente = cliente.id_cliente

                Cliente.set_contador_id(max_id_cliente)
                
    except (IOError, json.JSONDecodeError) as e:
        print(f"Erro ao carregar clientes (ou arquivo vazio): {e}")

    try:
        if os.path.exists(FUNCIONARIOS_FILE):
            with open(FUNCIONARIOS_FILE, 'r', encoding='utf-8') as f:
                dados_funcionarios = json.load(f)
                
                max_mat_num = 0
                for dados in dados_funcionarios:
                    funcionario = Funcionario.from_dict(dados)
                    funcionarios_carregados.append(funcionario)
                    
                    try:
                        num_mat = int(funcionario.matricula[1:]) 
                        if num_mat > max_mat_num:
                            max_mat_num = num_mat
                    except ValueError:
                        continue
                
                Funcionario.set_contador_matricula(max_mat_num)
    except (IOError, json.JSONDecodeError) as e:
        print(f"Erro ao carregar funcionários (ou arquivo vazio): {e}")

    return clientes_carregados, funcionarios_carregados

def carregar_estoque() -> Estoque:
    _garantir_diretorio_dados()
    estoque = Estoque()
    try:
        if os.path.exists(ESTOQUE_FILE):
            with open(ESTOQUE_FILE, 'r', encoding='utf-8') as f:
                dados_estoque = json.load(f)
                if dados_estoque:
                    estoque.load_from_data(dados_estoque)
    except (IOError, json.JSONDecodeError) as e:
        print(f"Erro ao carregar estoque (ou arquivo vazio): {e}")
    return estoque

def carregar_historico(todos_clientes: List[Cliente], 
                       todos_funcionarios: List[Funcionario], 
                       todos_os_produtos: List[Produto]) -> HistoricoVendas:
    
    _garantir_diretorio_dados()
    historico = HistoricoVendas()

    try:
        if os.path.exists(HISTORICO_FILE):
            with open(HISTORICO_FILE, 'r', encoding='utf-8') as f:
                dados_historico = json.load(f)
                if dados_historico:
                    historico.load_from_data(
                        dados_historico, 
                        todos_clientes, 
                        todos_funcionarios, 
                        todos_os_produtos
                    )
    except (IOError, json.JSONDecodeError) as e:
        print(f"Erro ao carregar histórico (ou arquivo vazio): {e}")
    
    return historico

def carregar_orcamentos(todos_clientes: List[Cliente],
                        todos_funcionarios: List[Funcionario],
                        todos_os_produtos: List[Produto]) -> List[Orcamento]:
    _garantir_diretorio_dados()
    orcamentos_carregados = []
    max_id_orcamento = 0
    try:
        if os.path.exists(ORCAMENTOS_FILE):
            with open(ORCAMENTOS_FILE, 'r', encoding='utf-8') as f:
                dados_orcamentos = json.load(f)
                for dados in dados_orcamentos:
                    try:
                        orc = Orcamento.from_dict(
                            dados, todos_clientes, todos_funcionarios, todos_os_produtos
                        )
                        orcamentos_carregados.append(orc)
                        if orc.id_orcamento > max_id_orcamento:
                            max_id_orcamento = orc.id_orcamento
                    except ValueError as e:
                        print(f"[ERRO] Falha ao carregar Orçamento: {e}")

        Orcamento.set_contador_id(max_id_orcamento)
        print(f"Carregados {len(orcamentos_carregados)} orçamentos.")

    except Exception as e:
        print(f"Erro ao carregar orçamentos: {e}")

    return orcamentos_carregados

def carregar_vendas_pausadas(todos_clientes: List[Cliente],
                           todos_funcionarios: List[Funcionario],
                           todos_os_produtos: List[Produto]) -> List[Venda]:
    _garantir_diretorio_dados()
    vendas_carregadas = []
    try:
        if os.path.exists(VENDAS_PAUSADAS_FILE):
            with open(VENDAS_PAUSADAS_FILE, 'r', encoding='utf-8') as f:
                dados_vendas = json.load(f)
                for dados in dados_vendas:
                    try:
                        venda = Venda.from_dict(
                            dados, todos_clientes, todos_funcionarios, todos_os_produtos
                        )
                        if venda.status == "PAUSADA":
                            vendas_carregadas.append(venda)
                        else:
                            print(f"[AVISO] Venda {venda.id_venda} encontrada em 'vendas_pausadas.json' mas com status '{venda.status}'. Ignorando.")
                    except ValueError as e:
                        print(f"[ERRO] Falha ao carregar Venda pausada: {e}")
        
        print(f"Carregadas {len(vendas_carregadas)} vendas pausadas.")

    except Exception as e:
        print(f"Erro ao carregar vendas pausadas: {e}")

    return vendas_carregadas