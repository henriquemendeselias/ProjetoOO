from farmacia.entidades.produto import Produto
from farmacia.entidades.pessoa import Funcionario, Cliente
from datetime import datetime
from typing import List, Dict

class ItemVenda:
    def __init__(self, produto: Produto, quantidade: int):
        if quantidade <= 0:
            raise ValueError("a quantidade de um item deve ser positiva")
        
        self.__produto = produto
        self.__quantidade = quantidade
        self.__preco_momento = produto.preco

    @property
    def produto(self) -> Produto:
        return self.__produto
        
    @property
    def quantidade(self) -> int:
        return self.__quantidade

    @property
    def preco_momento(self) -> float:
        return self.__preco_momento
        
    def calcular_subtotal(self) -> float:
        return self.__quantidade * self.__preco_momento
        
    def __str__(self) -> str:
        subtotal = self.calcular_subtotal()
        return f"{self.__produto.nome} com {self.__quantidade} unidades, Preço Un.: R${self.__preco_momento:.2f} | Subtotal: R${subtotal:.2f}"
    
    def to_dict(self) -> Dict:
        return {
            "codigo_produto_ref": self.__produto.codigo,
            "quantidade": self.__quantidade,
            "preco_momento": self.__preco_momento
        }
    
    @classmethod
    def from_dict(cls, dados: Dict, todos_os_produtos: List[Produto]) -> "ItemVenda":
        codigo_busca = dados['codigo_produto_ref']

        produto_encontrado = next((p for p in todos_os_produtos if p.codigo == codigo_busca), None)
        
        if not produto_encontrado:
            raise ValueError(f"Produto com código {codigo_busca} não encontrado ao carregar histórico.")

        novo_item = cls(produto_encontrado, dados['quantidade'])
        
        novo_item.__preco_momento = dados['preco_momento']
        
        return novo_item
    
