from farmacia.entidades.pessoa import Cliente, Funcionario
from farmacia.entidades.produto import Lote, Medicamento, Perfumaria
from farmacia.servicos.estoque import Estoque
from farmacia.servicos.venda import HistoricoVendas, ItemVenda, Orcamento, Venda
from typing import List
from datetime import date
import os
from farmacia.servicos.persistencia import (
    carregar_pessoas, salvar_pessoas,
    carregar_estoque, salvar_estoque,
    carregar_historico, salvar_historico,
    carregar_orcamentos, salvar_orcamentos,
    carregar_vendas_pausadas, salvar_vendas_pausadas
)

def exibir_menu(titulo: str, opcoes: list) -> None:
    largura = 50
    print("+" + "-" * (largura + 2) + "+")
    print(f"| {titulo.center(largura)} |")
    print("+" + "=" * (largura + 2) + "+")
    for i, opcao in enumerate(opcoes):
        texto_da_opcao = f"{i + 1}. {opcao}"
        print(f"| {texto_da_opcao.ljust(largura)} |")
    print("+" + "-" * (largura + 2) + "+")

def menu_caixa(estoque: Estoque, historico: HistoricoVendas, funcionario_logado: Funcionario, lista_de_clientes: list, vendas_pausadas):
    
    venda_ativa = None

    while True:
        if venda_ativa is None:
            titulo = "MÓDULO CAIXA (LIVRE)"
            opcoes = [
                "Iniciar Nova Venda", 
                "Retomar Venda Pausada",
                "Cancelar Venda Finalizada (Estorno)"
            ]

            exibir_menu(titulo, opcoes)
            largura_menu = 50
            print(f"| {'0. Voltar ao Menu Principal'.ljust(largura_menu)} |")
            print("+" + "-" * (largura_menu + 2) + "+")

            try:
                escolha = int(input("Escolha uma opção: "))
            except ValueError:
                print("ERRO..."); input("Pressione Enter..."); continue

            if escolha == 1:
                print("\n--- Iniciando Nova Venda ---")
                if not lista_de_clientes:
                    print("[ERRO] Nenhum cliente cadastrado. Cadastre um cliente no 'Módulo Balcão' primeiro.")
                    input("Pressione Enter...")
                    continue

                for cliente in lista_de_clientes:
                    print(f"ID: {cliente.id_cliente} | Nome: {cliente.nome}")

                try:
                    id_cliente = int(input("\nDigite o ID do cliente para a venda: "))
                    cliente_selecionado = None
                    for cliente in lista_de_clientes:
                        if cliente.id_cliente == id_cliente:
                            cliente_selecionado = cliente                    

                    if cliente_selecionado:
                        venda_ativa = Venda(funcionario_logado,cliente_selecionado)
                        
                        print(f"\n[SUCESSO] Venda #{venda_ativa.id_venda} iniciada para o cliente {cliente_selecionado.nome}.")
                        input("Pressione Enter para começar a adicionar os itens...")
                    else:
                        print("ERRO: Cliente não encontrado.")
                        input("Pressione Enter...")
                    
                except ValueError:
                    print("ERRO: ID inválido.")

            elif escolha == 2: 
                print("\n--- Retomar Venda Pausada ---")
                
                if not vendas_pausadas:
                    print("Nenhuma venda pausada no momento.")
                    input("Pressione Enter para continuar...")
                    continue 

                print("\nVendas pausadas disponíveis:")
                for i, venda in enumerate(vendas_pausadas):
                    print(f"  [{i + 1}] Venda #{venda.id_venda} | Cliente: {venda.cliente.nome} | Total: R${venda.valor_total:.2f}")

                try:
                    indice_escolhido = int(input("\nDigite o número da venda a retomar: "))
                    
                    if 1 <= indice_escolhido <= len(vendas_pausadas):
                        venda_retomada = vendas_pausadas.pop(indice_escolhido - 1)
                        venda_retomada.retomar_venda()
                        venda_ativa = venda_retomada
                        
                        print(f"\n[SUCESSO] Venda #{venda_ativa.id_venda} retomada.")
                        input("Pressione Enter para continuar a edição...")
                    else:
                        print("ERRO: Número de venda inválido.")
                        input("Pressione Enter para continuar...")

                except ValueError:
                    print("ERRO: Entrada inválida. Digite apenas um número.")
                    input("Pressione Enter para continuar...")
            
            elif escolha == 3: 
                print("\n--- Cancelar Venda Finalizada (Estorno) ---")
                
                if not historico.vendas:
                    print("Nenhuma venda no histórico para cancelar.")
                    input("Pressione Enter para continuar...")
                    continue

                try:
                    for venda in historico.vendas:
                        print(venda)
                    id_busca = int(input("\nDigite o ID da venda a ser cancelada: "))
                    
                    venda_encontrada = historico.buscar_venda_por_id(id_busca)

                    if venda_encontrada:
                        if venda_encontrada.status == "FINALIZADA":
                            print("\n--- Venda a ser Cancelada ---")
                            print(venda_encontrada)

                            confirmacao = input("Confirmar o cancelamento e estorno desta venda? (s/n): ").lower()
                            
                            if confirmacao == 's':
                                venda_encontrada.cancelar_venda(estoque)
                            else:
                                print("\nOperação de cancelamento abortada.")
                        else:
                            print(f"\n[ERRO] A venda #{id_busca} não pode ser cancelada (Status atual: {venda_encontrada.status}).")
                    else:
                        print(f"\n[ERRO] Nenhuma venda encontrada com o ID #{id_busca}.")

                except ValueError:
                    print("ERRO: ID inválido. Digite apenas um número.")
                
                input("Pressione Enter para continuar...")

            elif escolha == 0:
                break

        else:
            resultado_submenu = submenu_venda_ativa(venda_ativa, estoque, historico)

            if resultado_submenu is None:
                venda_ativa = None
            elif resultado_submenu.status == "PAUSADA":
                vendas_pausadas.append(resultado_submenu)
                venda_ativa = None
            else:
                venda_ativa = resultado_submenu

