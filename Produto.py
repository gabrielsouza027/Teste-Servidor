import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import os





# Função para exibir a imagem corretamente
def exibir_imagem():
    imagem_path = "B:\CBT-BKADM\GABRIEL\Gabriel Arquivos ADM\VSCODE\PROJETO COBATA\Arquivos\WhatsApp_Image_2024-11-28_at_10.47.28-removebg-preview.png"
    if os.path.exists(imagem_path):
        st.image(imagem_path, caption="", width=200, use_container_width=False)
    else:
        st.error("Imagem não encontrada!")

# Função para carregar dados com cache (agora vai buscar do endpoint)
@st.cache_data
def carregar_dados():
    url = "http://127.0.0.1:5000/dados?data_inicial=2023-01-01&data_final=2024-12-31&pagina=1&limite=500000"  # Alterar para o seu endpoint real

    params = {
        'data_inicial': '2023-01-01', 
        'data_final': '2024-12-31',    
        'pagina': 1,                   
        'limite': 10000                  
    }

    try:
        response = requests.get(url, params=params)

        if response.status_code == 200:
            df = pd.DataFrame(response.json())  # Convertendo a resposta para um DataFrame
        else:
            st.error(f"Erro ao obter dados: {response.status_code}")
            return pd.DataFrame()

        expected_columns = ['DESCRICAO', 'CODPROD', 'DATA', 'QT', 'PVENDA', 'VLCUSTOFIN']
        missing_columns = [col for col in expected_columns if col not in df.columns]

        if missing_columns:
            st.error(f"As seguintes colunas estão faltando: {', '.join(missing_columns)}")
            return pd.DataFrame()

        df['DESCRICAO'] = df['DESCRICAO'].fillna('').astype(str).str.strip()
        df['Código Produto'] = df['CODPROD'].fillna('').astype(str).str.strip()

        df['Data do Pedido'] = pd.to_datetime(df['DATA'], errors='coerce')

        if df['Data do Pedido'].isnull().any():
            st.warning("Existem valores inválidos ou ausentes na coluna 'DATA' após conversão para datetime.")

        df['Valor Total Vendido'] = df['QT'] * df['PVENDA']
        df['Margem de Lucro'] = (df['PVENDA'] - df['VLCUSTOFIN']) * df['QT']
        df['Ano'] = df['Data do Pedido'].dt.year
        df['Mês'] = df['Data do Pedido'].dt.month
        return df

    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao fazer a requisição: {e}")
        return pd.DataFrame()

# Função para exibir a tabela
def exibir_tabela(df_filtrado):
    df_resumo = df_filtrado.groupby(['DESCRICAO', 'Código Produto']).agg(
        Total_Vendido=('QT', 'sum'),
        Valor_Total_Vendido=('Valor Total Vendido', 'sum')
    ).reset_index()
    df_resumo['Valor_Total_Vendido'] = df_resumo['Valor_Total_Vendido'].apply(lambda x: f"R$ {x:,.2f}")
    df_resumo['Total_Vendido'] = df_resumo['Total_Vendido'].apply(lambda x: f"{x:,.0f}")
    st.dataframe(df_resumo, use_container_width=True)

# Função para exibir gráfico dos top 20 produtos por valor total vendido
def exibir_grafico_top_produtos(df, periodo_inicial, periodo_final):
    # Garantir que as datas de início e fim sejam do tipo datetime
    periodo_inicial = pd.to_datetime(periodo_inicial)
    periodo_final = pd.to_datetime(periodo_final)

    df_mes = df[(df['Data do Pedido'] >= periodo_inicial) & (df['Data do Pedido'] <= periodo_final)]
    
    top_produtos = df_mes.groupby('DESCRICAO').agg(
        Total_Vendido=('QT', 'sum'),
        Valor_Total_Vendido=('Valor Total Vendido', 'sum')
    ).reset_index()

    top_produtos = top_produtos.sort_values(by='Valor_Total_Vendido', ascending=False).head(20)
    
    top_produtos['Valor_Total_Vendido'] = top_produtos['Valor_Total_Vendido'].apply(lambda x: f"R$ {x:,.2f}")
    top_produtos['Total_Vendido'] = top_produtos['Total_Vendido'].apply(lambda x: f"{x:,.0f}")

    fig = px.bar(top_produtos, x='DESCRICAO', y='Valor_Total_Vendido',
                 title=f'Top 20 Produtos Mais Vendidos',
                 labels={'DESCRICAO': 'Produto', 'Valor_Total_Vendido': 'Valor Total Vendido (R$)'},
                 color='Valor_Total_Vendido', color_continuous_scale='RdYlGn',
                 hover_data={'DESCRICAO': False, 'Valor_Total_Vendido': True, 'Total_Vendido': True})

    fig.update_traces(texttemplate="%{y}", textposition="outside", insidetextfont_size=12)
    fig.update_layout(title_font_size=20, xaxis_title_font_size=16, yaxis_title_font_size=16,
                      xaxis_tickfont_size=14, yaxis_tickfont_size=14, xaxis_tickangle=-45)

    st.plotly_chart(fig, key=f"top_produtos_{periodo_inicial}_{periodo_final}")

