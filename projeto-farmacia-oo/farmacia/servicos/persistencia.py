import json
import os
from farmacia.entidades.pessoa import Cliente, Funcionario
from typing import List, Dict, Tuple

CAMINHO_DADOS = "dados"
CLIENTES_FILE = os.path.join(CAMINHO_DADOS, "clientes.json")
FUNCIONARIOS_FILE = os.path.join(CAMINHO_DADOS, "funcionarios.json")
# (No futuro, adicionaremos aqui 'estoque.json', 'vendas.json', etc.)


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