def menu_balcao(lista_de_orcamentos: list, lista_de_clientes: list, lista_de_funcionarios: list, estoque: Estoque, historico: HistoricoVendas, funcionario: Funcionario, vendas_pausadas: list):
    while True:
        titulo_menu = "MÓDULO DO BALCÃO"
        opcoes_menu = [
            "Gerenciar Clientes",
            "Gerenciar Funcionarios",
            "Gerenciar Produtos",
            "Gerenciar Orçamentos", 
            "Gerenciar Estoque",
            "Consultar Histórico de Vendas"
            ]
        exibir_menu(titulo_menu, opcoes_menu)
        largura_menu = 50
        print(f"| {'0. Voltar ao Menu Principal'.ljust(largura_menu)} |")
        print("+" + "-" * (largura_menu + 2) + "+")

        try:
            escolha = int(input("Digite sua opção: "))
        except ValueError:
            print("ERRO: Por favor, digite um número.")
            input("Pressione Enter para seguir...")
            continue

        if escolha == 1:
            submenu_clientes(lista_de_clientes, historico)
            salvar_pessoas(lista_de_clientes, lista_de_funcionarios)
        elif escolha == 2:
            submenu_funcionarios(lista_de_funcionarios, historico)
            salvar_pessoas(lista_de_clientes, lista_de_funcionarios)
        elif escolha == 3:
            submenu_produtos(estoque)
            salvar_estoque(estoque)
        elif escolha == 4:
            submenu_orcamentos(lista_de_orcamentos, lista_de_clientes, estoque, funcionario, vendas_pausadas, historico)
        elif escolha == 5: 
            submenu_estoque(estoque)
            salvar_estoque(estoque)
        elif escolha == 6:
            submenu_historicos(historico, lista_de_clientes, lista_de_funcionarios)
        elif escolha == 0:
            print("Voltando ao Menu Principal...")
            break
        else:
            print("ERRO: Opção não existe.")

def submenu_clientes(lista_de_clientes: list, historico: HistoricoVendas):
    while True:
        titulo = "GERENCIAR CLIENTES"
        opcoes = [
            "Cadastrar Novo Cliente",
            "Listar Todos os Clientes",
            "Atualizar Cliente",
            "Deletar Cliente" 
        ]
        exibir_menu(titulo, opcoes)
        largura_menu = 50
        print(f"| {'0. Voltar'.ljust(largura_menu)} |")
        print("+" + "-" * (largura_menu + 2) + "+")
        
        try:
            escolha = int(input("Escolha uma opção: "))
        except ValueError:
            print("ERRO: Opção inválida.")
            input("Pressione Enter para continuar...")
            continue

        if escolha == 1:
            print("\n--- Cadastro de Novo Cliente ---")
            nome = input("Digite o nome do cliente: ")
            cpf = input("Digite o CPF do cliente: ")
            novo_cliente = Cliente(nome, cpf)
            lista_de_clientes.append(novo_cliente)

            print(f"\n Cliente '{novo_cliente.nome}' cadastrado com o ID: {novo_cliente.id_cliente}")
            input("Pressione Enter para continuar...")

        elif escolha == 2:
            print("\n--- Lista de Clientes Cadastrados ---")
            if not lista_de_clientes:
                print("Nenhum cliente cadastrado.")
            else:
                for cliente in lista_de_clientes:
                    print(cliente)
            input("\nPressione Enter para continuar...")

        elif escolha == 3:
            print("\n--- Atualizar Cliente ---")
            if not lista_de_clientes:
                print("Nenhum cliente cadastrado para atualizar.")
                input("\nPressione Enter para continuar...")
                continue

            for cliente in lista_de_clientes:
                print(f"ID: {cliente.id_cliente} | Nome: {cliente.nome}")
            
            try:
                id_busca = int(input("\nDigite o ID do cliente para atualizá-lo: "))
                cliente_encontrado = None
                for cliente in lista_de_clientes:
                    if cliente.id_cliente == id_busca:
                        cliente_encontrado = cliente
                        break

                if cliente_encontrado:
                    print("(Deixe em branco e pressione Enter para não alterar)")
                    
                    novo_nome = input("Digite o novo nome: ")
                    if novo_nome:
                        cliente_encontrado.nome = novo_nome 

                    novo_cpf = input(f"Digite o novo CPF: ")
                    if novo_cpf:
                        cliente_encontrado.cpf = novo_cpf 
                    
                    print(f"\n[SUCESSO] Dados do cliente atualizados!")
                    print(f"Novos dados: {cliente_encontrado}")
                else:
                    print("ERRO: Nenhum cliente encontrado com o ID informado.")

            except ValueError:
                print("ERRO: ID inválido. Digite apenas números.")
            input("Pressione Enter para continuar...")

        elif escolha == 4:
            print("\n--- Deletar Cliente ---")
            if not lista_de_clientes:
                print("Nenhum cliente cadastrado para remover.")
                input("\nPressione Enter para continuar...")
                continue

            for cliente in lista_de_clientes:
                print(f"ID: {cliente.id_cliente} | Nome: {cliente.nome}")
            
            try:
                id_busca = int(input("\nDigite o ID do cliente para removê-lo: "))

                cliente_encontrado = None
                for cliente in lista_de_clientes:
                    if cliente.id_cliente == id_busca:
                        cliente_encontrado = cliente
                        break

                if cliente_encontrado:
                    lista_de_clientes.remove(cliente_encontrado)
                    print(f"{cliente_encontrado.nome}, removido com sucesso")
                else:
                    print("ERRO: Nenhum cliente encontrado com o ID informado.")

            except ValueError:
                print("ERRO: ID inválido. Digite apenas números.")

            input("Pressione Enter para continuar...")    


        elif escolha == 0:
            break
        else:
            print("Opção em construção ou inválida.")
            input("Pressione Enter para continuar...")