class Venda:
    _contador_id = 0
    def __init__(self,  funcionario: Funcionario, cliente: Cliente):
        Venda._contador_id += 1
        self.__id_venda = Venda._contador_id
        self.__funcionario = funcionario
        self.__cliente = cliente
        self.__data_hora = datetime.now()
        self.__itens = []
        self.__valor_total = 0.0
        self.__status = "ATIVA"

    @property
    def id_venda(self) -> int:
        return self.__id_venda

    @property
    def cliente(self) -> Cliente:
        return self.__cliente

    @property
    def funcionario(self) -> Funcionario:
        return self.__funcionario
    
    @property
    def data_hora(self) -> datetime:
        return self.__data_hora

    @property
    def itens(self) -> list:
        return self.__itens

    @property
    def valor_total(self) -> float:
        return self.__valor_total
        
    @property
    def status(self) -> str:
        return self.__status
    
    def adicionar_item(self, produto: Produto, quantidade: int) -> None:
        novo_item = ItemVenda(produto, quantidade)
        self.__itens.append(novo_item)
        self._recalcular_total()

    def remover_item(self, item: ItemVenda) -> None:
        if item in self.__itens:
            self.__itens.remove(item)
            self._recalcular_total()
            print(f"Produto {item.produto.nome} removido com sucesso")
        else:
            print(f"Produto {item.produto.nome} não encontrado na venda.")

    def _recalcular_total(self) -> None:
        total_atualizado = 0.0
        for item in self.__itens:
            s = item.calcular_subtotal()
            total_atualizado += s

        self.__valor_total = total_atualizado
    
    def finalizar_venda(self, estoque, historico: "HistoricoVendas") -> None:
        if not self.__itens:
            print("impossível finalizar venda sem itens")
            return
        
        if self.__status != "ATIVA":
            print("impossível finalizar venda não ativa")
            return
        
        for item in self.__itens:
            estoque.dar_baixa_por_venda(item.produto, item.quantidade)

        self.__status = "FINALIZADA"
        print(f"status da venda {self.id_venda} atualizada para 'FINALIZADA'.")

        historico.registrar_venda(self)

    def cancelar_venda(self, estoque) -> None:
        if self.__status == "ATIVA" or self.__status == "PAUSADA":
            self.__status = "CANCELADA"
            print(f"venda {self.id_venda} (em andamento) cancelada")
        elif self.__status == "FINALIZADA":
            for item in self.__itens:
                estoque.estornar_item(item.produto, item.quantidade)
            self.__status = "CANCELADA"
            print(f"venda{self.id_venda} estornada com sucesso")
        else:
            print(f"venda {self.id_venda} já cancelada")
    
    def pausar_venda(self) -> None:
        if self.__status == "ATIVA":
            self.__status = "PAUSADA"
            print(f"venda {self.id_venda} pausada")
        else:
            print("impossível pausar esta venda")

    def retomar_venda(self) -> None:
        if self.__status == "PAUSADA":
            self.__status = "ATIVA"
            print("venda retomada")
        else:
            print("impossível retomar esta venda")

    def aplicar_desconto(self, percentual: float):
        if not 0 <= percentual <= 100:
            print("percentual inválido")
            return
        
        desconto_decimal = percentual / 100.0
        fator_multiplicador = 1 - desconto_decimal
        novo_valor = self.__valor_total * fator_multiplicador
        self.__valor_total = novo_valor
        print(f"desconto de {percentual}% aplicado. novo total: R$ {self.__valor_total:.2f}")
    
    def processar_pagamento(self, forma: str, valor: float) -> bool:
        if self.__valor_total == 0:
            print("Venda sem itens ou com valor zerado, pagamento não aplicável")
            return False
        
        if self.__status != "ATIVA":
            print("pagamento não pode ser processado para uma venda que não está ativa.")
            return False

        if round(valor, 2) >= round(self.__valor_total, 2):
            print(f"Total da Venda: R$ {self.__valor_total:.2f}")
            print(f"Valor Pago: R${valor:.2f}")
            print(f"Forma: {forma}")
            if forma.lower() == 'dinheiro':
                troco = round(valor, 2) - round(self.__valor_total, 2)
                print(f"Troco: R${troco:.2f}")
            print("Pagamento APROVADO.")
            return True
        else:
            print(f"Total da Venda: R$ {self.__valor_total:.2f}")
            print(f"Valor Pago: R${valor:.2f}")
            print("Valor pago é insuficiente.")
            print("Pagamento RECUSADO.")
            return False


    def __str__(self) -> str:
        cabecalho = (
            f"--- Venda ID: {self.id_venda} | Status: {self.status} ---\n"
            f"Data: {self.data_hora.strftime('%d/%m/%Y %H:%M:%S')}\n"
            f"Cliente: {self.cliente.nome}\n"
            f"Funcionário: {self.funcionario.nome}\n"
            f"{'-'*40}\n"
        )

        itens_str = ""
        if not self.itens:
            itens_str = "Nenhum item na venda.\n"
        else:
            for item in self.itens:
                itens_str += f"- {item}\n"
        
        rodape = (
            f"{'-'*40}\n"
            f"Valor Total: R$ {self.valor_total:.2f}\n"
            f"{'='*40}"
        )

        return cabecalho + itens_str + rodape
    
    def to_dict(self) -> Dict:
        return {
            "id_venda": self.__id_venda,
            "id_cliente_ref": self.__cliente.id_cliente,
            "matricula_func_ref": self.__funcionario.matricula,
            "data_hora": self.__data_hora.isoformat(),
            "status": self.__status,
            "valor_total": self.__valor_total,
            "itens": [item.to_dict() for item in self.__itens]
        }

    @classmethod
    def from_dict(cls, dados: Dict, 
                  todos_clientes: List[Cliente], 
                  todos_funcionarios: List[Funcionario], 
                  todos_os_produtos: List[Produto]) -> "Venda":
        
        id_cli = dados['id_cliente_ref']
        cliente_encontrado = next((c for c in todos_clientes if c.id_cliente == id_cli), None)

        mat_func = dados['matricula_func_ref']
        func_encontrado = next((f for f in todos_funcionarios if f.matricula == mat_func), None)

        if not cliente_encontrado or not func_encontrado:
            raise ValueError(f"Cliente (ID {id_cli}) ou Funcionário (Mat {mat_func}) não encontrado ao carregar Venda {dados['id_venda']}.")

        nova_venda = cls(func_encontrado, cliente_encontrado)

        nova_venda.__id_venda = dados['id_venda']
        nova_venda.__data_hora = datetime.fromisoformat(dados['data_hora'])
        nova_venda.__status = dados['status']
        nova_venda.__valor_total = dados['valor_total']
        
        nova_venda.__itens = [
            ItemVenda.from_dict(item_dados, todos_os_produtos) 
            for item_dados in dados['itens']
        ]
        
        return nova_venda
    
    @classmethod
    def set_contador_id(cls, valor_max: int):
        cls._contador_id = valor_max
    

