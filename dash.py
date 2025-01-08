#%%
import streamlit as st
import yfinance as yf
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import numpy as np

#%% Login




#%%
tickers = pd.read_csv('TICKERS.csv',delimiter=';')
tickers_options = tickers['TICKERS'].values
tickers_dict = tickers.set_index("TICKERS")["YF"].to_dict()


#%%
st.title('Dashboard Seanonal - VLAD')
st.text('Dashboard de dados sazonais do VLAD')
st.divider()
#st.set_page_config(layout="wide")

# Coleta de Dados
ativo = st.sidebar.selectbox('Escolha o Ativo',options=tickers_options)
ticker_yf = tickers_dict[ativo]


dados = yf.download(ticker_yf,start='1994-12-29')['Close']
anos = dados.index.year.unique()
anos = anos[1:]
anos_eleito = np.arange(1998,anos[-1]+1,4)
anos_pos = np.arange(1995,anos[-1]+1,4)
anos_meio = np.arange(1996,anos[-1]+1,4)
anos_pre = np.arange(1997,anos[-1]+1,4)
anos_dec = np.arange(1995,anos[-1]+1,10)


ciclos = {
    "Total":anos,
    "Anos Eleitorais": anos_eleito,
    "Anos Pós-Eleitorais": anos_pos,
    "Anos de Meio de Mandato": anos_meio,
    "Anos Pré-Eleitorais": anos_pre,
    "Anos de Década": anos_dec
}


ciclo_set = st.sidebar.selectbox(
    "Selecione o Ciclo:",
    options=list(ciclos.keys())
)
anos_disp = ciclos[ciclo_set]

dados = dados.rename(columns={ticker_yf:ativo})
dados = dados.pct_change().dropna()
first_day = dados.index[0].strftime('%d/%m/%Y')
last_day = dados.index[-1].strftime('%d/%m/%Y')
dados = dados[dados.index.year.isin(anos_disp)]
anos_disp = dados.index.year.unique()
anos_disp = anos_disp[1:]


# Tratamento de dados
data_saz = dados.copy()
dados_day_week = dados.copy()
dados_day_week['day'] = dados_day_week.index.dayofweek
dados_day_week['year'] = dados_day_week.index.strftime('%Y')
dados_month = dados.resample('M').last()
dados_month['month'] = dados_month.index.strftime('%m')
dados_month['year'] = dados_month.index.strftime('%Y')



ano_destaq = st.sidebar.selectbox('Escolha o ano para Destacar',options=anos_disp)

data_saz = data_saz.groupby(data_saz.index.year).apply(lambda x: x.values.flatten()).apply(pd.Series).T
data_saz_destaq = pd.DataFrame(data_saz[ano_destaq]).rename(columns={ano_destaq:ativo})
dados_day_week = dados_day_week.pivot_table(values=ativo, columns='year', index='day')
dados_saz_day_week_destaq = pd.DataFrame(dados_day_week[f'{ano_destaq}']*100).rename(columns={f'{ano_destaq}':ativo})

#Dados Mensais
dados_month = dados_month.pivot_table(values=ativo, columns='year', index='month')
dados_month_destaq = pd.DataFrame(dados_month[f'{ano_destaq}']*100).rename(columns={f'{ano_destaq}':ativo})



#Calculo total
data_saz_destaq = data_saz_destaq.add(1).cumprod().sub(1)*100
data_saz = pd.DataFrame(data_saz.mean(axis=1)).rename(columns={0:ativo})
data_saz = data_saz.add(1).cumprod().sub(1)*100

media_dados = data_saz.mean()


#Calculo dia da semana
dados_day_week = pd.DataFrame(dados_day_week.mean(axis=1)*100)
dados_day_week = dados_day_week.rename(columns={0:ativo})

#Calculo Mensal
dados_month = pd.DataFrame(dados_month.mean(axis=1)*100)
dados_month = dados_month.rename(columns={0:ativo})



# Grafico Sazonalidade
st.header(f'Sazonalidade {ativo}  - {ciclo_set}')

fig_sazon = go.Figure()
fig_sazon.add_trace(go.Line(
    x=data_saz.index,
    y=data_saz[ativo],
    name='Ciclo',
    line=dict(color='blue'),
))
fig_sazon.add_trace(go.Line(
    x=data_saz_destaq.index,
    y=data_saz_destaq[ativo],
    name=ano_destaq,
    line=dict(color='red'),
))

fig_sazon.update_layout(xaxis_title='Trading day', yaxis=dict(title='Retorno %'),
                  title=f'Ciclo', margin=dict(l=40, r=40, t=40, b=40) ) 



# Grafico dia da semana
fig_day_week = go.Figure()
fig_day_week.add_trace(go.Bar(
    x=dados_day_week.index,
    y=dados_day_week[ativo],
    marker_color='blue',
    name='Ciclo'
))
fig_day_week.add_trace(go.Bar(
    x=dados_saz_day_week_destaq.index,
    y=dados_saz_day_week_destaq[ativo],
    marker_color='red',
    name = ano_destaq
))


fig_day_week.update_layout(xaxis_title='Dia da Semana', yaxis_title='Retorno %', 
                  title=f'Dias da Semana', margin=dict(l=40, r=40, t=40, b=40) ) 

#Grafico Mensal
fig_month = go.Figure()
fig_month.add_trace(go.Bar(
    x=dados_month.index,
    y=dados_month[ativo],
    marker_color='blue',
    name='Ciclo'
))
fig_month.add_trace(go.Bar(
    x=dados_month_destaq.index,
    y=dados_month_destaq[ativo],
    marker_color='red',
    name = ano_destaq
))

fig_month.update_layout(xaxis_title='Retornos Mensais', yaxis_title='Retorno %', 
                  title=f'Mês', margin=dict(l=40, r=40, t=40, b=40) ) 

st.text(f'Range dos dados disponíveis  \n {first_day} - {last_day}' )

st.plotly_chart(fig_sazon, use_container_width=True)
col1, col2 = st.columns(2)
with col1:
    with st.container():
        st.plotly_chart(fig_day_week)
with col2:
    with st.container():
        st.plotly_chart(fig_month)



# with col2:
    # st.plotly_chart(fig_other, use_container_width=True)
# st.plotly_chart(fig_day_week)

#%% 