def submenu_funcionarios(lista_de_funcionarios: list, historico: HistoricoVendas):
    while True:
        titulo = "GERENCIAR FUNCIONÁRIOS"
        opcoes = [
            "Cadastrar Novo Funcionário",
            "Listar Todos os Funcionários",
            "Atualizar Funcionário",
            "Deletar Funcionário" 
        ]
        exibir_menu(titulo, opcoes)
        largura_menu = 50
        print(f"| {'0. Voltar'.ljust(largura_menu)} |")
        print("+" + "-" * (largura_menu + 2) + "+")
        
        try:
            escolha = int(input("Escolha uma opção: "))
        except ValueError:
            print("ERRO: Opção inválida.")
            input("Pressione Enter para continuar...")
            continue

        if escolha == 1:
            print("\n--- Cadastro de Novo Funcionário ---")
            nome = input("Digite o nome do funcionário: ")
            cpf = input("Digite o CPF do funcionário: ")
            novo_funcionário = Funcionario(nome, cpf)
            lista_de_funcionarios.append(novo_funcionário)

            print(f"\n Funcionário '{novo_funcionário.nome}' cadastrado com a matrícula: {novo_funcionário.matricula}")
            input("Pressione Enter para continuar...")

        elif escolha == 2:
            print("\n--- Lista de Funcionários Cadastrados ---")
            if not lista_de_funcionarios:
                print("Nenhum funcionário cadastrado.")
            else:
                for funcionario in lista_de_funcionarios:
                    print(funcionario)
            input("\n Pressione Enter para continuar...")

        elif escolha == 3:
            print("\n--- Atualizar Funcionário ---")
            if not lista_de_funcionarios:
                print("Nenhum funcionário cadastrado para atualizar.")
                input("\n Pressione Enter para continuar...")
                continue

            for funcionario in lista_de_funcionarios:
                print(f"Matrícula: {funcionario.matricula} | Nome: {funcionario.nome}")
            
            try:
                matricula_busca = str(input("\nDigite a matrícula do funcionário para atualizá-lo: ")).upper()
                funcionario_encontrado = None
                for funcionario in lista_de_funcionarios:
                    if funcionario.matricula == matricula_busca:
                        funcionario_encontrado = funcionario
                        break

                if funcionario_encontrado:
                    print("(Deixe em branco e pressione Enter para não alterar)")
                    
                    novo_nome = input("Digite o novo nome: ")
                    if novo_nome:
                        funcionario_encontrado.nome = novo_nome 

                    novo_cpf = input(f"Digite o novo CPF: ")
                    if novo_cpf:
                        funcionario_encontrado.cpf = novo_cpf 
                    
                    print(f"\n[SUCESSO] Dados do funcionário atualizados!")
                    print(f"Novos dados: {funcionario_encontrado}")
                else:
                    print("ERRO: Nenhum funcionário encontrado com a matrícula informada.")

            except ValueError:
                print("ERRO: Matrícula inválida.")
            input("Pressione Enter para continuar...")

        elif escolha == 4:
            print("\n--- Deletar Funcionário ---")
            if not lista_de_funcionarios:
                print("Nenhum funcionário cadastrado para remover.")
                input("\nPressione Enter para continuar...")
                continue

            for funcionario in lista_de_funcionarios:
                print(f"Matrícula: {funcionario.matricula} | Nome: {funcionario.nome}")
            
            try:
                matricula_busca = str(input("\n Digite a Matrícula do funcionário para removê-lo: ")).upper()

                funcionario_encontrado = None
                for funcionario in lista_de_funcionarios:
                    if funcionario.matricula == matricula_busca:
                        funcionario_encontrado = funcionario
                        break

                if funcionario_encontrado:
                    lista_de_funcionarios.remove(funcionario_encontrado)
                    print(f"{funcionario_encontrado.nome}, removido com sucesso")
                else:
                    print("ERRO: Nenhum funcionário encontrado com a matrícula informada.")

            except ValueError:
                print("ERRO: ID inválido. Digite apenas números.")

            input("Pressione Enter para continuar...")    


        elif escolha == 0:
            break
        else:
            print("Opção inválida.")
            input("Pressione Enter para continuar...")

