from abc import ABC, abstractmethod

class Pessoa(ABC):
    def __init__(self, nome: str, cpf: str):
        self._nome = nome
        self._cpf = cpf

    def __str__(self) -> str:
        return f"Nome: {self._nome}, CPF: {self._cpf}"
    
    @property
    def nome(self) -> str:
        return self._nome
    
    @property
    def cpf(self) -> str:
        return self._cpf
    
    @nome.setter
    def nome(self, novo_nome: str):
        if novo_nome and novo_nome.strip():
            self._nome = novo_nome
        else:
            print("O nome não pode ser vazio.")

    @cpf.setter
    def cpf(self, novo_cpf: str):
        if novo_cpf and novo_cpf.strip():
            self._cpf = novo_cpf
        else:
            print("[ERRO] O CPF não pode ser vazio.")
    
    def to_dict(self) -> dict:
        return {
            "@type": self.__class__.__name__,
            "nome": self._nome,
            "cpf": self._cpf
        }
    
class Funcionario(Pessoa):
    _contador_matricula = 0
    def __init__(self, nome: str, cpf: str):
        super().__init__(nome, cpf)
        Funcionario._contador_matricula += 1
        self.__matricula = f"F{Funcionario._contador_matricula:03d}"
    
    def __str__(self) -> str: 
        info_base = super().__str__()
        return f"Funcionario | {info_base}, Matricula: {self.__matricula}"
    
    @property
    def matricula(self) -> str:
        return self.__matricula
    
    def to_dict(self) -> dict:
        dados_base = super().to_dict()
        dados_base.update({
            "matricula": self.__matricula
        })
        return dados_base

    @classmethod
    def from_dict(cls, dados: dict) -> "Funcionario":
        novo_func = cls(dados['nome'], dados['cpf'])
        novo_func.__matricula = dados['matricula']
        return novo_func

    @classmethod
    def set_contador_matricula(cls, valor_max: int):
        cls._contador_matricula = valor_max
    
class Cliente(Pessoa):
    _contador_id = 0
    def __init__(self, nome: str, cpf: str):
        super().__init__(nome, cpf)
        Cliente._contador_id += 1
        self.__id_cliente = Cliente._contador_id

    def __str__(self) -> str:
        info_base = super().__str__()
        return f"Cliente | {info_base}, ID: {self.__id_cliente}"
    
    @property
    def id_cliente(self) -> int:
        return self.__id_cliente
    
    def to_dict(self) -> dict:
        dados_base = super().to_dict()
        dados_base.update({
            "id_cliente": self.__id_cliente
        })
        return dados_base
    
    @classmethod
    def from_dict(cls, dados: dict) -> "Cliente":
        novo_cli = cls(dados['nome'], dados['cpf'])
        novo_cli.__id_cliente = dados['id_cliente']
        return novo_cli

    @classmethod
    def set_contador_id(cls, valor_max: int):
        cls._contador_id = valor_max