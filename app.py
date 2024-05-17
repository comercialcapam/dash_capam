#Carregar bibliotecas


import streamlit as st 
import altair as alt
import pandas as pd
import matplotlib.pyplot as plt 
import numpy as np
import plotly.express as px 
import plotly.graph_objects as go 
from streamlit_extras.switch_page_button import switch_page 
from st_pages import Page, Section, show_pages, add_page_title, hide_pages


#LAYOUT DASBOARD
st.set_page_config(layout="wide")

def main_page():
    st.title("Olá, comercial CAPAM!")
    col1, col2 = st.columns([2,2])
    col1.markdown("## **💡 Sobre o Dashoard**")
    col1.markdown("Esse dashboard tem o objetivo de blá blá blá")
    col1.markdown("## **🗃️ Dados**")
    col1.markdown("Os dados são das pasta X, Y e Z. Caso você não saiba atualizar, **clique aqui**")

    col2.markdown("## **📊 Visualização**")
    col2.markdown("Para visualizar em tela cheia ou sair da tela cheia aperte a tecla F11 em seu teclado")

    st.sidebar.markdown("")

#LAYOUT CLIENTES =====================================

def clientes():
    st.title('Clientes - Visão Geral')
    col1, col2 = st.columns([2,2])

    #GRAFICO
    df_economias = pd.read_parquet('dados/economias.parquet')
    # FILTRO
    tarifa_selecionada = col1.selectbox('Selecione a Tarifa', df_economias['Tarifa'].unique())

    
    # Filtrar DataFrame de acordo com a tarifa selecionada
    df_filtrado = df_economias[df_economias['Tarifa'] == tarifa_selecionada]

    # CONSUMO
    df_consumo = pd.read_parquet('dados/consumo.parquet')
    categoria_selecionada = col2.selectbox('Selecione a Categoria', df_consumo['categoria'].unique())

    df_consumo_filtrado = df_consumo[df_consumo['categoria'] == categoria_selecionada]


    #LINHA 2 - METRICS 
    # Agrupe por tarifa e data de faturamento, somando as quantidades de economias
    df_soma_economias = df_filtrado.groupby(['Tarifa', 'Dt. Faturamento'])['Qtde. Economias'].sum().reset_index()   

        # Obter o último mês disponível nos dados
    ultimo_mes = df_filtrado['Dt. Faturamento'].max().to_period('M')

    # Obter o mês anterior
    mes_anterior = ultimo_mes - 1

    # Filtrar DataFrame para o mês anterior
    df_mes_anterior = df_filtrado[df_filtrado['Dt. Faturamento'].dt.to_period('M') == mes_anterior]

    # Calcular a quantidade total de economias para o mês anterior
    qtde_economias_mes_anterior = df_mes_anterior['Qtde. Economias'].sum()

    # Filtrar DataFrame para o mês atual
    df_mes_atual = df_filtrado[df_filtrado['Dt. Faturamento'].dt.to_period('M') == ultimo_mes]

    # Calcular a quantidade total de economias para o mês atual
    qtde_economias_mes_atual = df_mes_atual['Qtde. Economias'].sum()

    # Calcular a diferença percentual entre os valores do mês atual e do mês anterior
    if qtde_economias_mes_anterior != 0:
        delta_percentual = ((qtde_economias_mes_atual - qtde_economias_mes_anterior) / qtde_economias_mes_anterior) * 100
    else:
        delta_percentual = 0
 
     # Exibir o total de economias do mês passado
    cols = st.columns(4)
    #with cols[0]:
    
    

    with cols[0]:
      st.metric(label ='N° de Economias', value=f'{qtde_economias_mes_atual:.2f}', delta=f'{delta_percentual:.2f}% em relação ao mês anterior')

    #CONSUMO
     # Filtrar DataFrame para o mês anterior
    df_mes_anterior = df_consumo_filtrado[df_consumo_filtrado['data'].dt.to_period('M') == mes_anterior]

    # Calcular o último mês disponível nos dados
    ultimo_mes = df_consumo_filtrado['data'].max().to_period('M')

    # Filtrar DataFrame para o último mês
    df_ultimo_mes = df_consumo_filtrado[df_consumo_filtrado['data'].dt.to_period('M') == ultimo_mes]

    # Calcular o consumo faturado do mês anterior e atual
    consumo_mes_anterior = df_mes_anterior['voluma fat agua'].sum()
    consumo_mes_atual = df_ultimo_mes['voluma fat agua'].sum()

    # Calcular a porcentagem de mudança entre os consumos do mês atual e do mês anterior
    if consumo_mes_anterior != 0:
        delta_percentual_consumo = ((consumo_mes_atual - consumo_mes_anterior) / consumo_mes_anterior) * 100
    else:
        delta_percentual_consumo = 0

    # Calcular o consumo faturado do mês anterior e atual esgoto
    consumo_mes_anterior_esgoto = df_mes_anterior['volume fat esgoto'].sum()
    consumo_mes_atual_esgoto = df_ultimo_mes['volume fat esgoto'].sum()

    # Calcular a porcentagem de mudança entre os consumos do mês atual e do mês anterior
    if consumo_mes_anterior_esgoto != 0:
        delta_percentual_consumo_esgoto = ((consumo_mes_atual_esgoto - consumo_mes_anterior_esgoto) / consumo_mes_anterior_esgoto) * 100
    else:
        delta_percentual_consumo_esgoto = 0
    
    # Exibir as métricas colocar em decimal separado por virgula
    with cols[2]:
        st.metric(label='Consumo Faturado Água', value=f'R$ {consumo_mes_atual:,.2f}'.replace(",", "|").replace(".", ",").replace("|", "."), delta=f'{delta_percentual_consumo:.2f}% em relação ao mês anterior')

    #Exibir as métriacas esgoto colocar em decimal separado por virgula
    with cols[3]:
        st.metric(label='Consumo Faturado Esgoto', value=f'R$ {consumo_mes_atual_esgoto:,.2f}'.replace(",", "|").replace(".", ",").replace("|", "."), delta=f'{delta_percentual_consumo_esgoto:.2f}% em relação ao mês anterior')


    #GRÁFICOS LINHA 3
    col1, col2, col3 = st.columns([4,1,4])
    graph_economia = px.line(df_soma_economias, x='Dt. Faturamento', y='Qtde. Economias', color='Tarifa', markers=True,
                         labels={'Dt. Faturamento': 'Data de Faturamento', 'Qtde. Economias': 'Soma de Economias', 'Tarifa': 'Tarifa'},
                         title='Economias x Data de Faturamento')
    col1.plotly_chart(graph_economia,theme="streamlit", use_container_width=True)

    #consumo por categoria
    df_consumo_filtrado['data'] = pd.to_datetime(df_consumo_filtrado['data'])
    df_consumo_filtrado['MES'] = df_consumo_filtrado['data'].dt.month
    df_consumo_filtrado['ANO'] = df_consumo_filtrado['data'].dt.year

    # Agrupar por categoria e data, somando os valores totais
    consumo_categoria = df_consumo_filtrado.groupby(['categoria', 'data'])[['voluma fat agua', 'volume fat esgoto']].sum().reset_index()

    # Melting das colunas 'voluma fat agua' e 'voluma fat esgoto' em uma única coluna 'value'
    consumo_categoria_melted = pd.melt(consumo_categoria, id_vars=['categoria', 'data'], value_vars=['voluma fat agua', 'volume fat esgoto'], var_name='tipo_consumo', value_name='consumo')

    # Criar gráfico de linha com duas linhas (água e esgoto)
    fig = px.line(consumo_categoria_melted, x='data', y='consumo', color='tipo_consumo', markers=True, title='Consumo Faturado - Água e Esgoto', color_discrete_map={'voluma fat agua': 'blue', 'volume fat esgoto': 'green'})
    fig.update_layout(xaxis_title='Data', yaxis_title='Consumo Faturado', legend_title='Tipo de Consumo')
    col3.plotly_chart(fig, theme="streamlit", use_container_width=True)

    ################

    ##### PÁGINA ARRECADAÇÕES E SUBPÁGINA DE DESCONTOS