def submenu_produtos(estoque: Estoque):
    while True:
        titulo = "GERENCIAR PRODUTOS"
        opcoes = [
            "Cadastrar Novo Produto",
            "Listar Todos os Produtos",
            "Atualizar Produto",
            "Deletar Produto"
            ]
        exibir_menu(titulo, opcoes)
        largura_menu = 50
        print(f"| {'0. Voltar'.ljust(largura_menu)} |")
        print("+" + "-" * (largura_menu + 2) + "+")

        try:
            escolha = int(input("Escolha uma opção: "))
        except ValueError:
            print("ERRO: Opção inválida.")
            input("Pressione Enter para continuar...")
            continue
        
        if escolha == 1:
            print("\n--- Cadastro de Novo Produto ---")
            try:
                tipo = input("Tipo (1-Medicamento, 2-Perfumaria), escolha o desejado: ")
                codigo = input("Código do produto: ").upper()
                nome = input("Nome do produto: ")
                preco = float(input("Preço de venda: R$ "))
                codigo_lote = input("Código do primeiro lote: ").upper()
                quantidade = int(input("Quantidade inicial no lote: "))
                ano = int(input("Ano de validade (AAAA): "))
                mes = int(input("Mês de validade (MM): "))
                dia = int(input("Dia de validade (DD): "))
                data_validade = date(ano, mes, dia)

                if tipo == '1':
                    receita = input("Exige receita? (s/n): ").lower() == 's'
                    novo_produto = Medicamento(codigo, nome, preco, receita)
                elif tipo == '2':
                    volume = input("Volume/Descrição (ex: 250ml): ")
                    novo_produto = Perfumaria(codigo, nome, preco, volume)
                else:
                    print("Tipo de produto inválido.")
                    continue
                
                estoque.adicionar_lote(novo_produto, codigo_lote, quantidade, data_validade)

            except ValueError:
                print("ERRO: Preço, data de validade ou quantidade inválidos. Digite apenas números.")
            input("\n Pressione Enter para continuar...")

        elif escolha == 2:
            print("\n--- Lista de Produtos no Estoque ---")
            todos_os_produtos = estoque.produtos
            if not todos_os_produtos:
                print("Nenhum produto cadastrado no estoque.")
            else:
                print(f"\n{'NOME DO PRODUTO'.ljust(30)} | {'ESTOQUE TOTAL'.ljust(15)} | {'PREÇO'.ljust(15)}")
                print("-" * 65)
                for produto in todos_os_produtos:
                    lotes_do_produto = estoque.consultar_lotes_produto(produto)
                    estoque_total = sum(lote.quantidade for lote in lotes_do_produto)
                    preco_formatado = f"R$ {produto.preco:.2f}"
                    print(f"{produto.nome.ljust(30)} | {str(estoque_total).ljust(15)} | {preco_formatado.ljust(15)}")
            input("\n Pressione Enter para continuar...")

        elif escolha == 3:
            print("\n--- Atualizar Produto ---")
            
            print("\n --- Produtos disponíveis ---")
            for produto in estoque.produtos:
                print(f"Código: {produto.codigo} | Nome: {produto.nome}")

            codigo_busca = input("Digite o código do produto que deseja atualizar: ").upper()
            
            produto_encontrado = None
            for produto in estoque.produtos:
                if produto.codigo == codigo_busca:
                    produto_encontrado = produto
                    break
            
            if produto_encontrado:
                print("(Deixe em branco e pressione Enter para não alterar)")
                try:
                    novo_preco_str = input("Digite o novo preço: ")
                    if novo_preco_str:
                        produto_encontrado.preco = float(novo_preco_str)
                    print("Produto atualizado.")
                except ValueError:
                    print("Preço inválido.")
            else:
                print("ERRO: Nenhum produto encontrado com o código informado.")
            input("\n Pressione Enter para continuar...")

        elif escolha == 4:
            print("\n--- Deletar Produto ---")

            if not estoque.produtos:
                print("Nenhum produto cadastrado para deletar.")
            else:
                for produto in estoque.produtos:
                    print(f"Código: {produto.codigo} | Nome: {produto.nome}")

            codigo_busca = input("Digite o código do produto que deseja deletar: ").upper()
            sucesso = estoque.remover_produto(codigo_busca)
            if sucesso:
                    print("\nOperação concluída.")
            else:
                print("\nOperação não concluída.")
            input("\nPressione Enter para continuar...")

        elif escolha == 0:
            break
        else:
            print("ERRO: Opção não existe.")
            input("Pressione Enter para continuar...")

