import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import os
import plotly.graph_objects as go

# Função para exibir a imagem corretamente
def exibir_imagem():
    imagem_path = "B:/CBT-BKADM/GABRIEL/Gabriel Arquivos ADM/VSCODE/PROJETO COBATA/Arquivos/WhatsApp_Image_2024-11-28_at_10.47.28-removebg-preview.png"
    if os.path.exists(imagem_path):
        st.image(imagem_path, caption="", width=200, use_container_width=False)
    else:
        st.error("Imagem não encontrada!")

@st.cache_data
# Função para obter dados do endpoint
def get_data_from_api(url):
    response = requests.get(url)
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        st.error("Erro ao buscar dados da API")
        return pd.DataFrame()

def calcular_faturamento(data, hoje, ontem, semana_inicial):
    data['FATURAMENTO'] = data['QT'] * data['PVENDA']
    
    # Faturamento de hoje e ontem
    faturamento_hoje = data[data['DATA'] == hoje]['FATURAMENTO'].sum()
    faturamento_ontem = data[data['DATA'] == ontem]['FATURAMENTO'].sum()
    
    # Faturamento semanal
    faturamento_semanal = data[(data['DATA'] >= semana_inicial) & (data['DATA'] <= hoje)]['FATURAMENTO'].sum()
    
    return faturamento_hoje, faturamento_ontem, faturamento_semanal

def calcular_comparativos(data, hoje, mes_atual, ano_atual):
    # Obter o mês e o ano atuais
    mes_anterior = mes_atual - 1 if mes_atual > 1 else 12
    ano_anterior = ano_atual if mes_atual > 1 else ano_atual - 1
    
    # Faturamento mês atual e mês anterior
    faturamento_mes_atual = data[(data['DATA'].dt.month == mes_atual) & (data['DATA'].dt.year == ano_atual)]['FATURAMENTO'].sum()
    faturamento_mes_anterior = data[(data['DATA'].dt.month == mes_anterior) & (data['DATA'].dt.year == ano_anterior)]['FATURAMENTO'].sum()
    
    # Ticket médio mês atual e mês anterior
    ticket_medio_mes_atual = faturamento_mes_atual / data[(data['DATA'].dt.month == mes_atual) & (data['DATA'].dt.year == ano_atual)]['CODPROD'].nunique() if faturamento_mes_atual > 0 else 0
    ticket_medio_mes_anterior = faturamento_mes_anterior / data[(data['DATA'].dt.month == mes_anterior) & (data['DATA'].dt.year == ano_anterior)]['CODPROD'].nunique() if faturamento_mes_anterior > 0 else 0
    
    # Pedidos mês atual e mês anterior
    pedidos_mes_atual = data[(data['DATA'].dt.month == mes_atual) & (data['DATA'].dt.year == ano_atual)]['CODPROD'].nunique()
    pedidos_mes_anterior = data[(data['DATA'].dt.month == mes_anterior) & (data['DATA'].dt.year == ano_anterior)]['CODPROD'].nunique()
    
    return faturamento_mes_atual, faturamento_mes_anterior, ticket_medio_mes_atual, ticket_medio_mes_anterior, pedidos_mes_atual, pedidos_mes_anterior



def calcular_faturamento_por_vendedor (data):

    data['FATURAMENTO'] = data['QT'] * data['PVENDA']



    top_vendedores = data.groupby('VENDEDOR')