def faturamento():

    #load data principal
    df_contas = pd.read_parquet('dados/contas_receber.parquet')

    #TÍTULO
    st.title('Faturamentos 💰')


    #LINHA 1    
   
    #CÓDIGO
    # Carrega o DataFrame
    df_recebidos = pd.read_parquet('dados/contas_recebidas.parquet')

    # Define a data mínima como o primeiro dia do mês mínimo do DataFrame
    min_data = df_recebidos['DT. PAGAMENTO'].min().replace(day=1).date()

        # Define a data máxima como o último dia do mês máximo do DataFrame
    max_date = df_recebidos['DT. PAGAMENTO'].max()
    max_data = max_date.replace(day=max_date.days_in_month).date()

        # Converte todas as datas do DataFrame para objetos datetime.date
    df_recebidos['DT. PAGAMENTO'] = pd.to_datetime(df_recebidos['DT. PAGAMENTO']).dt.date

    #LINHA 2
    cols = st.columns(4)

    with cols[0]:
        data_inicio = st.date_input("Selecione a data inicial", min_value=min_data, max_value=max_data, value=min_data, format="DD/MM/YYYY")

    with cols[1]:
        data_fim = st.date_input("Selecione a data final", min_value=min_data, max_value=max_data, value=max_data, format="DD/MM/YYYY")

    with cols[2]:
    #Seleção de cateogoria para valores a receber
        categoria_selecionada = st.selectbox(label= 'Selecione uma categoria:', options= df_contas['CATEGORIA'].unique())
    
    #CÓDIGO
        # Filtra os dados pelo intervalo de datas selecionado
        df_recebidos_filtrado = df_recebidos[(df_recebidos['DT. PAGAMENTO'] >= data_inicio) & 
                                            (df_recebidos['DT. PAGAMENTO'] <= data_fim)]
        # Calcula o total recebido no período selecionado
        valor_recebido_geral = df_recebidos_filtrado['VALOR TOTAL'].sum()

    #LINHA 3 METRICS
    cols = st.columns(4)
    with cols[0]:
        st.metric(label = "Total Recebido -  Geral", value = f"R$ {valor_recebido_geral:,.2f}".replace(",", "|").replace(".", ",").replace("|", "."))
              
    # SEGUNDA LINHA
    df_contas_filtrado = df_contas[df_contas['CATEGORIA'] == categoria_selecionada]
    total_para_receber = df_contas_filtrado['VALOR TOTAL'].sum()
    total_para_receber_geral = df_contas['VALOR TOTAL'].sum()

    with cols[3]:
        card_receber = st.metric(label = 'Total a receber -  ' + categoria_selecionada, value= f'R$ {total_para_receber:,.2f}'.replace(",", "|").replace(".", ",").replace("|", "."))
    with cols[2]:
        card_receber_geral = st.metric(label= 'Total a receber - Geral ', value= f'R$ {total_para_receber_geral:,.2f}'.replace(",", "|").replace(".", ",").replace("|", "."))

    #TOTAL RECEBIDO POR CATEGORIA
        # Filtra os dados pelo intervalo de datas e pela categoria selecionada
    df_recebidos_filtrado = df_recebidos[(df_recebidos['DT. PAGAMENTO'] >= data_inicio) & 
                                        (df_recebidos['DT. PAGAMENTO'] <= data_fim) &
                                        (df_recebidos['CATEGORIA'] == categoria_selecionada)]

    # Calcula o total recebido no período e para a categoria selecionada
    valor_recebido_categoria = df_recebidos_filtrado['VALOR TOTAL'].sum()

    with cols[1]:
    # Exibe o total recebido em um card métrico
        st.metric(label = 'Total a recebido - ' + categoria_selecionada, value= f"R$ {valor_recebido_categoria:,.2f}".replace(",", "|").replace(".", ",").replace("|", "."))

    cols = st.columns(2)

    with cols[0]:
        #FILTRO DO GRAFICO DE LINHAS
        df_soma_recebido = df_recebidos_filtrado.groupby(['CATEGORIA', 'DT. PAGAMENTO'])['VALOR TOTAL'].sum().reset_index() 

        #with cols[0]:
        #LINHA 4 - LINE GRAPH
        graph_recebidos = px.line(df_soma_recebido, x='DT. PAGAMENTO', y='VALOR TOTAL', markers=True,
                         color_discrete_sequence=['#05A942'],
                         labels={'DT. PAGAMENTO': 'Data', 'VALOR TOTAL': '($)', 'CATEGORIA': 'Categoria'},
                         title='Valores Recebidos por Categoria')
        st.plotly_chart(graph_recebidos,theme="streamlit", use_container_width=True)  

    with cols[1]:
        # Ordena o DataFrame pela coluna de data em ordem ascendente (do menos recente para o mais recente)
       # Crie uma nova coluna para representar o ano e o mês como strings
        df_contas_filtrado['Ano-Mês'] = df_contas_filtrado['DT. VENCIMENTO'].dt.to_period('M').astype(str)
        # Agrupe os dados por ano, mês e categoria e calcule a soma dos valores totais para cada grupo
        soma_valores_por_mes = df_contas_filtrado.groupby(['Ano-Mês', 'CATEGORIA'])['VALOR TOTAL'].sum().reset_index()    
        graph_receber = px.line(soma_valores_por_mes,x='Ano-Mês', y='VALOR TOTAL', color='CATEGORIA',markers=True,
                            labels={'Ano-Mês':'Data','VALOR TOTAL':'Valor ($)','CATEGORIA':'Categoria'},
                            title='Valores a receber por Categoria')
        st.plotly_chart(graph_receber, theme='streamlit', use_container_width=True)