def submenu_orcamentos(lista_de_orcamentos: list, lista_de_clientes: list, estoque: Estoque, funcionario_logado: Funcionario, vendas_pausadas, historico: HistoricoVendas):
    while True:
        titulo = "GERENCIAR ORÇAMENTOS"
        opcoes = [
                "Criar Novo Orçamento",
                "Listar Orçamentos Salvos",
                "Converter Orçamento em Venda"
                ]
        
        exibir_menu(titulo, opcoes)
        largura_menu = 50
        print(f"| {'0. Voltar'.ljust(largura_menu)} |")
        print("+" + "-" * (largura_menu + 2) + "+")

        try:
            escolha = int(input("Escolha uma opção: "))
        except ValueError:
            print("ERRO: Opção inválida."); input("Pressione Enter..."); 
        
        if escolha == 1:
            print("\n--- Criar Novo Orçamento ---")
            if not lista_de_clientes:
                print("Nenhum cliente cadastrado. Cadastre um cliente primeiro."); input("Pressione Enter..."); continue
            
            for cliente in lista_de_clientes: print(f"ID: {cliente.id_cliente} | Nome: {cliente.nome}")
            
            try:
                id_cliente = int(input("Digite o ID do cliente para o orçamento: "))
                cliente_selecionado = next((c for c in lista_de_clientes if c.id_cliente == id_cliente), None)

                if not cliente_selecionado:
                    print("ERRO: Cliente não encontrado."); input("Pressione Enter..."); continue

                novo_orcamento = Orcamento(funcionario_logado, cliente_selecionado)
            
                
                while True:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("--- Editando Orçamento ---")
                    print(novo_orcamento) 
                    print("Opções: \n[1] Adicionar Item \n[2] Remover Item \n[0] Salvar e Sair")
                    escolha_item = input(">> ")

                    if escolha_item == '1':
                        print("\n--- Produtos Disponíveis no Estoque ---")

                        if not estoque.produtos:
                            print("Nenhum produto no estoque para adicionar.")
                            input("Pressione Enter...")
                            continue 
                        else:
                            for produto in estoque.produtos:
                                print(f"Código: {produto.codigo.ljust(15)} | Nome: {produto.nome}")

                        try:
                            cod_produto = input("\nDigite o código do produto a adicionar: ").upper()
                            produto_encontrado = next((p for p in estoque.produtos if p.codigo == cod_produto), None)
                            
                            if produto_encontrado:
                                qtd = int(input(f"Digite a quantidade para '{produto_encontrado.nome}': "))
                                novo_orcamento.adicionar_item(produto_encontrado, qtd)
                            else:
                                print("ERRO: Produto não encontrado."); input("Pressione Enter...")

                        except ValueError:
                            print("ERRO: Quantidade deve ser um número."); input("Pressione Enter...")

                    elif escolha_item == '2':
                        if not novo_orcamento.itens:
                            print("ERRO: Não há itens para remover."); input("Pressione Enter...")
                            continue

                        print("\n--- Itens no Orçamento ---")
                        for i, item in enumerate(novo_orcamento.itens):
                            print(f"  [{i + 1}] {item.produto.nome} (Qtd: {item.quantidade})")
                        
                        try:
                            indice_remover = int(input("Digite o número do item a remover: "))
                            
                            if 1 <= indice_remover <= len(novo_orcamento.itens):
                                item_a_remover = novo_orcamento.itens[indice_remover - 1]
                                
                                novo_orcamento.remover_item(item_a_remover)
                                print(f"[SUCESSO] Item '{item_a_remover.produto.nome}' removido.")
                            else:
                                print("ERRO: Número de item inválido.")
                        except ValueError:
                            print("ERRO: Digite apenas o número do item.")
                        
                        input("Pressione Enter...")

                    elif escolha_item == '0':
                        lista_de_orcamentos.append(novo_orcamento)
                        print(f"[SUCESSO] Orçamento #{novo_orcamento.id_orcamento} salvo.")
                        break
                    else:
                        print("Opção de edição inválida."); input("Pressione Enter...")

            except (ValueError, IndexError):
                print("ERRO: Entrada inválida."); input("Pressione Enter...")
            
            input("Pressione Enter para voltar ao menu de orçamentos...")

        elif escolha == 2:
            print("\n--- Orçamentos Salvos ---")
            if not lista_de_orcamentos:
                print("Nenhum orçamento salvo.")
            else:
                for orcamento in lista_de_orcamentos:
                    print(orcamento)
            input("\nPressione Enter para continuar...")

        elif escolha == 3:
            print("\n--- Converter Orçamento em Venda ---")
            if not lista_de_orcamentos:
                print("Nenhum orçamento salvo para converter."); input("Pressione Enter..."); continue

            for orcamento in lista_de_orcamentos: print(f"ID: {orcamento.id_orcamento} | Cliente: {orcamento.cliente.nome} | Total: R${orcamento.valor_total:.2f}")

            try:
                id_orcamento = int(input("Digite o ID do orçamento a ser convertido: "))
                orcamento_encontrado = next((o for o in lista_de_orcamentos if o.id_orcamento == id_orcamento), None)

                if orcamento_encontrado:
                    nova_venda = orcamento_encontrado.converter_em_venda()
                    lista_de_orcamentos.remove(orcamento_encontrado)
                    print("\n[SUCESSO] Orçamento convertido. Iniciando processamento da venda...")
                    input("Pressione Enter para ir para a tela da venda...")
                    resultado_venda = submenu_venda_ativa(nova_venda, estoque, historico)
                    if resultado_venda and resultado_venda.status == "PAUSADA":
                        vendas_pausadas.append(resultado_venda)
                    print("\nRetornando ao menu de orçamentos...")
                        
                else:
                    print("ERRO: Orçamento não encontrado.")
            except ValueError:
                print("ERRO: ID inválido.")
            input("\nPressione Enter para continuar...")

        elif escolha == 0:
            break
        else:
            print("ERRO: Opção não existe."); input("Pressione Enter...")

