import pandas as pd
import requests
import matplotlib.pyplot as plt
import streamlit as st


def dadosDeputados():
        url = f'https://dadosabertos.camara.leg.br/api/v2/deputados?ordem=ASC&ordenarPor=nome' 
        r = requests.get(url)               
        info_deputados = pd.DataFrame(r.json()['dados'])
        info_deputados.set_index('nome', inplace=True)
        return info_deputados

class DespesasDeputados:
        def __init__(self,id:int, ano:int):
                self.id = id
                self.ano = ano

        def get_links(self):
                self.links = []
                self.url = f'https://dadosabertos.camara.leg.br/api/v2/deputados/{self.id}/despesas?ano={self.ano}&itens=100&ordem=ASC&ordenarPor=ano'
                self.resp1 = requests.get(self.url)
                self.links.append(self.resp1.json()['links'])
                return self.links

        def get_pages(self):
                self.final_links = []
                self.first_page = self.links[0][2]['href']
                self.last_page = self.links[0][3]['href']
                for i in range(int(self.first_page[-11]), int(self.last_page[-11])+1):
                        link = f'https://dadosabertos.camara.leg.br/api/v2/deputados/{self.id}/despesas?ano={self.ano}&ordem=ASC&ordenarPor=ano&pagina={i}&itens=100'
                        self.final_links.append(link)
                return self.final_links

        def create_dataframes(self):
                self.df_dataframes = []        
                for page in self.final_links:
                        self.resp = requests.get(page)
                        self.info_despesas = pd.DataFrame(self.resp.json()['dados'])
                        self.info_despesas.set_index('dataDocumento', inplace=True)
                        self.info_despesas.sort_index(inplace=True)
                        self.df_dataframes.append(self.info_despesas)
                self.df_final = pd.concat(self.df_dataframes[0:len(self.df_dataframes)])
                return self.df_final

def detalhesDeputados(id):
    url = f'https://dadosabertos.camara.leg.br/api/v2/deputados/{id}'
    r = requests.get(url)               
    det_deputados = r.json()['dados']
    return det_deputados


deputados = dadosDeputados()
nome_deputados = deputados.index
dados_dict = deputados.to_dict('index')

st.title('Gastos com cota parlamentar')

nome_deputado = st.sidebar.selectbox('Deputados', nome_deputados)

ano = st.sidebar.radio('Escolha um ano', 
                        (2022, 2021, 2020, 2019),
                        horizontal=True)

col1, col2 = st.columns([1,3])
if nome_deputado in dados_dict.keys():
    with col1:
        st.image(dados_dict[nome_deputado]['urlFoto'])
    with col2:
        st.write('Deputado', nome_deputado)
        st.write('Partido', dados_dict[nome_deputado]['siglaPartido'])
        st.write('ID', dados_dict[nome_deputado]['id'])
        st.write('UF', dados_dict[nome_deputado]['siglaUf']) 
        st.write(dados_dict[nome_deputado]['email'])


dados = DespesasDeputados(dados_dict[nome_deputado]['id'], ano)
links = dados.get_links()
pages = dados.get_pages()
gasto_deputado = dados.create_dataframes()

st.write('Total gasto em {} R$ {:.2f}'.format(ano, gasto_deputado['valorLiquido'].sum()))
with st.expander('informações detalhadas'):
    st.write(gasto_deputado[['tipoDespesa', 'nomeFornecedor', 'valorLiquido', 'urlDocumento']])

with st.expander('Totais por mês'):    
    total_mes = gasto_deputado.groupby(gasto_deputado['mes'])['valorLiquido'].sum()
    st.write(total_mes)

with st.expander('Totais por Categoria'):    
    total_categoria = gasto_deputado.groupby(gasto_deputado['tipoDespesa'])['valorLiquido'].sum()
    st.write(total_categoria.sort_values(ascending=False))

with st.expander('Totais por Fornecedor'):    
    total_fornecedor= gasto_deputado.groupby(gasto_deputado['nomeFornecedor'])['valorLiquido'].sum()
    st.write(total_fornecedor.sort_values(ascending=False))

def barPlot():
    color=['black', 'red', 'green', 'blue', 'cyan', 'white', 'gray', 'pink', 'brown', 'purple', 'darksalmon', 'gold', 'violet', 'navy']
    fig = plt.figure(figsize=(14,8))
    total_categoria.plot(kind='bar', color=color)
    st.pyplot(fig)

with st.expander('Grafico'):
    barPlot()


detalhe_deputado = detalhesDeputados(dados_dict[nome_deputado]['id'])

list_compare = [0,1]
r_social = detalhe_deputado['redeSocial']

st.sidebar.title('Redes sociais')
for redes in r_social:
    st.sidebar.write(redes)

st.sidebar.title('Escolaridade')
st.sidebar.write(detalhe_deputado['escolaridade'])
