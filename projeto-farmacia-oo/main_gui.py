import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from datetime import date, datetime

from farmacia.entidades.pessoa import Cliente, Funcionario
from farmacia.entidades.produto import Medicamento, Perfumaria
from farmacia.servicos.estoque import Estoque
from farmacia.servicos.venda import HistoricoVendas, Orcamento, Venda
from farmacia.servicos.persistencia import (
    carregar_pessoas, salvar_pessoas,
    carregar_estoque, salvar_estoque,
    carregar_historico, salvar_historico,
    carregar_orcamentos, salvar_orcamentos,
    carregar_vendas_pausadas, salvar_vendas_pausadas
)

class FarmaciaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestão de Farmácia - POO (Final)")
        self.root.geometry("1100x750") 
        
        self.lista_de_clientes = []
        self.lista_de_funcionarios = []
        self.estoque = None
        self.historico = None
        self.lista_de_orcamentos = []
        self.vendas_pausadas = []
        self.funcionario_logado = None

        self.carregar_dados_sistema()
        self.criar_menu_principal()

    def carregar_dados_sistema(self):
        try:
            self.lista_de_clientes, self.lista_de_funcionarios = carregar_pessoas()
            self.estoque = carregar_estoque()
            
            self.historico = carregar_historico(
                self.lista_de_clientes, self.lista_de_funcionarios, self.estoque.produtos
            )
            self.lista_de_orcamentos = carregar_orcamentos(
                self.lista_de_clientes, self.lista_de_funcionarios, self.estoque.produtos
            )
            self.vendas_pausadas = carregar_vendas_pausadas(
                self.lista_de_clientes, self.lista_de_funcionarios, self.estoque.produtos
            )
            
            if not self.lista_de_funcionarios:
                self.lista_de_funcionarios.append(Funcionario("Funcionario Admin", "000.000.000-00"))
            self.funcionario_logado = self.lista_de_funcionarios[0]

            if not self.lista_de_clientes:
                self.lista_de_clientes.append(Cliente("Cliente Balcão", "111.111.111-11"))

            if not self.estoque.produtos:
                med = Medicamento("DIPIRONA", "Dipirona 500mg", 5.99, False)
                self.estoque.adicionar_lote(med, "LOTE_INI", 50, date(2027, 12, 31))

        except Exception as e:
            messagebox.showerror("Erro Crítico", f"Falha ao carregar dados: {e}")

    def limpar_janela(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # =========================================================================
    # --- MENU PRINCIPAL ---
    # =========================================================================
    def criar_menu_principal(self):
        self.limpar_janela()
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(expand=True)

        tk.Label(main_frame, text="Sistema de Farmácia", font=("Helvetica", 26, "bold"), fg="#2c3e50").pack(pady=10)
        
        if self.funcionario_logado:
            tk.Label(main_frame, text=f"Logado como: {self.funcionario_logado.nome}", fg="blue", font=("Arial", 10)).pack()

        tk.Label(main_frame, text="Selecione o Módulo:", font=("Arial", 14)).pack(pady=20)

        tk.Button(main_frame, text="MÓDULO CAIXA (Vendas)", font=("Arial", 14, "bold"), bg="#ddffdd", width=35, height=2,
                  command=self.abrir_modulo_caixa).pack(pady=10)

        tk.Button(main_frame, text="MÓDULO BALCÃO (Gerência)", font=("Arial", 14), width=35, height=2,
                  command=self.abrir_modulo_balcao).pack(pady=10)

        tk.Button(main_frame, text="Sair e Salvar", font=("Arial", 12), bg="#ffcccc", width=20,
                  command=self.sair_do_sistema).pack(pady=40)

    def sair_do_sistema(self):
        if messagebox.askyesno("Sair", "Deseja salvar todos os dados e sair?"):
            try:
                salvar_pessoas(self.lista_de_clientes, self.lista_de_funcionarios)
                salvar_estoque(self.estoque)
                salvar_historico(self.historico)
                salvar_orcamentos(self.lista_de_orcamentos)
                salvar_vendas_pausadas(self.vendas_pausadas)
                self.root.destroy()
            except Exception as e:
                messagebox.showerror("Erro ao Salvar", str(e))

    # =========================================================================
    # --- MÓDULO CAIXA ---
    # =========================================================================
    def abrir_modulo_caixa(self):
        self.limpar_janela()
        tk.Label(self.root, text="Módulo Caixa", font=("Helvetica", 18, "bold")).pack(pady=20)

        frame_btns = tk.Frame(self.root)
        frame_btns.pack(pady=10)

        tk.Button(frame_btns, text="Iniciar Nova Venda", font=("Arial", 12), bg="#ddffdd", width=30, height=2,
                  command=self._iniciar_nova_venda).pack(pady=10)
        
        tk.Button(frame_btns, text="Retomar Venda Pausada", font=("Arial", 12), width=30, height=2,
                  command=self._listar_vendas_pausadas).pack(pady=10)
        
        tk.Button(frame_btns, text="Cancelar Venda (Estorno)", font=("Arial", 12), bg="#ffdddd", width=30, height=2,
                  command=self._tela_cancelar_venda_finalizada).pack(pady=10)

        tk.Button(self.root, text="Voltar ao Menu Principal", width=20, 
                  command=self.criar_menu_principal).pack(pady=30)

    def _iniciar_nova_venda(self):
        if not self.lista_de_clientes: return messagebox.showerror("Erro", "Nenhum cliente cadastrado.")

        win_cli = tk.Toplevel(self.root)
        win_cli.title("Selecionar Cliente")
        win_cli.geometry("400x400")
        
        tk.Label(win_cli, text="Selecione o Cliente:", font=("Arial", 12)).pack(pady=10)
        listbox = tk.Listbox(win_cli, font=("Courier", 10))
        listbox.pack(expand=True, fill='both', padx=10)
        
        for cli in self.lista_de_clientes: listbox.insert(tk.END, f"{cli.id_cliente} - {cli.nome}")

        def confirmar():
            sel = listbox.curselection()
            if not sel: return
            cliente = self.lista_de_clientes[sel[0]]
            win_cli.destroy()
            self._tela_venda_ativa(Venda(self.funcionario_logado, cliente))

        tk.Button(win_cli, text="Confirmar", bg="#ddffdd", command=confirmar).pack(pady=10)

    def _listar_vendas_pausadas(self):
        if not self.vendas_pausadas: return messagebox.showinfo("Aviso", "Nenhuma venda pausada.")

        win = tk.Toplevel(self.root)
        win.title("Retomar Venda")
        win.geometry("500x400")

        listbox = tk.Listbox(win, font=("Courier", 10))
        listbox.pack(expand=True, fill='both', padx=10, pady=10)

        for v in self.vendas_pausadas: listbox.insert(tk.END, f"ID: {v.id_venda} | Cli: {v.cliente.nome} | Total: R${v.valor_total:.2f}")

        def retomar():
            sel = listbox.curselection()
            if not sel: return
            venda = self.vendas_pausadas.pop(sel[0])
            venda.retomar_venda()
            win.destroy()
            self._tela_venda_ativa(venda)

        tk.Button(win, text="Retomar Selecionada", bg="#ddffdd", command=retomar).pack(pady=10)

    def _tela_venda_ativa(self, venda_obj):
        """Tela principal do PDV (Ponto de Venda)"""
        self.limpar_janela()
        
        frame_info = tk.Frame(self.root, bg="#f0f0f0", padx=10, pady=10)
        frame_info.pack(fill='x')
        tk.Label(frame_info, text=f"VENDA #{venda_obj.id_venda} - {venda_obj.status}", font=("Arial", 14, "bold"), bg="#f0f0f0").pack(side=tk.LEFT)
        tk.Label(frame_info, text=f"Cliente: {venda_obj.cliente.nome}", font=("Arial", 12), bg="#f0f0f0").pack(side=tk.RIGHT)

        frame_itens = tk.Frame(self.root)
        frame_itens.pack(expand=True, fill='both', padx=10, pady=5)
        
        cols = ("Produto", "Qtd", "Preço Un.", "Subtotal")
        tree = ttk.Treeview(frame_itens, columns=cols, show='headings')
        for col in cols: tree.heading(col, text=col)
        tree.pack(side=tk.LEFT, expand=True, fill='both')
        
        scroll = tk.Scrollbar(frame_itens, command=tree.yview); scroll.pack(side=tk.RIGHT, fill='y')
        tree.config(yscrollcommand=scroll.set)

        lbl_total = tk.Label(self.root, text=f"TOTAL: R$ {venda_obj.valor_total:.2f}", font=("Arial", 20, "bold"), fg="green")
        lbl_total.pack(pady=10)

        def atualizar_lista_itens():
            for i in tree.get_children(): tree.delete(i)
            for item in venda_obj.itens:
                tree.insert("", tk.END, values=(item.produto.nome, item.quantidade, f"R$ {item.preco_momento:.2f}", f"R$ {item.calcular_subtotal():.2f}"))
            lbl_total.config(text=f"TOTAL: R$ {venda_obj.valor_total:.2f}")

        atualizar_lista_itens()

        frame_acoes = tk.Frame(self.root, pady=10)
        frame_acoes.pack(fill='x', padx=10)

        def acao_adicionar_item():
            win_add = tk.Toplevel(self.root)
            win_add.title("Adicionar Item")
            win_add.geometry("600x400")
            
            prods = [p for p in self.estoque.produtos if self.estoque.consultar_quantidade_total(p) > 0]
            list_prod = tk.Listbox(win_add, font=("Courier", 10))
            list_prod.pack(expand=True, fill='both', padx=10)
            
            for p in prods:
                list_prod.insert(tk.END, f"{p.codigo} | {p.nome} | R${p.preco:.2f} | Est: {self.estoque.consultar_quantidade_total(p)}")

            def confirmar_add():
                sel = list_prod.curselection()
                if not sel: return
                prod = prods[sel[0]]
                try:
                    qtd = simpledialog.askinteger("Qtd", f"Quantos '{prod.nome}'?")
                    if not qtd: return
                    if qtd > self.estoque.consultar_quantidade_total(prod):
                        return messagebox.showerror("Erro", "Estoque insuficiente.")
                    venda_obj.adicionar_item(prod, qtd)
                    atualizar_lista_itens()
                    win_add.destroy()
                except ValueError as e: messagebox.showerror("Erro", str(e))

            tk.Button(win_add, text="Adicionar", bg="#ddffdd", command=confirmar_add).pack(pady=10)

        def acao_remover_item():
            sel = tree.selection()
            if not sel: return
            item = venda_obj.itens[tree.index(sel[0])]
            venda_obj.remover_item(item)
            atualizar_lista_itens()

        def acao_desconto():
            perc = simpledialog.askfloat("Desconto", "% (0-100):")
            if perc is not None: venda_obj.aplicar_desconto(perc); atualizar_lista_itens()

        def acao_pausar():
            venda_obj.pausar_venda()
            self.vendas_pausadas.append(venda_obj)
            messagebox.showinfo("Pausada", "Venda salva."); self.abrir_modulo_caixa()

        def acao_cancelar():
            if messagebox.askyesno("Cancelar", "Descartar venda atual?"):
                venda_obj.cancelar_venda(self.estoque); self.abrir_modulo_caixa()

        def acao_finalizar():
            if not venda_obj.itens: return messagebox.showwarning("Erro", "Venda vazia.")
            win_pay = tk.Toplevel(self.root)
            win_pay.title("Pagamento")
            win_pay.geometry("300x250")
            
            tk.Label(win_pay, text=f"Total: R$ {venda_obj.valor_total:.2f}", font=("Arial", 12, "bold")).pack(pady=10)
            combo = ttk.Combobox(win_pay, values=["Dinheiro", "Débito", "Crédito"]); combo.pack(); combo.current(0)
            entry_val = tk.Entry(win_pay); entry_val.pack()

            def processar():
                try:
                    val = float(entry_val.get())
                    if venda_obj.processar_pagamento(combo.get(), val):
                        if combo.get() == "Dinheiro" and (val - venda_obj.valor_total) > 0:
                            messagebox.showinfo("Troco", f"Troco: R$ {val - venda_obj.valor_total:.2f}")
                        venda_obj.finalizar_venda(self.estoque, self.historico)
                        messagebox.showinfo("Sucesso", "Venda Finalizada!"); win_pay.destroy(); self.abrir_modulo_caixa()
                    else: messagebox.showerror("Erro", "Pagamento Recusado.")
                except: messagebox.showerror("Erro", "Valor inválido.")

            tk.Button(win_pay, text="Pagar", bg="#ddffdd", command=processar).pack(pady=20)

        btn_f1 = tk.Frame(frame_acoes); btn_f1.pack(pady=5)
        tk.Button(btn_f1, text="+ Item", bg="#ddffdd", command=acao_adicionar_item).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_f1, text="- Item", command=acao_remover_item).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_f1, text="% Desc", command=acao_desconto).pack(side=tk.LEFT, padx=5)

        btn_f2 = tk.Frame(frame_acoes); btn_f2.pack(pady=10)
        tk.Button(btn_f2, text="Pausar", width=15, command=acao_pausar).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_f2, text="Cancelar", bg="#ffcccc", width=15, command=acao_cancelar).pack(side=tk.LEFT, padx=5)
        
        tk.Button(self.root, text="FINALIZAR VENDA ($)", bg="#27ae60", fg="white", font=("Arial", 14, "bold"), width=30, height=2,
                  command=acao_finalizar).pack(side=tk.BOTTOM, pady=20)

    def _tela_cancelar_venda_finalizada(self):
        id_v = simpledialog.askinteger("Estorno", "ID da Venda:")
        if not id_v: return
        v = self.historico.buscar_venda_por_id(id_v)
        if v and v.status == "FINALIZADA":
            if messagebox.askyesno("Estorno", f"Cancelar venda de R${v.valor_total:.2f} e devolver ao estoque?"):
                v.cancelar_venda(self.estoque); messagebox.showinfo("Sucesso", "Estornado.")
        else: messagebox.showerror("Erro", "Venda não encontrada ou não finalizada.")

    # =========================================================================
    # --- MÓDULO BALCÃO ---
    # =========================================================================
    def abrir_modulo_balcao(self):
        self.limpar_janela()
        tk.Label(self.root, text="Módulo Balcão", font=("Helvetica", 18, "bold")).pack(pady=10)

        btn_frame = tk.Frame(self.root); btn_frame.pack(pady=10)

        tk.Label(btn_frame, text="--- Pessoas ---", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=10, pady=5)
        tk.Button(btn_frame, text="Gerenciar Clientes", width=25, command=lambda: self._abrir_crud_pessoas("Clientes", self.lista_de_clientes, Cliente)).grid(row=1, column=0, padx=10, pady=5)
        tk.Button(btn_frame, text="Gerenciar Funcionários", width=25, command=lambda: self._abrir_crud_pessoas("Funcionários", self.lista_de_funcionarios, Funcionario)).grid(row=2, column=0, padx=10, pady=5)

        tk.Label(btn_frame, text="--- Produtos/Estoque ---", font=("Arial", 10, "bold")).grid(row=0, column=1, padx=10, pady=5)
        tk.Button(btn_frame, text="Gerenciar Produtos", width=25, command=self._abrir_gerenciar_produtos).grid(row=1, column=1, padx=10, pady=5)
        tk.Button(btn_frame, text="Gerenciar Estoque (Lotes)", width=25, command=self._abrir_gerenciar_estoque).grid(row=2, column=1, padx=10, pady=5)

        tk.Label(btn_frame, text="--- Vendas ---", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=10, pady=5)
        tk.Button(btn_frame, text="Gerenciar Orçamentos", width=25, command=self._abrir_gerenciar_orcamentos).grid(row=1, column=2, padx=10, pady=5)
        tk.Button(btn_frame, text="Histórico de Vendas", width=25, command=self._abrir_historico_vendas).grid(row=2, column=2, padx=10, pady=5)

        tk.Button(self.root, text="Voltar ao Menu Principal", bg="#e6e6e6", width=20,
                  command=self.criar_menu_principal).pack(pady=30)

    def _abrir_crud_pessoas(self, titulo_janela, lista_dados, ClasseEntidade):
        self.limpar_janela()
        tk.Label(self.root, text=f"Gerenciar {titulo_janela}", font=("Arial", 16, "bold")).pack(pady=10)

        frame_list = tk.Frame(self.root); frame_list.pack(expand=True, fill='both', padx=20)
        scroll = tk.Scrollbar(frame_list); scroll.pack(side=tk.RIGHT, fill=tk.Y)
        listbox = tk.Listbox(frame_list, font=("Courier", 10), yscrollcommand=scroll.set)
        listbox.pack(side=tk.LEFT, expand=True, fill='both'); scroll.config(command=listbox.yview)

        def atualizar(): listbox.delete(0, tk.END); [listbox.insert(tk.END, str(i)) for i in lista_dados]
        atualizar()

        frame_btn = tk.Frame(self.root, pady=10); frame_btn.pack(fill='x', padx=20)
        
        def novo():
            nome = simpledialog.askstring("Novo", "Nome:"); cpf = simpledialog.askstring("Novo", "CPF:")
            if nome and cpf: lista_dados.append(ClasseEntidade(nome, cpf)); atualizar()
        
        def editar():
            sel = listbox.curselection()
            if not sel: return
            obj = lista_dados[sel[0]]
            n = simpledialog.askstring("Ed", "Nome:", initialvalue=obj.nome); c = simpledialog.askstring("Ed", "CPF:", initialvalue=obj.cpf)
            if n: obj.nome = n
            if c: obj.cpf = c
            atualizar()
            
        def deletar():
            sel = listbox.curselection()
            if not sel: return
            if messagebox.askyesno("Del", "Apagar?"): lista_dados.pop(sel[0]); atualizar()

        tk.Button(frame_btn, text="Novo", bg="#ddffdd", command=novo).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_btn, text="Editar", command=editar).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_btn, text="Deletar", bg="#ffcccc", command=deletar).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_btn, text="Voltar", command=self.abrir_modulo_balcao).pack(side=tk.RIGHT)

    def _abrir_gerenciar_produtos(self):
        self.limpar_janela()
        tk.Label(self.root, text="Gerenciar Produtos", font=("Arial", 16, "bold")).pack(pady=10)
        
        cols = ("Código", "Nome", "Preço", "Tipo", "Estoque"); tree = ttk.Treeview(self.root, columns=cols, show='headings')
        for c in cols: tree.heading(c, text=c); tree.column(c, width=120)
        tree.pack(expand=True, fill='both', padx=20)
        
        def atualizar():
            [tree.delete(i) for i in tree.get_children()]
            for p in self.estoque.produtos:
                tree.insert("", tk.END, values=(p.codigo, p.nome, f"{p.preco:.2f}", type(p).__name__, self.estoque.consultar_quantidade_total(p)))
        atualizar()
        
        def novo():
            win = tk.Toplevel(self.root); win.geometry("300x450")
            tk.Label(win, text="Tipo (Medicamento/Perfumaria):").pack(); tipo = tk.Entry(win); tipo.pack()
            tk.Label(win, text="Cod:").pack(); cod = tk.Entry(win); cod.pack()
            tk.Label(win, text="Nome:").pack(); nome = tk.Entry(win); nome.pack()
            tk.Label(win, text="Preço:").pack(); preco = tk.Entry(win); preco.pack()
            tk.Label(win, text="Extra (Receita/Volume):").pack(); extra = tk.Entry(win); extra.pack()
            
            tk.Label(win, text="-- Lote Inicial --").pack(pady=5)
            tk.Label(win, text="Cod Lote:").pack(); l_cod = tk.Entry(win); l_cod.pack()
            tk.Label(win, text="Qtd:").pack(); l_qtd = tk.Entry(win); l_qtd.pack()
            tk.Label(win, text="Data (d/m/y):").pack(); l_dat = tk.Entry(win); l_dat.pack()
            
            def save():
                try:
                    p = float(preco.get()); q = int(l_qtd.get()); d,m,a = map(int, l_dat.get().split('/'))
                    prod = Medicamento(cod.get().upper(), nome.get(), p, extra.get()=='s') if tipo.get().lower().startswith('m') else Perfumaria(cod.get().upper(), nome.get(), p, extra.get())
                    self.estoque.adicionar_lote(prod, l_cod.get(), q, date(a,m,d))
                    atualizar(); win.destroy()
                except Exception as e: messagebox.showerror("Erro", str(e))
            tk.Button(win, text="Salvar", command=save).pack(pady=20)

        def deletar():
            sel = tree.selection()
            if sel and messagebox.askyesno("Confirmar", "Deletar?"): self.estoque.remover_produto(tree.item(sel[0])['values'][0]); atualizar()

        frame_btn = tk.Frame(self.root, pady=10); frame_btn.pack(fill='x', padx=20)
        tk.Button(frame_btn, text="Novo", bg="#ddffdd", command=novo).pack(side=tk.LEFT)
        tk.Button(frame_btn, text="Deletar", bg="#ffcccc", command=deletar).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_btn, text="Voltar", command=self.abrir_modulo_balcao).pack(side=tk.RIGHT)

    def _abrir_gerenciar_estoque(self):
        self.limpar_janela()
        tk.Label(self.root, text="Gerenciar Estoque", font=("Arial", 16)).pack(pady=10)
        
        tree = ttk.Treeview(self.root, columns=("Cod", "Nome", "Total"), show='headings'); tree.pack(fill='x', padx=20)
        for c in ("Cod", "Nome", "Total"): tree.heading(c, text=c)
        for p in self.estoque.produtos: tree.insert("", tk.END, values=(p.codigo, p.nome, self.estoque.consultar_quantidade_total(p)))
        
        def get_sel():
            s = tree.selection()
            return next((p for p in self.estoque.produtos if p.codigo == str(tree.item(s[0])['values'][0])), None) if s else None

        def add_lote():
            p = get_sel()
            if not p: return
            try:
                c = simpledialog.askstring("Lote", "Cod:"); q = simpledialog.askinteger("Qtd", "Qtd:"); d = simpledialog.askstring("Data", "dd/mm/aaaa")
                di,me,an = map(int, d.split('/'))
                self.estoque.adicionar_lote(p, c, q, date(an,me,di)); self._abrir_gerenciar_estoque()
            except: messagebox.showerror("Erro", "Dados inválidos")

        def ver():
            p = get_sel()
            if p: messagebox.showinfo("Lotes", "\n".join([str(l) for l in self.estoque.consultar_lotes_produto(p)]))

        f = tk.Frame(self.root, pady=10); f.pack()
        tk.Button(f, text="Add Lote", command=add_lote).pack(side=tk.LEFT, padx=5)
        tk.Button(f, text="Ver Lotes", command=ver).pack(side=tk.LEFT, padx=5)
        tk.Button(self.root, text="Voltar", command=self.abrir_modulo_balcao).pack(pady=10)

    # =========================================================================
    # --- NOVO: GERENCIAR ORÇAMENTOS ---
    # =========================================================================
    def _abrir_gerenciar_orcamentos(self):
        self.limpar_janela()
        tk.Label(self.root, text="Gerenciar Orçamentos", font=("Arial", 16, "bold")).pack(pady=10)

        cols = ("ID", "Cliente", "Data", "Total")
        tree = ttk.Treeview(self.root, columns=cols, show='headings')
        for c in cols: tree.heading(c, text=c)
        tree.pack(expand=True, fill='both', padx=20)

        def atualizar():
            for i in tree.get_children(): tree.delete(i)
            for o in self.lista_de_orcamentos:
                tree.insert("", tk.END, values=(o.id_orcamento, o.cliente.nome, o.data_hora.strftime("%d/%m %H:%M"), f"R$ {o.valor_total:.2f}"))
        atualizar()

        frame_btns = tk.Frame(self.root, pady=10); frame_btns.pack(fill='x', padx=20)

        def novo_orcamento():
            if not self.lista_de_clientes: return messagebox.showerror("Erro", "Sem clientes.")
            
            cli_nome = simpledialog.askstring("Novo Orçamento", "Parte do nome do cliente:")
            if not cli_nome: return
            cliente = next((c for c in self.lista_de_clientes if cli_nome.lower() in c.nome.lower()), None)
            if not cliente: return messagebox.showerror("Erro", "Cliente não achado.")

            orc = Orcamento(self.funcionario_logado, cliente)
            
            win_orc = tk.Toplevel(self.root); win_orc.geometry("500x500"); win_orc.title("Editando Orçamento")
            
            lbl_info = tk.Label(win_orc, text=f"Orçamento para {cliente.nome}")
            lbl_info.pack(pady=5)
            
            lb_itens = tk.Listbox(win_orc); lb_itens.pack(fill='both', expand=True, padx=10)
            
            def refresh_itens():
                lb_itens.delete(0, tk.END)
                for it in orc.itens: lb_itens.insert(tk.END, f"{it.produto.nome} ({it.quantidade}) - R${it.calcular_subtotal():.2f}")
                lbl_info.config(text=f"Total: R$ {orc.valor_total:.2f}")

            def add_item():
                cod = simpledialog.askstring("Add", "Código do Produto:")
                prod = next((p for p in self.estoque.produtos if p.codigo == cod), None)
                if prod:
                    q = simpledialog.askinteger("Qtd", "Quantidade:")
                    if q: orc.adicionar_item(prod, q); refresh_itens()
                else: messagebox.showerror("Erro", "Produto não encontrado")

            def salvar_sair():
                self.lista_de_orcamentos.append(orc)
                win_orc.destroy(); atualizar()

            tk.Button(win_orc, text="+ Adicionar Produto pelo Código", command=add_item).pack(pady=5)
            tk.Button(win_orc, text="SALVAR ORÇAMENTO", bg="#ddffdd", command=salvar_sair).pack(pady=10)

        def converter_venda():
            sel = tree.selection()
            if not sel: return messagebox.showwarning("Aviso", "Selecione um orçamento.")
            idx = tree.index(sel[0])
            orc = self.lista_de_orcamentos[idx]
            
            nova_venda = orc.converter_em_venda()
            self.lista_de_orcamentos.pop(idx)
            
            messagebox.showinfo("Sucesso", "Orçamento convertido! Redirecionando para o Caixa...")
            self._tela_venda_ativa(nova_venda)

        tk.Button(frame_btns, text="Criar Novo Orçamento", bg="#ddffdd", command=novo_orcamento).pack(side=tk.LEFT)
        tk.Button(frame_btns, text="Converter em Venda (Ir p/ Caixa)", bg="#3498db", fg="white", command=converter_venda).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_btns, text="Voltar", command=self.abrir_modulo_balcao).pack(side=tk.RIGHT)

    # =========================================================================
    # --- HISTÓRICO DE VENDAS ---
    # =========================================================================
    def _abrir_historico_vendas(self):
        self.limpar_janela()
        tk.Label(self.root, text="Histórico de Vendas Finalizadas", font=("Arial", 16, "bold")).pack(pady=10)

        cols = ("ID", "Data", "Cliente", "Funcionário", "Total")
        tree = ttk.Treeview(self.root, columns=cols, show='headings')
        for c in cols: tree.heading(c, text=c)
        tree.column("ID", width=50); tree.column("Total", width=100)
        tree.pack(expand=True, fill='both', padx=20)

        for v in self.historico.vendas:
            tree.insert("", tk.END, values=(v.id_venda, v.data_hora.strftime("%d/%m/%Y %H:%M"), v.cliente.nome, v.funcionario.nome, f"R$ {v.valor_total:.2f}"))

        def ver_detalhes():
            sel = tree.selection()
            if not sel: return
            id_v = tree.item(sel[0])['values'][0]
            venda = self.historico.buscar_venda_por_id(int(id_v))
            
            detalhes = f"Venda #{venda.id_venda}\nStatus: {venda.status}\n\nITENS:\n"
            for item in venda.itens:
                detalhes += f"- {item.produto.nome} (x{item.quantidade}) = R${item.calcular_subtotal():.2f}\n"
            detalhes += f"\nTOTAL FINAL: R$ {venda.valor_total:.2f}"
            messagebox.showinfo("Detalhes da Venda", detalhes)

        tk.Button(self.root, text="Ver Detalhes", command=ver_detalhes).pack(pady=10)
        tk.Button(self.root, text="Voltar", command=self.abrir_modulo_balcao).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = FarmaciaApp(root)
    root.mainloop()