def submenu_estoque(estoque: Estoque):
    while True:
        titulo = "GERENCIAR ESTOQUE"
        opcoes = [
            "Adicionar Lote a Produto Existente",
            "Registrar Perda de Lote",
            "Consultar Lotes de um Produto",
            "Gerar Relatório de Baixo Estoque",
            "Gerar Relatório de Lotes a Vencer"
        ]
        exibir_menu(titulo, opcoes)
        largura_menu = 50
        print(f"| {'0. Voltar'.ljust(largura_menu)} |")
        print("+" + "-" * (largura_menu + 2) + "+")

        try:
            escolha = int(input("Escolha uma opção: "))
        except ValueError:
            print("ERRO: Opção inválida."); input("Pressione Enter..."); continue

        if escolha == 1:
            print("\n--- Adicionar Lote a Produto Existente ---")
            for p in estoque.produtos: print(f"Código: {p.codigo} | Nome: {p.nome}")
            cod_produto = input("\nDigite o código do produto: ").upper()
            produto_encontrado = next((p for p in estoque.produtos if p.codigo == cod_produto), None)
            
            if produto_encontrado:
                try:
                    codigo_lote = input("Código do novo lote: ").upper()
                    quantidade = int(input("Quantidade no lote: "))
                    ano = int(input("Ano de validade (AAAA): "))
                    mes = int(input("Mês de validade (MM): "))
                    dia = int(input("Dia de validade (DD): "))
                    data_validade = date(ano, mes, dia)
                    estoque.adicionar_lote(produto_encontrado, codigo_lote, quantidade, data_validade)
                except ValueError:
                    print("ERRO: Dados numéricos inválidos.")
            else:
                print("ERRO: Produto não encontrado.")
            input("\nPressione Enter para continuar...")

        elif escolha == 2:
            print("\n--- Registrar Perda de Lote ---")
            for p in estoque.produtos: print(f"Código: {p.codigo} | Nome: {p.nome}")
            cod_produto = input("\nDigite o código do produto com perda: ").upper()
            produto_encontrado = next((p for p in estoque.produtos if p.codigo == cod_produto), None)

            if produto_encontrado:
                lotes_do_produto = estoque.consultar_lotes_produto(produto_encontrado)
                if not lotes_do_produto:
                    print("Produto não possui lotes."); input("Pressione Enter..."); continue
                
                for i, lote in enumerate(lotes_do_produto): print(f"  [{i + 1}] - {lote}")
                
                try:
                    idx_lote = int(input("Digite o número do lote com perda: "))
                    lote_selecionado = lotes_do_produto[idx_lote - 1]
                    qtd_perdida = int(input("Digite a quantidade perdida: "))
                    motivo = input("Digite o motivo da perda: ")
                    estoque.registrar_perda(lote_selecionado, qtd_perdida, motivo)
                except (ValueError, IndexError):
                    print("ERRO: Seleção ou quantidade inválida.")
            else:
                print("ERRO: Produto não encontrado.")
            input("\nPressione Enter para continuar...")

        elif escolha == 3:
            print("\n--- Consultar Lotes de um Produto ---")
            for p in estoque.produtos: print(f"Código: {p.codigo} | Nome: {p.nome}")
            cod_produto = input("Digite o código do produto para ver os lotes: ").upper()
            produto_encontrado = next((p for p in estoque.produtos if p.codigo == cod_produto), None)

            if produto_encontrado:
                lotes_do_produto = estoque.consultar_lotes_produto(produto_encontrado)
                print(f"\nLotes para '{produto_encontrado.nome}':")
                if not lotes_do_produto:
                    print("Nenhum lote em estoque para este produto.")
                else:
                    for lote in lotes_do_produto: print(f"  - {lote}")
            else:
                print("ERRO: Produto não encontrado.")
            input("\nPressione Enter para continuar...")

        elif escolha == 4:
            try:
                limite = int(input("\nListar produtos com estoque menor ou igual a: "))
                print(f"\n--- Relatório: Produtos com Baixo Estoque dado Limite: {limite} ---")
                
                produtos_encontrados = estoque.listar_produtos_baixo_estoque(limite)

                if not produtos_encontrados:
                    print("Nenhum produto encontrado com estoque baixo.")
                else:
                    print(f"\n{'NOME DO PRODUTO'.ljust(30)} | {'CÓDIGO'.ljust(15)} | {'ESTOQUE ATUAL'}")
                    print("-" * 65)
                    for produto, quantidade in produtos_encontrados:
                        print(f"{produto.nome.ljust(30)} | {produto.codigo.ljust(15)} | {quantidade}")

            except ValueError:
                print("ERRO: Limite inválido. Digite apenas um número.")

            input("\nPressione Enter para continuar...")
            
       
        elif escolha == 5:
            try:
                dias = int(input("\nListar lotes que vencem nos próximos (dias): "))
                print(f"\n--- Relatório: Lotes a Vencer nos Próximos {dias} Dias ---")

                lotes_encontrados = estoque.listar_produtos_proximo_vencimento(dias)

                if not lotes_encontrados:
                    print("Nenhum lote encontrado próximo do vencimento.")
                else:
                    print(f"\n{'PRODUTO'.ljust(25)} | {'LOTE'.ljust(15)} | {'QTD'.ljust(5)} | {'DATA DE VENCIMENTO'}")
                    print("-" * 75)
                    for produto, lote in lotes_encontrados:
                        data_str = lote.data_validade.strftime('%d/%m/%Y')
                        print(f"{produto.nome.ljust(25)} | {lote.codigo_lote.ljust(15)} | {str(lote.quantidade).ljust(5)} | {data_str}")
            except ValueError:
                print("ERRO: Número de dias inválido.")
            input("\nPressione Enter para continuar...")
            
        elif escolha == 0:
            break
        else:
            print("ERRO: Opção não existe.")
            input("Pressione Enter para continuar...")