class Orcamento:
    _contador_id = 0
    def __init__(self, funcionario: Funcionario, cliente: Cliente):
        Orcamento._contador_id += 1
        self.__id_orcamento = Orcamento._contador_id
        self.__cliente = cliente
        self.__funcionario = funcionario
        self.__data_hora = datetime.now()
        self.__itens = []
        self.__valor_total = 0.0
    
    
    @property
    def id_orcamento(self) -> int:
        return self.__id_orcamento
    
    @property
    def valor_total(self) -> float:
        return self.__valor_total

    @property
    def cliente(self) -> Cliente:
        return self.__cliente
    
    @property
    def funcionario(self) -> Funcionario:
        return self.__funcionario

    @property
    def data_hora(self) -> datetime:
        return self.__data_hora

    @property
    def itens(self) -> list:
        return self.__itens

    def _recalcular_total(self) -> None:
        total_atualizado = 0.0
        for item in self.__itens:
            total_atualizado += item.calcular_subtotal()
            
        self.__valor_total = total_atualizado

    def adicionar_item(self, produto: Produto, quantidade: int) -> None:
        novo_item = ItemVenda(produto, quantidade)
        self.__itens.append(novo_item)
        self._recalcular_total()
        
    def remover_item(self, item: ItemVenda) -> None:
        if item in self.__itens:
            self.__itens.remove(item)
            self._recalcular_total()
        else:
            print("produto não encontrado no orçamento")

    def converter_em_venda(self) -> "Venda":
        orcamento_convertido = Venda(self.funcionario, self.cliente)

        if self.itens:
            orcamento_convertido.itens.extend(self.itens)

        orcamento_convertido._recalcular_total()

        print(f"orcamento {self.id_orcamento} convertido na venda {orcamento_convertido.id_venda}")

        return orcamento_convertido

    def __str__(self) -> str:
        cabecalho = (
            f"--- Orçamento ID: {self.id_orcamento} ---\n"
            f"Data: {self.data_hora.strftime('%d/%m/%Y %H:%M:%S')}\n"
            f"Cliente: {self.cliente.nome}\n"
            f"Funcionário: {self.funcionario.nome}\n"
            f"{'-'*40}\n"
        )
        itens_str = "Itens:\n"
        if not self.itens:
            itens_str = "Nenhum item no orçamento.\n"
        else:
            for item in self.itens:
                itens_str += f"  - {item}\n"
    
        rodape = (
            f"{'-'*40}\n"
            f"Valor Total: R$ {self.valor_total:.2f}\n"
            f"{'='*40}"
        )
        return cabecalho + itens_str + rodape  
    
    def to_dict(self) -> Dict:
        return {
            "id_orcamento": self.__id_orcamento,
            "id_cliente_ref": self.__cliente.id_cliente,
            "matricula_func_ref": self.__funcionario.matricula,
            "data_hora": self.__data_hora.isoformat(),
            "valor_total": self.__valor_total,
            "itens": [item.to_dict() for item in self.__itens]
        }

    @classmethod
    def from_dict(cls, dados: Dict, 
                  todos_clientes: List[Cliente], 
                  todos_funcionarios: List[Funcionario], 
                  todos_os_produtos: List[Produto]) -> "Orcamento":

        id_cli = dados['id_cliente_ref']
        cliente_encontrado = next((c for c in todos_clientes if c.id_cliente == id_cli), None)

        mat_func = dados['matricula_func_ref']
        func_encontrado = next((f for f in todos_funcionarios if f.matricula == mat_func), None)

        if not cliente_encontrado or not func_encontrado:
            raise ValueError(f"Cliente (ID {id_cli}) ou Funcionário (Mat {mat_func}) não encontrado ao carregar Orçamento {dados['id_orcamento']}.")

        novo_orcamento = cls(func_encontrado, cliente_encontrado)

        novo_orcamento.__id_orcamento = dados['id_orcamento']
        novo_orcamento.__data_hora = datetime.fromisoformat(dados['data_hora']) 
        novo_orcamento.__valor_total = dados['valor_total']
        
        
        novo_orcamento.__itens = [
            ItemVenda.from_dict(item_dados, todos_os_produtos) 
            for item_dados in dados['itens']
        ]
        
        return novo_orcamento
    
    @classmethod
    def set_contador_id(cls, valor_max: int):
        cls._contador_id = valor_max

