from farmacia.entidades.produto import Produto, Lote, Medicamento, Perfumaria
from datetime import date, timedelta
from typing import List, Dict, Type

class Estoque:
    def __init__(self):
        self.__inventario: Dict[str, Dict] = {}

    @property
    def produtos(self) -> List[Produto]:
        return [dados["produto"] for dados in self.__inventario.values()]

    def to_dict(self) -> Dict[str, Dict]:
        inventario_serializado = {}
        for chave_produto, dados in self.__inventario.items():
            produto_dict = dados["produto"].to_dict()
            lotes_list_dict = [lote.to_dict() for lote in dados["lotes"]]
            inventario_serializado[chave_produto] = {
                "produto": produto_dict,
                "lotes": lotes_list_dict
            }
        return inventario_serializado
    
    def load_from_data(self, dados_inventario: Dict[str, Dict]):
        CLASSES_PRODUTO: Dict[str, Type[Produto]] = {
            "Medicamento": Medicamento,
            "Perfumaria": Perfumaria
        }

        novo_inventario_carregado = {}
        
        for chave_produto, dados in dados_inventario.items():
            
            dados_produto = dados["produto"]
            tipo_produto_str = dados_produto.get("@type")
            
            classe_do_produto = CLASSES_PRODUTO.get(tipo_produto_str)
            
            if not classe_do_produto:
                print(f"[ERRO] Tipo de produto desconhecido '{tipo_produto_str}' ao carregar. Pulando item.")
                continue

            produto_obj = classe_do_produto.from_dict(dados_produto)
            
            lotes_obj_list = []
            for dados_lote in dados["lotes"]:
                lote_obj = Lote.from_dict(dados_lote)
                lotes_obj_list.append(lote_obj)
                
            novo_inventario_carregado[chave_produto] = {
                "produto": produto_obj,
                "lotes": lotes_obj_list
            }

        self.__inventario = novo_inventario_carregado
        print(f"Estoque carregado com {len(self.__inventario)} tipos de produtos.")

    def adicionar_lote(self, produto: Produto, codigo_lote: str, quantidade: int, data_validade: date) -> None:
        novo_lote = Lote(codigo_lote, quantidade, data_validade)
        chave_produto = produto.codigo

        if chave_produto in self.__inventario:
            self.__inventario[chave_produto]["lotes"].append(novo_lote)
            print(f"Novo lote {codigo_lote} adicionado ao produto existente '{produto.nome}'.")
        else:
            self.__inventario[chave_produto] = {"produto": produto, "lotes": [novo_lote]}

            print(f"Produto novo '{produto.nome}'adicionado ao inventário com o lote {codigo_lote}.")


    def dar_baixa_por_venda(self, produto: Produto, quantidade: int) -> bool:
        chave_produto = produto.codigo

        if chave_produto not in self.__inventario:
            print(f"Produto '{produto.nome}' não encontrado.")
            return False
        else:
            lista_de_lotes = self.__inventario[chave_produto]["lotes"]

        estoque_total_produto = 0
        for lote in lista_de_lotes:
            estoque_total_produto += lote.quantidade

        if estoque_total_produto < quantidade:
            print(f"Estoque insuficiente para '{produto.nome}'.")
            return False
        
        lista_de_lotes.sort(key=lambda lote: lote.data_validade)

        for lote in lista_de_lotes:
            if quantidade == 0:
                break

            elif lote.quantidade >= quantidade:
                lote.quantidade -= quantidade
                quantidade = 0 
            
            else: 
                quantidade -= lote.quantidade
                lote.quantidade = 0
            
        self.__inventario[chave_produto]["lotes"] = [
        lote for lote in lista_de_lotes if lote.quantidade > 0 ]
            
        return True

    def estornar_item(self, produto: Produto, quantidade: int) -> None:
        chave_produto = produto.codigo

        if chave_produto not in self.__inventario:
            print(f"Tentativa de estornar produto não existente no inventário: {produto.nome}") 
            return
        
        lista_de_lotes = self.__inventario[chave_produto]["lotes"]

        if not lista_de_lotes:
            print(f"Não há lotes para estornar o produto {produto.nome}. O estorno falhou.")
            return

        lista_de_lotes.sort(key=lambda lote: lote.data_validade, reverse=True)

        lote_alvo = lista_de_lotes[0]
        lote_alvo.quantidade += quantidade
        print(f"Estornado {quantidade} un. para o lote {lote_alvo.codigo_lote} do produto '{produto.nome}'.")

    def registrar_perda(self, lote_a_verificar: Lote, quantidade: int, motivo: str) -> None:
        chave_do_produto = None
        lista_de_lotes_do_produto = None
        for chave, dados in self.__inventario.items():
            if lote_a_verificar in dados["lotes"]:
                chave_do_produto = chave
                lista_de_lotes_do_produto = dados["lotes"]
                break

        if not chave_do_produto:
            print(f"[ERRO] O lote {lote_a_verificar.codigo_lote} não foi encontrado no inventário.")
            return

        if quantidade <= 0 or quantidade > lote_a_verificar.quantidade:
            print(f"[ERRO] Quantidade de perda inválida ({quantidade}). Estoque do lote: {lote_a_verificar.quantidade}.")
            return

        print(f"[LOG ESTOQUE] Registrada perda de {quantidade} un. do lote {lote_a_verificar.codigo_lote}. Motivo: {motivo}")
        lote_a_verificar.quantidade -= quantidade

        self.__inventario[chave_do_produto]["lotes"] = [
            lote for lote in lista_de_lotes_do_produto if lote.quantidade > 0
        ]
        
    def remover_produto(self, codigo_produto: str) -> bool:
        if codigo_produto in self.__inventario:
            del self.__inventario[codigo_produto]
            print(f"Produto com código '{codigo_produto}' foi removido.")
            return True
        else:
            print(f"Produto com código '{codigo_produto}' não encontrado para remoção.")
            return False    

    def consultar_lotes_produto(self, produto: Produto) -> List[Lote]:
        chave_produto = produto.codigo
        dados_produto = self.__inventario.get(chave_produto)
        
        if dados_produto:
            return dados_produto["lotes"]
        
        return []

    def listar_produtos_baixo_estoque(self, limite_minimo: int) -> list:
        produtos_em_falta = []
        for dados_produto in self.__inventario.values():
            produto_atual = dados_produto["produto"]
            lista_de_lotes = dados_produto["lotes"]
            
            estoque_total = sum(lote.quantidade for lote in lista_de_lotes)

            if estoque_total <= limite_minimo:
                produtos_em_falta.append((produto_atual, estoque_total))
        
        produtos_em_falta.sort(key=lambda item: item[1])
        return produtos_em_falta


    def listar_produtos_proximo_vencimento(self, dias_limite: int) -> List[Lote]:

        lotes_a_vencer = []
        data_limite = date.today() + timedelta(days=dias_limite)
        
        for dados_produto in self.__inventario.values():
            produto = dados_produto["produto"]
            for lote in dados_produto["lotes"]:
                if lote.data_validade <= data_limite:
                    lotes_a_vencer.append((produto, lote))
        
        lotes_a_vencer.sort(key=lambda item: item[1].data_validade)
        return lotes_a_vencer
    
    def consultar_quantidade_total(self, produto: Produto) -> int:
        chave_produto = produto.codigo
        dados_produto = self.__inventario.get(chave_produto)
        
        if dados_produto:
            lista_de_lotes = dados_produto["lotes"]
            return sum(lote.quantidade for lote in lista_de_lotes)
        
        return 0


    def __str__(self) -> str:
        if not self.__inventario:
            return "Estoque vazio"
        
        resumo = "Resumo do estoque\n"
        for dados_produto in self.__inventario.values():
            produto = dados_produto["produto"]
            estoque_total = sum(lote.quantidade for lote in dados_produto["lotes"])
            resumo += f"produto: {produto.nome} | estoque total: {estoque_total} unidades\n"
        
        return resumo    