#SERVIÇOS E DESCONTOS 

def descontos(): #ADICIONAR MAIS DADOS AOS DESCONTOS
    st.markdown('# Descontos e Serviços 📈')

    # Supondo que df_servicos seja seu DataFrame com os dados
    df_servicos = pd.read_parquet('dados/servicos.parquet')
    # FILTRO
    cols = st.columns(3)
    with cols[0]:
        categoria_selecionada = st.selectbox(label= 'Selecione uma categoria:', options= df_servicos['Categoria Principal'].unique())
        
    
    df_servicos_filtrado = df_servicos[df_servicos['Categoria Principal'] == categoria_selecionada]
   
    
    # Calcula a contagem de cada serviço
    contagem_servicos = df_servicos_filtrado['Agrupador Serviço'].value_counts()

    # Seleciona os 10 serviços mais comuns
    top_10_servicos = contagem_servicos.head(10)

    # Cria um DataFrame com os 10 serviços mais comuns e suas contagens
    df_top_servicos = pd.DataFrame({'Serviço': top_10_servicos.index, 'Contagem': top_10_servicos.values})

    cols = st.columns(3)
    # Mostra a tabela com os serviços mais comuns
    with cols[0]:
        st.markdown('#### Serviços')
        st.dataframe(df_top_servicos,
                    column_order=("Serviço", "Contagem"),
                    hide_index=True,
                    width=None,
                    column_config={
                        "Serviço": st.column_config.TextColumn(
                            "Serviço",
                        ),
                        "Contagem": st.column_config.ProgressColumn(
                            "Contagem",
                            format="%d",
                            min_value=0,
                            max_value=max(df_top_servicos['Contagem']),
                        )}
                    )


#######
page_names_to_funcs = {
    "Sobre o Dashboard": main_page,  
    "Clientes": clientes, 
    "Arrecadações": faturamento,
    "Descontos e Serviços": descontos
}

selected_page = st.sidebar.selectbox("Selecione uma página", page_names_to_funcs.keys())
page_names_to_funcs[selected_page]()