class HistoricoVendas:
    def __init__(self):
        self.__vendas_finalizadas = []

    @property 
    def vendas(self) -> list:
        return self.__vendas_finalizadas
        
    def registrar_venda(self, venda: Venda) -> None:
        if venda.status != "FINALIZADA":
            print("Impoossível registrar venda não finalizada")
            return
        else:
            self.__vendas_finalizadas.append(venda)
            print("Venda registrada")

    def buscar_venda_por_id(self, id_venda_para_busca: int) -> Venda | None:
        for venda in self.__vendas_finalizadas:
            if venda.id_venda == id_venda_para_busca:
                return venda
        return None
    

    def consultar_historico_cliente(self, cliente: Cliente) -> list:
        compras_do_cliente = []
        for venda in self.__vendas_finalizadas:
            if venda.cliente == cliente:
                compras_do_cliente.append(venda)
            
        return compras_do_cliente
        
    def consultar_historico_funcionario(self, funcionario: Funcionario) -> list:
        vendas_do_funcionario = []
        for venda in self.__vendas_finalizadas:
            if venda.funcionario == funcionario:
                vendas_do_funcionario.append(venda)
            
        return vendas_do_funcionario

    def __str__(self):
        return f"histórico contendo {len(self.__vendas_finalizadas)} vendas registradas."
    
    def to_dict(self) -> List[Dict]:
        return [venda.to_dict() for venda in self.__vendas_finalizadas]
    
    def load_from_data(self, 
                       dados_historico: List[Dict], 
                       todos_clientes: List[Cliente], 
                       todos_funcionarios: List[Funcionario], 
                       todos_os_produtos: List[Produto]):
        
        vendas_carregadas = []
        max_id_venda = 0
        
        for dados_venda in dados_historico:
            try:
                venda = Venda.from_dict(
                    dados_venda, 
                    todos_clientes, 
                    todos_funcionarios, 
                    todos_os_produtos
                )
                vendas_carregadas.append(venda)
            
                if venda.id_venda > max_id_venda:
                    max_id_venda = venda.id_venda
                    
            except ValueError as e:
                print(f"[ERRO] Falha ao carregar Venda: {e}")
        self.__vendas_finalizadas = vendas_carregadas
    
        Venda.set_contador_id(max_id_venda)
        print(f"Histórico carregado com {len(self.__vendas_finalizadas)} vendas.")