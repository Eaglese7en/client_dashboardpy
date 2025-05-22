import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path
import requests

# Optional: Animações com Lottie
try:
    from streamlit_lottie import st_lottie
except ImportError:
    st_lottie = None

# Caminho do banco de dados
DB_PATH = "workshop.db"

# Função para criar as tabelas se não existirem
def criar_tabelas():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS clientes (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nome TEXT NOT NULL,
                            telefone TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS carros (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            cliente_id INTEGER,
                            modelo TEXT,
                            ano INTEGER,
                            cor TEXT,
                            status TEXT,
                            FOREIGN KEY(cliente_id) REFERENCES clientes(id))''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS orcamentos (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            carro_id INTEGER,
                            servico TEXT,
                            preco_estimado REAL,
                            preco_final REAL,
                            FOREIGN KEY(carro_id) REFERENCES carros(id))''')

# Carregar animação Lottie
def carregar_lottie(url):
    try:
        r = requests.get(url, timeout=5)  # Timeout para não travar
        if r.status_code == 200:
            return r.json()
    except:
        return None
    return None

# Exibir dados de clientes
def pagina_clientes():
    st.subheader("Cadastro de Clientes")

    with st.form("form_cliente"):
        nome = st.text_input("Nome do Cliente")
        telefone = st.text_input("Telefone")
        submit = st.form_submit_button("Salvar Cliente")

        if submit and nome:
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute("INSERT INTO clientes (nome, telefone) VALUES (?, ?)", (nome, telefone))
                conn.commit()
                st.success("Cliente salvo com sucesso!")

    # Mostrar tabela de clientes
    clientes = pd.read_sql("SELECT * FROM clientes", sqlite3.connect(DB_PATH))
    st.dataframe(clientes, use_container_width=True)

# Exibir e editar carros
def pagina_carros():
    st.subheader("Cadastro de Carros")

    clientes = pd.read_sql("SELECT * FROM clientes", sqlite3.connect(DB_PATH))
    if clientes.empty:
        st.warning("Cadastre um cliente antes de adicionar carros.")
        return

    with st.form("form_carro"):
        cliente_nome = st.selectbox("Cliente", clientes["nome"])
        cliente_id = clientes[clientes["nome"] == cliente_nome]["id"].values[0]
        modelo = st.text_input("Modelo")
        ano = st.number_input("Ano", min_value=1900, max_value=2100, step=1)
        cor = st.text_input("Cor")
        status = st.selectbox("Status", ["Em revisão", "Pronto", "Aguardando peças"])
        submit = st.form_submit_button("Salvar Carro")

        if submit and modelo:
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute("""INSERT INTO carros (cliente_id, modelo, ano, cor, status)
                                VALUES (?, ?, ?, ?, ?)""", (cliente_id, modelo, ano, cor, status))
                conn.commit()
                st.success("Carro salvo com sucesso!")

    carros = pd.read_sql("""SELECT carros.id, clientes.nome AS cliente, modelo, ano, cor, status
                            FROM carros JOIN clientes ON carros.cliente_id = clientes.id""",
                         sqlite3.connect(DB_PATH))
    st.dataframe(carros, use_container_width=True)

# Exibir e editar orçamentos
def pagina_orcamentos():
    st.subheader("Cadastro de Orçamentos")

    carros = pd.read_sql("SELECT * FROM carros", sqlite3.connect(DB_PATH))
    if carros.empty:
        st.warning("Cadastre um carro antes de adicionar orçamentos.")
        return

    with st.form("form_orcamento"):
        modelo_carro = st.selectbox("Modelo do Carro", carros["modelo"])
        carro_id = carros[carros["modelo"] == modelo_carro]["id"].values[0]
        servico = st.text_input("Serviço Realizado")
        preco_estimado = st.number_input("Preço Estimado", min_value=0.0)
        preco_final = st.number_input("Preço Final", min_value=0.0)
        submit = st.form_submit_button("Salvar Orçamento")

        if submit and servico:
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute("""INSERT INTO orcamentos (carro_id, servico, preco_estimado, preco_final)
                                VALUES (?, ?, ?, ?)""", (carro_id, servico, preco_estimado, preco_final))
                conn.commit()
                st.success("Orçamento salvo com sucesso!")

    orcamentos = pd.read_sql("""SELECT orcamentos.id, modelo, servico, preco_estimado, preco_final
                                FROM orcamentos
                                JOIN carros ON orcamentos.carro_id = carros.id""",
                             sqlite3.connect(DB_PATH))
    st.dataframe(orcamentos, use_container_width=True)

# Página inicial
def pagina_inicio():
    st.title("Dashboard da Oficina 🚗")
    st.write("Bem-vindo! Acompanhe clientes, carros e orçamentos em um só lugar.")

    if st_lottie:
        anim = carregar_lottie("https://assets9.lottiefiles.com/packages/lf20_tutvdkg0.json")
        if anim:
            st_lottie(anim, height=300)
        else:
            st.error("Erro ao carregar animação Lottie")
    else:
        st.info("Para ver animações, instale com: `pip install streamlit-lottie`")

# Status da oficina
def pagina_status():
    st.subheader("Status da Oficina")
    carros = pd.read_sql("SELECT * FROM carros", sqlite3.connect(DB_PATH))

    em_revisao = len(carros[carros["status"] == "Em revisão"])
    prontos = len(carros[carros["status"] == "Pronto"])
    aguardando = len(carros[carros["status"] == "Aguardando peças"])

    st.metric("Em Revisão", em_revisao)
    st.metric("Prontos para Entrega", prontos)
    st.metric("Aguardando Peças", aguardando)

    st.dataframe(carros, use_container_width=True)

# Função principal
def main():
    criar_tabelas()

    st.sidebar.title("Menu")
    opcoes = ["Início", "Clientes", "Carros", "Orçamentos", "Status da Oficina"]
    escolha = st.sidebar.radio("Escolha uma página", opcoes)

    if escolha == "Início":
        pagina_inicio()
    elif escolha == "Clientes":
        pagina_clientes()
    elif escolha == "Carros":
        pagina_carros()
    elif escolha == "Orçamentos":
        pagina_orcamentos()
    elif escolha == "Status da Oficina":
        pagina_status()

if __name__ == "__main__":
    main()