def main():
    exibir_imagem()

    # URL do seu endpoint
    url = "http://127.0.0.1:5000/dados?data_inicial=2023-01-01&data_final=2024-12-31&pagina=1&limite=500000"  # Substitua pela URL do seu endpoint

    # Carregar dados
    data = get_data_from_api(url)

    # Certifique-se de que a coluna 'DATA' é do tipo datetime
    if not data.empty:
        data['DATA'] = pd.to_datetime(data['DATA'])

        # Obter a data de hoje, ontem e a data do início da semana
        hoje = pd.to_datetime('today').normalize()
        ontem = hoje - timedelta(days=1)
        semana_inicial = hoje - timedelta(days=hoje.weekday())  # Início da semana (segunda-feira)

        # Calcular o faturamento
        faturamento_hoje, faturamento_ontem, faturamento_semanal = calcular_faturamento(data, hoje, ontem, semana_inicial)

        # Obter o mês e o ano atuais
        mes_atual = hoje.month
        ano_atual = hoje.year

        # Calcular comparativos
        faturamento_mes_atual, faturamento_mes_anterior, ticket_medio_mes_atual, ticket_medio_mes_anterior, pedidos_mes_atual, pedidos_mes_anterior = calcular_comparativos(data, hoje, mes_atual, ano_atual)

        # Exibição no Dashboard
        st.title('📊 Dashboard de Faturamento')
        st.markdown("### Resumo de Vendas")

        # Layout em colunas com cards mais interativos e modernos
        col1, col2 = st.columns(2)

        with col1:
            # Faturamento de Ontem
            st.markdown(f"""
                <div style="display:grid; justify-content: start; font-weight: bold; padding: 35px; background-color:#FF6347; color:white; border-radius: 15px; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1); font-size: 35px; margin-bottom: 10px; transition: all 0.3s ease;">
                     <span style="font-size: 21px; font-weight: normal;">📉 Faturamento Ontem:</span> \n R$ {faturamento_ontem:,.2f}
                </div>
               <div style="display:grid; justify-content: start; font-weight: bold; padding: 35px; background-color:#FF4500; color:white; border-radius: 15px; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1); font-size: 35px; margin-bottom: 10px; transition: all 0.3s ease;">
                     <span style="font-size: 21px; font-weight: normal;">📅 Faturamento Semanal:</span> \n R$ {faturamento_semanal:,.2f}
                </div>
                <div style="display:grid; justify-content: start; font-weight: bold; padding: 35px; background-color:#32CD32; color:white; border-radius: 15px; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1); font-size: 35px; margin-bottom: 10px; transition: all 0.3s ease;">
                     <span style="font-size: 21px; font-weight: normal;">📦 Pedidos Mês Passado:</span> \n {pedidos_mes_anterior}
                </div>
            """, unsafe_allow_html=True)

        with col2:
            # Faturamento de Hoje
            st.markdown(f"""
                <div style="display:grid; justify-content: start; font-weight: bold; padding: 35px; background-color:#007bff; color:white; border-radius: 15px; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1); font-size: 35px; margin-bottom: 10px; transition: all 0.3s ease;">
                     <span style="font-size: 21px; font-weight: normal;">💰 Faturamento Hoje:</span> \n  R$ {faturamento_hoje:,.2f}
                </div>
                <div style="display:grid; justify-content: start; font-weight: bold; padding: 35px; background-color:#FFD700; color:white; border-radius: 15px; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1); font-size: 35px; margin-bottom: 10px; transition: all 0.3s ease;">
                     <span style="font-size: 21px; font-weight: normal;">📈 Faturamento Mês Atual:</span> \n R$ {faturamento_mes_atual:,.2f}
                </div>
                <div style="display:grid; justify-content: start; font-weight: bold; padding: 35px; background-color:#8A2BE2; color:white; border-radius: 15px; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1); font-size: 35px; margin-bottom: 10px; transition: all 0.3s ease;">
                     <span style="font-size: 21px; font-weight: normal;">💳 Ticket Médio Mês Atual:</span> \n R$ {ticket_medio_mes_atual:,.2f}
                </div>
            """, unsafe_allow_html=True)

        # Gráfico interativo com Plotly para visualização detalhada
        st.markdown("### 📈 Gráfico de Faturamento")
        fig = go.Figure()

        # Gráfico de Faturamento com Plotly
        data_grouped = data.groupby('DATA')['FATURAMENTO'].sum().reset_index()
        fig.add_trace(go.Scatter(x=data_grouped['DATA'], y=data_grouped['FATURAMENTO'], mode='lines+markers', line=dict(color='#007bff', width=3), marker=dict(size=8, color='red')))

        fig.update_layout(
            title='Faturamento ao Longo do Tempo',
            xaxis_title='Data',
            yaxis_title='Faturamento (R$)',
            template='plotly_dark',
            plot_bgcolor='rgb(0,0,0)',
            paper_bgcolor='rgb(0,0,0)',
            font=dict(color='white'),
            autosize=True,
            hovermode='closest'
        )
        st.plotly_chart(fig)

if __name__ == "__main__":
    main()
