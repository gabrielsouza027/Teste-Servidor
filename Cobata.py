import streamlit as st
import json
import os
import importlib

st.set_page_config(layout="wide", initial_sidebar_state="auto")

# Caminho do arquivo JSON para armazenar os dados de login
USER_DATA_FILE = "users.json"

# Lista de páginas disponíveis
PAGES = {
    "Página Inicial": "Página_Inicial",
    "Produto": "Produto",
    "Fornecedor": "Fornecedor",
    "Estoque": "Estoque",
    "Validade": "Validade"
}

# Função para carregar dados de usuários do arquivo JSON
def load_users():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as f:
            return json.load(f)
    return {}

# Função para salvar os dados de usuários no arquivo JSON
def save_users(users):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(users, f, indent=4)

# Função para exibir a barra de navegação estilizada na barra lateral
def navigation_bar(selected_page):
    st.markdown(
        """
        <style>
        /* Barra lateral */
        .sidebar .sidebar-content {
            background: #f4f6f8;
            padding: 1rem 0;
            width: 250px; /* Largura fixa da barra lateral */
            border-right: 1px solid #d1d8de;
        }

        /* Estilos de Botões */
        .sidebar .sidebar-content .nav-button {
            display: block;
            width: 100%; /* Largura total do botão */
            margin: 8px 0;
            padding: 12px;
            font-size: 1rem;
            color: #ffffff;
            background: linear-gradient(135deg, #0072ff, #00c6ff);
            border: none;
            border-radius: 12px; /* Borda arredondada */
            text-align: center;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.15);
            transition: all 0.3s ease-in-out;
        }

        /* Hover nos botões */
        .sidebar .sidebar-content .nav-button:hover {
            background: linear-gradient(135deg, #0056b3, #0078c9);
            box-shadow: 0px 6px 12px rgba(0, 0, 0, 0.25);
            transform: scale(1.05);
        }

        /* Botão ativo */
        .sidebar .sidebar-content .nav-button.active {
            background: linear-gradient(135deg, #003d66, #0066cc);
            box-shadow: 0px 6px 12px rgba(0, 0, 0, 0.35);
            transform: scale(1.1);
            border: 2px solid #fff; /* Borda branca no botão ativo */
        }

        /* Responsividade: Para telas menores */
        @media (max-width: 768px) {
            .sidebar .sidebar-content {
                width: 200px; /* Ajuste para largura da barra lateral em telas pequenas */
            }

            .sidebar .sidebar-content .nav-button {
                font-size: 0.9rem;
                padding: 10px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.title("")  # Título vazio para não ocupar espaço extra
    for page in PAGES.keys():
        button_class = "nav-button active" if page == selected_page else "nav-button"
        # Aqui, usamos ícones ou apenas o texto como nome da página
        if st.sidebar.button(page, key=page):
            st.session_state.page = page

# Função para exibir o formulário de login
def login_page():
   
    # Exibir imagem no topo da página de login
    st.image("B:\CBT-BKADM\GABRIEL\Gabriel Arquivos ADM\VSCODE\PROJETO COBATA\Arquivos\WhatsApp_Image_2024-11-28_at_10.47.28-removebg-preview.png", width=200)  # Coloque o caminho correto da sua imagem

    st.title("Login", )
    
    # Campos de login
    username = st.text_input("Nome de usuário")
    password = st.text_input("Senha", type="password")

    # Carregar dados dos usuários
    users_db = load_users()

    # Colunas para os botões lado a lado
    col1, col2 = st.columns([1, 1])  # Dividir a tela em duas colunas

    # Validação do login
    with col1:
        if st.button("Entrar"):
            if username in users_db and users_db[username]["password"] == password:
                # Login bem-sucedido, configurando estado da sessão
                st.session_state.logged_in = True
                st.session_state.page = "Página Inicial"  # Define a página inicial 
                st.success(f"Bem-vindo, {username}!")
            else:
                st.error("Usuário ou senha inválidos. Tente novamente.")

    with col2:
        if st.button("Registrar-se"):
            st.session_state.page = "Register"

# Função para exibir o formulário de registro de um novo usuário
def register_page():
    st.title("Página de Registro")

    # Campos para registrar um novo usuário
    username = st.text_input("Escolha um nome de usuário")
    password = st.text_input("Escolha uma senha", type="password")
    name = st.text_input("Nome completo")

    # Carregar dados dos usuários
    users_db = load_users()

    # Validação do formulário de registro
    if st.button("Criar conta"):
        if username and password and name:
            if username not in users_db:
                # Adiciona o novo usuário ao banco de dados
                users_db[username] = {"password": password, "name": name}
                save_users(users_db)  # Salva no arquivo JSON
                st.session_state.page = "Login"
                st.success("Conta criada com sucesso! Faça login para acessar.")
            else:
                st.warning("Nome de usuário já existe. Tente outro.")
        else:
            st.warning("Preencha todos os campos.")

    if st.button("Voltar para Login"):
        st.session_state.page = "Login"

# Função para carregar e exibir a página selecionada
def load_page(page_name):
    module_name = PAGES.get(page_name)
    if module_name:
        try:
            page_module = importlib.import_module(module_name)
            page_module.main()  # Presume que cada página tem uma função `main()`
        except ModuleNotFoundError:
            st.error(f"Módulo '{module_name}' não encontrado.")
        except AttributeError:
            st.error(f"O módulo '{module_name}' não possui uma função 'main()'.")

# Função principal que gerencia o fluxo da aplicação
def main():
    # Verifica se a sessão de login existe
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if 'page' not in st.session_state:
        st.session_state.page = "Login"  # Inicia com a página de login

    # Controle de navegação
    if st.session_state.logged_in:
        # Renderiza a barra de navegação estilizada
        navigation_bar(st.session_state.page)
        load_page(st.session_state.page)
    else:
        # Exibe a página de login ou registro
        if st.session_state.page == "Login":
            login_page()
        elif st.session_state.page == "Register":
            register_page()

if __name__ == "__main__":
    main()