def submenu_historicos(historico: HistoricoVendas, lista_de_clientes: list, lista_de_funcionarios: list):
    while True:
        titulo = "CONSULTAR HISTÓRICO DE VENDAS"
        opcoes = [
            "Listar Histórico Geral de Vendas",
            "Consultar Histórico por Cliente",
            "Consultar Histórico por Funcionário"
        ]
        exibir_menu(titulo, opcoes)
        largura_menu = 50
        print(f"| {'0. Voltar'.ljust(largura_menu)} |")
        print("+" + "-" * (largura_menu + 2) + "+")

        try:
            escolha = int(input("Escolha uma opção: "))
        except ValueError:
            print("ERRO: Opção inválida."); input("Pressione Enter..."); continue

        if escolha == 1:
            print("\n--- Histórico Geral de Todas as Vendas ---")
            todas_as_vendas = historico.vendas
            if not todas_as_vendas:
                print("Nenhuma venda registrada no histórico.")
            else:
                for venda in todas_as_vendas:
                    print("-" * 50)
                    print(venda)
            input("\nPressione Enter para continuar...")

        elif escolha == 2:
            print("\n--- Histórico de Vendas por Cliente ---")
            if not lista_de_clientes:
                print("Nenhum cliente cadastrado."); input("Pressione Enter..."); continue
            
            for cliente in lista_de_clientes: print(f"ID: {cliente.id_cliente} | Nome: {cliente.nome}")
            
            try:
                id_cliente = int(input("\nDigite o ID do cliente para ver o histórico: "))
                cliente_encontrado = next((c for c in lista_de_clientes if c.id_cliente == id_cliente), None)

                if cliente_encontrado:
                    vendas_do_cliente = historico.consultar_historico_cliente(cliente_encontrado)
                    print(f"\n--- Compras de {cliente_encontrado.nome} ---")
                    if not vendas_do_cliente:
                        print("Nenhuma compra registrada para este cliente.")
                    else:
                        for venda in vendas_do_cliente:
                            print("-" * 50)
                            print(venda)
                else:
                    print("ERRO: Cliente não encontrado.")
            except ValueError:
                print("ERRO: ID inválido.")
            input("\nPressione Enter para continuar...")

        elif escolha == 3:
            print("\n--- Histórico de Vendas por Funcionário ---")
            if not lista_de_funcionarios:
                print("Nenhum funcionário cadastrado."); input("Pressione Enter..."); continue

            for func in lista_de_funcionarios: print(f"Matrícula: {func.matricula} | Nome: {func.nome}")

            try:
                mat_funcionario = input("\nDigite a matrícula do funcionário: ").upper()
                func_encontrado = next((f for f in lista_de_funcionarios if f.matricula == mat_funcionario), None)

                if func_encontrado:
                    vendas_do_funcionario = historico.consultar_historico_funcionario(func_encontrado)
                    print(f"\n--- Vendas de {func_encontrado.nome} ---")
                    if not vendas_do_funcionario:
                        print("Nenhuma venda registrada para este funcionário.")
                    else:
                        for venda in vendas_do_funcionario:
                            print("-" * 50)
                            print(venda)
                else:
                    print("ERRO: Funcionário não encontrado.")
            except ValueError:
                print("ERRO: Entrada inválida.")
            input("\nPressione Enter para continuar...")

        elif escolha == 0:
            break
        else:
            print("ERRO: Opção não existe."); input("Pressione Enter...")
            
def submenu_venda_ativa(venda_em_andamento: Venda, estoque: Estoque, historico: HistoricoVendas):
    while True:
        print("--- VENDA EM ANDAMENTO ---")
        print(venda_em_andamento)

        titulo = f"OPERAÇÕES PARA A VENDA #{venda_em_andamento.id_venda}"
        opcoes = [
            "Adicionar Item",
            "Remover Item",
            "Aplicar Desconto",
            "Pausar Venda",
            "Cancelar Venda",
            "Finalizar Venda (Ir para Pagamento)"
        ]

        exibir_menu(titulo, opcoes)

        try:
            escolha = int(input("Escolha uma ação: "))
        except ValueError:
            print("ERRO: Opção inválida."); input("Pressione Enter..."); continue

        if escolha == 1:
            print("\n--- Adicionar Item à Venda ---")
            
            produtos_disponiveis = [p for p in estoque.produtos if estoque.consultar_quantidade_total(p) > 0]
            if not produtos_disponiveis:
                print("Nenhum produto com estoque para adicionar."); input("Pressione Enter..."); continue

            print("\n--- Produtos Disponíveis ---")
            for produto in produtos_disponiveis:
                print(f"  Código: {produto.codigo.ljust(15)} | Nome: {produto.nome}")

            try:
                cod_produto = input("\nDigite o código do produto a adicionar: ").upper()
                produto_encontrado = next((p for p in estoque.produtos if p.codigo == cod_produto), None)
                    
                if produto_encontrado:
                    qtd = int(input(f"Digite a quantidade para '{produto_encontrado.nome}': "))
                    if qtd <= 0:
                        print("\n[ERRO] A quantidade deve ser um número positivo.")
                        input("Pressione Enter para continuar...")
                        continue

                    estoque_disponivel = estoque.consultar_quantidade_total(produto_encontrado)

                    if qtd > estoque_disponivel:
                        print(f"\n[ERRO] Estoque insuficiente. Disponível: {estoque_disponivel} unidades.")
                    else:
                        venda_em_andamento.adicionar_item(produto_encontrado, qtd)
                        print(f"\n[SUCESSO] {qtd} unidade(s) de '{produto_encontrado.nome}' adicionada(s) à venda.")
                else:
                    print("ERRO: Produto com o código informado não foi encontrado.")
                
            except ValueError:
                print("ERRO: Quantidade deve ser um número inteiro.")
                
            input("Pressione Enter para continuar...")

        elif escolha == 2:
            print("\n--- Remover Item da Venda ---")

            if not venda_em_andamento.itens:
                print("A venda está vazia. Não há itens para remover.")
                input("\nPressione Enter para continuar...")
                continue

            print("\nItens na venda atual:")
            for i, item in enumerate(venda_em_andamento.itens):
                print(f"[{i + 1}] {item}")

            try:
                indice_remover = int(input("\nDigite o número do item a remover: "))
                
                if 1 <= indice_remover <= len(venda_em_andamento.itens):
                    item_a_remover = venda_em_andamento.itens[indice_remover - 1]
                    
                    venda_em_andamento.remover_item(item_a_remover)
                    print("Item removido com sucesso.")

                else:
                    print("ERRO: Número de item inválido.")
            except ValueError:
                print("ERRO: Entrada inválida. Digite apenas o número do item.")
            input("\nPressione Enter para continuar...")

        elif escolha == 3: 
            print("\n--- Aplicar Desconto ---")
            try:
                percentual = float(input("Digite o percentual de desconto (ex: 10 para 10%): "))

                venda_em_andamento.aplicar_desconto(percentual)
            
            except ValueError:
                print("ERRO: Percentual inválido.")
            
            input("Pressione Enter para continuar...")


        elif escolha == 4:
            
            venda_em_andamento.pausar_venda()
            print(f"\nVenda pausada com sucesso.")
            input("Pressione Enter para voltar ao menu do caixa...")
            
            return venda_em_andamento
            
        elif escolha == 5: 
            confirmacao = input("Tem certeza que deseja cancelar esta venda em andamento? (s/n): ").lower()

            if confirmacao == 's':
                venda_em_andamento.cancelar_venda(estoque)
                
                input("\nPressione Enter para voltar ao menu do caixa...")
                return None
            else:
                print("\nOperação de cancelamento abortada.")
                input("Pressione Enter para continuar...")
                
        elif escolha == 6:
            print("\n--- Finalizar Venda ---")

            if not venda_em_andamento.itens:
                print("ERRO: Impossível finalizar uma venda sem itens.")
                input("Pressione Enter para continuar...")
                continue 

            print(f"Valor Total a Pagar: R$ {venda_em_andamento.valor_total:.2f}")
            try:
                forma_pagamento = input("Forma de pagamento (Dinheiro, Débito, Crédito): ")
                valor_pago = float(input("Valor pago pelo cliente: R$ "))

                pagamento_ok = venda_em_andamento.processar_pagamento(forma_pagamento, valor_pago)

                if pagamento_ok:
                    venda_em_andamento.finalizar_venda(estoque, historico)
                    input("\n[SUCESSO] Venda finalizada. Pressione Enter...")
                    return None
                
                else:
                    print("\nPagamento não aprovado. A venda continua ativa.")

            except ValueError:
                print("ERRO: Valor pago inválido. Digite apenas um número.")
            
            input("Pressione Enter para continuar...")

        else:
            print("ERRO: Opção inválida."); input("Pressione Enter...")

