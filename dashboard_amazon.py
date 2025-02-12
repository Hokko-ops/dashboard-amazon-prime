import streamlit as st
import pandas as pd
import plotly.express as px
from io import StringIO

# Configuração da Página
st.set_page_config(page_title="Dashboard de Clientes Amazon Prime", layout="wide")

# CSS customizado para um visual moderno e acessível
st.markdown(
    """
    <style>
    .main {background-color: #F8F9FA; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;}
    .sidebar .sidebar-content {background-image: linear-gradient(#2c3e50, #3498db); color: white; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;}
    h1, h2, h3, h4 {color: #2c3e50;}
    .metric {font-size: 1.5em; font-weight: bold;}
    </style>
    """,
    unsafe_allow_html=True,
)

# Função para carregar e preparar os dados
@st.cache_data
def load_data():
    data = pd.read_csv("amazon_prime_users_clean.csv")
    # Converter data de nascimento
    data['Date of Birth'] = pd.to_datetime(data['Date of Birth'], format='%d/%m/%Y', errors='coerce')
    data['Age'] = pd.to_datetime('today').year - data['Date of Birth'].dt.year
    return data

data = load_data()

# Sidebar: Filtros interativos
st.sidebar.header("Filtros de Análise")
subscription_options = data["Subscription Plan"].unique().tolist()
selected_subscription = st.sidebar.multiselect("Plano de Assinatura", subscription_options, default=subscription_options)

gender_options = data["Gender"].unique().tolist()
selected_gender = st.sidebar.multiselect("Gênero", gender_options, default=gender_options)

engagement_options = data["Engagement Metrics"].unique().tolist()
selected_engagement = st.sidebar.multiselect("Nível de Engajamento", engagement_options, default=engagement_options)

min_age, max_age = int(data['Age'].min()), int(data['Age'].max())
age_range = st.sidebar.slider("Faixa Etária", min_age, max_age, (min_age, max_age))

filtered_data = data[
    (data["Subscription Plan"].isin(selected_subscription)) & 
    (data["Gender"].isin(selected_gender)) & 
    (data["Engagement Metrics"].isin(selected_engagement)) & 
    (data["Age"] >= age_range[0]) & (data["Age"] <= age_range[1])
]

# Cabeçalho e KPIs
st.title("Dashboard de Análise de Clientes Amazon Prime")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total de Clientes", len(filtered_data))
with col2:
    st.metric("Idade Média", f"{filtered_data['Age'].mean():.0f} anos")
with col3:
    st.metric("Feedback Médio", f"{filtered_data['Feedback/Ratings'].mean():.1f}")
with col4:
    st.metric("Média de Suporte", f"{filtered_data['Customer Support Interactions'].mean():.1f}")

st.markdown("---")

# Gráficos: Sequência lógica para storytelling visual

# Distribuição de Planos de Assinatura
plan_fig = px.pie(
    filtered_data,
    names="Subscription Plan",
    title="Distribuição dos Planos de Assinatura",
    color_discrete_sequence=px.colors.sequential.RdBu
)
st.plotly_chart(plan_fig, use_container_width=True)

# Status de Renovação
renewal_counts = filtered_data["Renewal Status"].value_counts().reset_index()
renewal_counts.columns = ["Status de Renovação", "Quantidade"]
renewal_fig = px.bar(
    renewal_counts,
    x="Status de Renovação",
    y="Quantidade",
    title="Status de Renovação",
    color="Status de Renovação",
    template="plotly_white",
    text="Quantidade"
)
renewal_fig.update_traces(texttemplate='%{text}', textposition='outside')
renewal_fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
st.plotly_chart(renewal_fig, use_container_width=True)

# Distribuição de Idade (Histograma)
age_fig = px.histogram(
    filtered_data,
    x="Age",
    nbins=20,
    title="Distribuição de Idade dos Clientes",
    labels={"Age": "Idade"},
    color_discrete_sequence=["#3498db"]
)
st.plotly_chart(age_fig, use_container_width=True)

# Feedback vs. Interações com Suporte
feedback_fig = px.scatter(
    filtered_data,
    x="Feedback/Ratings",
    y="Customer Support Interactions",
    title="Feedback vs. Interações com Suporte",
    trendline="ols",  # Requer statsmodels
    color="Engagement Metrics",
    labels={"Feedback/Ratings": "Feedback", "Customer Support Interactions": "Interações com Suporte"},
    template="simple_white"
)
st.plotly_chart(feedback_fig, use_container_width=True)

# Gêneros Favoritos
favorite_genres = filtered_data["Favorite Genres"].value_counts().head(10)
genres_fig = px.bar(
    x=favorite_genres.index,
    y=favorite_genres.values,
    title="Top 10 Gêneros Favoritos",
    labels={'x': 'Gênero', 'y': 'Contagem'},
    color_discrete_sequence=["#e74c3c"]
)
st.plotly_chart(genres_fig, use_container_width=True)

# Botão para download dos dados filtrados
@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

csv = convert_df(filtered_data)
st.download_button(
    label="Download dos Dados Filtrados",
    data=csv,
    file_name='dados_filtrados.csv',
    mime='text/csv',
)

# Tabela interativa dos dados filtrados
st.subheader("Tabela de Clientes Filtrados")
st.dataframe(filtered_data)

