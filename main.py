import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

# Conectar ao banco de dados
conn = sqlite3.connect("estoque_empresa.db")
cursor = conn.cursor()

# Criar tabelas se não existirem
cursor.execute('''CREATE TABLE IF NOT EXISTS produtos
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, categoria TEXT, 
                   quantidade INTEGER, preco REAL)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS movimentacoes
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, produto_id INTEGER, 
                   tipo TEXT, quantidade INTEGER, data TEXT)''')
conn.commit()

# Função para adicionar produto
def adicionar_produto():
    nome = entry_nome.get().strip().lower()
    categoria = combo_categoria.get()
    try:
        quantidade = int(entry_quantidade.get())
        preco = float(entry_preco.get())
        
        if nome and categoria:
            cursor.execute("INSERT INTO produtos (nome, categoria, quantidade, preco) VALUES (?, ?, ?, ?)",
                           (nome, categoria, quantidade, preco))
            produto_id = cursor.lastrowid
            registrar_movimentacao(produto_id, "entrada", quantidade)
            conn.commit()
            atualizar_tabela()
            messagebox.showinfo("Sucesso", f"Produto '{nome}' adicionado!")
            limpar_campos()
        else:
            messagebox.showwarning("Erro", "Preencha nome e categoria.")
    except ValueError:
        messagebox.showerror("Erro", "Quantidade e preço devem ser números válidos.")

# Função para remover produto
def remover_produto():
    selecionado = tabela.selection()
    if selecionado:
        item = tabela.item(selecionado[0])["values"]
        produto_id = item[0]
        cursor.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
        registrar_movimentacao(produto_id, "saída", item[3])  # Quantidade antes de remover
        conn.commit()
        atualizar_tabela()
        messagebox.showinfo("Sucesso", "Produto removido!")
    else:
        messagebox.showwarning("Erro", "Selecione um produto para remover.")

# Função para atualizar quantidade
def atualizar_quantidade():
    selecionado = tabela.selection()
    if selecionado:
        item = tabela.item(selecionado[0])["values"]
        produto_id = item[0]
        try:
            nova_quantidade = int(entry_quantidade.get())
            cursor.execute("UPDATE produtos SET quantidade = ? WHERE id = ?", (nova_quantidade, produto_id))
            tipo = "entrada" if nova_quantidade > item[3] else "saída"
            registrar_movimentacao(produto_id, tipo, abs(nova_quantidade - item[3]))
            conn.commit()
            atualizar_tabela()
            messagebox.showinfo("Sucesso", "Quantidade atualizada!")
            limpar_campos()
        except ValueError:
            messagebox.showerror("Erro", "Quantidade deve ser um número válido.")
    else:
        messagebox.showwarning("Erro", "Selecione um produto para atualizar.")

# Registrar movimentação no histórico
def registrar_movimentacao(produto_id, tipo, quantidade):
    data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO movimentacoes (produto_id, tipo, quantidade, data) VALUES (?, ?, ?, ?)",
                   (produto_id, tipo, quantidade, data))

# Atualizar a tabela de estoque
def atualizar_tabela():
    for row in tabela.get_children():
        tabela.delete(row)
    cursor.execute("SELECT id, nome, categoria, quantidade, preco FROM produtos")
    for row in cursor.fetchall():
        tabela.insert("", "end", values=row)

# Limpar campos de entrada
def limpar_campos():
    entry_nome.delete(0, tk.END)
    entry_quantidade.delete(0, tk.END)
    entry_preco.delete(0, tk.END)
    combo_categoria.set("")

# Configuração da janela
janela = tk.Tk()
janela.title("Estoque - Bahia")
janela.geometry("700x500")

# Frame para entrada de dados
frame_entrada = tk.Frame(janela)
frame_entrada.pack(pady=10)

tk.Label(frame_entrada, text="Nome:").grid(row=0, column=0, padx=5)
entry_nome = tk.Entry(frame_entrada)
entry_nome.grid(row=0, column=1, padx=5)

tk.Label(frame_entrada, text="Categoria:").grid(row=0, column=2, padx=5)
combo_categoria = ttk.Combobox(frame_entrada, values=["Alimentos", "Bebidas", "Higiene", "Limpeza"])
combo_categoria.grid(row=0, column=3, padx=5)

tk.Label(frame_entrada, text="Quantidade:").grid(row=1, column=0, padx=5)
entry_quantidade = tk.Entry(frame_entrada)
entry_quantidade.grid(row=1, column=1, padx=5)

tk.Label(frame_entrada, text="Preço:").grid(row=1, column=2, padx=5)
entry_preco = tk.Entry(frame_entrada)
entry_preco.grid(row=1, column=3, padx=5)

# Botões
frame_botoes = tk.Frame(janela)
frame_botoes.pack(pady=10)

tk.Button(frame_botoes, text="Adicionar", command=adicionar_produto).pack(side=tk.LEFT, padx=5)
tk.Button(frame_botoes, text="Remover", command=remover_produto).pack(side=tk.LEFT, padx=5)
tk.Button(frame_botoes, text="Atualizar Quantidade", command=atualizar_quantidade).pack(side=tk.LEFT, padx=5)

# Tabela de estoque
tabela = ttk.Treeview(janela, columns=("ID", "Nome", "Categoria", "Quantidade", "Preço"), show="headings")
tabela.heading("ID", text="ID")
tabela.heading("Nome", text="Nome")
tabela.heading("Categoria", text="Categoria")
tabela.heading("Quantidade", text="Quantidade")
tabela.heading("Preço", text="Preço (R$)")
tabela.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Atualizar tabela ao iniciar
atualizar_tabela()

# Iniciar a janela
janela.mainloop()

# Fechar conexão ao sair
conn.close()