def main():
    print("Carregando dados do sistema...")
    lista_de_clientes, lista_de_funcionarios = carregar_pessoas()
    estoque = carregar_estoque()

    historico = carregar_historico(
        lista_de_clientes, 
        lista_de_funcionarios, 
        estoque.produtos
    )

    lista_de_orcamentos = carregar_orcamentos(
        lista_de_clientes,
        lista_de_funcionarios,
        estoque.produtos
    )

    vendas_pausadas = carregar_vendas_pausadas(
        lista_de_clientes,
        lista_de_funcionarios,
        estoque.produtos
    )

    print(f"Carregados {len(lista_de_clientes)} clientes e {len(lista_de_funcionarios)} funcionários.")

    if not lista_de_funcionarios:
        print("Nenhum funcionário encontrado. Criando funcionário de teste...")
        funcionario_logado = Funcionario("Funcionario Teste", "000.000.000-00")
        lista_de_funcionarios.append(funcionario_logado)
    else:
        funcionario_logado = lista_de_funcionarios[0]
        print(f"Usando funcionário: {funcionario_logado.nome}")

    if not lista_de_clientes:
        print("Nenhum cliente encontrado. Criando cliente de teste...")
        cliente_teste = Cliente("Cliente Teste", "111.111.111-11")
        lista_de_clientes.append(cliente_teste)

    if not estoque.produtos:
        print("Nenhum produto em estoque. Criando produto de teste...")
        med_teste = Medicamento("MED_TESTE", "med_teste", 4.99, False)
        estoque.adicionar_lote(med_teste, "diplote001", 100, date(2027, 5, 16))

    while True:
        titulo_menu = f"MENU PRINCIPAL (Funcionario: {funcionario_logado.nome})"
        opcoes_menu = ["Módulo Caixa", "Módulo Balcão", "Sair do Sistema"]
        exibir_menu(titulo_menu, opcoes_menu)

        try:
            escolha = int(input("Digite sua opção: "))
        except ValueError:
            print("ERRO: Por favor, digite um número.")
            input("Pressione Enter para seguir...")
            continue

        if escolha == 1:
            menu_caixa(estoque, historico, funcionario_logado, lista_de_clientes, vendas_pausadas)
            salvar_historico(historico)
            salvar_vendas_pausadas(vendas_pausadas)
            salvar_estoque(estoque)

        elif escolha == 2:
            menu_balcao(lista_de_orcamentos, lista_de_clientes, lista_de_funcionarios, estoque, historico, funcionario_logado, vendas_pausadas)
            salvar_pessoas(lista_de_clientes, lista_de_funcionarios)
            salvar_estoque(estoque)
            salvar_orcamentos(lista_de_orcamentos)
            salvar_vendas_pausadas(vendas_pausadas)

        elif escolha == 3:
            print("Salvando todos os dados...")
            salvar_pessoas(lista_de_clientes, lista_de_funcionarios)
            salvar_estoque(estoque)
            salvar_historico(historico)
            salvar_orcamentos(lista_de_orcamentos)
            salvar_vendas_pausadas(vendas_pausadas)
            print("Saindo do sistema.")
            break
        else:
            input("Pressione Enter para continuar")
    

if __name__ == "__main__": main()