# Função para exibir gráfico de vendas ao longo do tempo (por mês)
def exibir_grafico_vendas_por_tempo(df, periodo_inicial, periodo_final):
    # Garantir que as datas de início e fim sejam do tipo datetime
    periodo_inicial = pd.to_datetime(periodo_inicial)
    periodo_final = pd.to_datetime(periodo_final)

    df_periodo = df[(df['Data do Pedido'] >= periodo_inicial) & (df['Data do Pedido'] <= periodo_final)]

    # Agrupar os dados por ano, mês
    vendas_por_mes = df_periodo.groupby(['Ano', 'Mês']).agg(
        Total_Vendido=('QT', 'sum'),
        Valor_Total_Vendido=('Valor Total Vendido', 'sum')
    ).reset_index()

    # Criando o gráfico de linhas com uma linha por ano
    fig = px.line(vendas_por_mes, x='Mês', y='Valor_Total_Vendido', color='Ano',
                  title=f'Evolução das Vendas ao Longo do Período',
                  labels={'Mês': 'Mês', 'Valor_Total_Vendido': 'Valor Total Vendido (R$)', 'Ano': 'Ano'},
                  markers=True)

    # Ajustes visuais
    fig.update_layout(
        title_font_size=20,
        xaxis_title_font_size=16,
        yaxis_title_font_size=16,
        xaxis_tickfont_size=14,
        yaxis_tickfont_size=14,
        xaxis_tickangle=-45
    )

    # Mostrar o gráfico
    st.plotly_chart(fig, key=f"vendas_por_tempo_{periodo_inicial}_{periodo_final}")

# Função para exibir gráfico de margem de lucro por produto
def exibir_grafico_margem_por_produto(df, periodo_inicial, periodo_final):
    # Garantir que as datas de início e fim sejam do tipo datetime
    periodo_inicial = pd.to_datetime(periodo_inicial)
    periodo_final = pd.to_datetime(periodo_final)

    df_periodo = df[(df['Data do Pedido'] >= periodo_inicial) & (df['Data do Pedido'] <= periodo_final)]
    
    df_margem = df_periodo.groupby('DESCRICAO').agg(
        Margem_Lucro=('Margem de Lucro', 'sum')
    ).reset_index()

    df_margem = df_margem.sort_values(by='Margem_Lucro', ascending=False).head(20)

    fig = px.bar(df_margem, x='DESCRICAO', y='Margem_Lucro',
                 title=f'Top 20 Produtos por Margem de Lucro',
                 labels={'DESCRICAO': 'Produto', 'Margem_Lucro': 'Margem de Lucro (R$)'},
                 color='Margem_Lucro', color_continuous_scale='Viridis')

    fig.update_traces(texttemplate="%{y}", textposition="outside", insidetextfont_size=12)
    fig.update_layout(title_font_size=20, xaxis_title_font_size=16, yaxis_title_font_size=16,
                      xaxis_tickfont_size=14, yaxis_tickfont_size=14, xaxis_tickangle=-45)

    st.plotly_chart(fig, key="margem_por_produto")

# Função principal
def main():
    st.title("Desempenho de Vendas por Produto")

    exibir_imagem()

    df = carregar_dados()

    if df.empty:
        return

    st.markdown("""<style> .stTextInput>div>div>input { border: 2px solid #4CAF50; border-radius: 10px; padding: 10px; font-size: 16px; background-color: black; } </style>""", unsafe_allow_html=True)
    produto_pesquisa = st.text_input('🔍 Pesquise por um produto ou código', '', key='search_input')

    # Filtro de período para a Tabela
    if 'Data do Pedido' in df.columns:
        with st.container():
            st.subheader("Tabela de Resumo")
            periodo_inicio_tabela = st.date_input('Data de Início - Tabela', df['Data do Pedido'].min())
            periodo_fim_tabela = st.date_input('Data de Fim - Tabela', df['Data do Pedido'].max())
        
        df_filtrado = df[(df['Data do Pedido'] >= pd.to_datetime(periodo_inicio_tabela)) & 
                         (df['Data do Pedido'] <= pd.to_datetime(periodo_fim_tabela))]

        if produto_pesquisa:
            produto_pesquisa = ' '.join(produto_pesquisa.split())
            df_filtrado['DESCRICAO'] = df_filtrado['DESCRICAO'].apply(lambda x: ' '.join(str(x).split()))
            df_filtrado['Código Produto'] = df_filtrado['Código Produto'].apply(lambda x: ' '.join(str(x).split()))
            df_filtrado = df_filtrado[
                df_filtrado['DESCRICAO'].str.contains(produto_pesquisa, case=False) |
                df_filtrado['Código Produto'].str.contains(produto_pesquisa, case=False)
            ]

        exibir_tabela(df_filtrado)

    # Gráfico de Top Produtos
    with st.container():
        st.subheader("Top Produtos Mais Vendidos por Valor")
        periodo_inicio_produtos = st.date_input('Data de Início - Top Produtos', df['Data do Pedido'].min())
        periodo_fim_produtos = st.date_input('Data de Fim - Top Produtos', df['Data do Pedido'].max())
        exibir_grafico_top_produtos(df, periodo_inicio_produtos, periodo_fim_produtos)

    # Gráfico de Vendas ao Longo do Tempo
    with st.container():
        st.subheader("Evolução das Vendas")
        periodo_inicio_vendas = st.date_input('Data de Início - Vendas ao Longo do Tempo', df['Data do Pedido'].min())
        periodo_fim_vendas = st.date_input('Data de Fim - Vendas ao Longo do Tempo', df['Data do Pedido'].max())
        exibir_grafico_vendas_por_tempo(df, periodo_inicio_vendas, periodo_fim_vendas)

    # Gráfico de Margem de Lucro por Produto
    with st.container():
        st.subheader("Margem de Lucro por Produto")
        periodo_inicio_margem = st.date_input('Data de Início - Margem de Lucro', df['Data do Pedido'].min())
        periodo_fim_margem = st.date_input('Data de Fim - Margem de Lucro', df['Data do Pedido'].max())
        exibir_grafico_margem_por_produto(df, periodo_inicio_margem, periodo_fim_margem)

if __name__ == "__main__":
    main()
