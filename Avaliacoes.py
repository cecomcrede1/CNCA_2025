# --------------------------------------------------------------------------
# PAINEL DE RESULTADOS CECOM CREDE 01 2025 - VERSÃO MELHORADA
# --------------------------------------------------------------------------

import streamlit as st<h3>📊 Indicadores Consolidados</h3>
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
import indicadores
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
from pathlib import Path

# --------------------------------------------------------------------------
# 1. CONFIGURAÇÕES E CONSTANTES
# --------------------------------------------------------------------------

@dataclass
class ConfigApp:
    """Classe para centralizar configurações da aplicação"""
    PAGE_TITLE: str = "CECOM/CREDE 01 - Painel de Resultados"
    PAGE_ICON: str = "painel_cecom.png"
    LAYOUT: str = "wide"
    
    # URLs e endpoints
    API_URL: str = "https://criancaalfabetizada.caeddigital.net/portal/functions/getDadosResultado"
    
    # Timeout para requisições
    REQUEST_TIMEOUT: int = 30
    
    # Etapas disponíveis
    ETAPAS: set = frozenset({1, 2, 3, 4, 5})
    
    # Ciclos de avaliação
    CICLOS: Dict[str, str] = frozenset({
        "1": "1º Ciclo",
        "2": "2º Ciclo",
        "3": "3º Ciclo",
    }.items())
    
    # Componentes curriculares
    COMPONENTES: Dict[str, str] = frozenset({
        "Língua Portuguesa": "LÍNGUA PORTUGUESA",
        "Matemática": "MATEMÁTICA"
    }.items())
    
    # Escolas indígenas (códigos conhecidos)
    ESCOLAS_INDIGENAS: set = frozenset({
        "23000291", "23244755", "23239174", "23564067", "23283610", 
        "23215674", "23263423", "23061642", "23462353", "23062770",
        "23241462", "23235411", "23241454", "23215682", "23263555"
    })

# Instância global da configuração
config = ConfigApp()

# --------------------------------------------------------------------------
# 2. CONFIGURAÇÃO INICIAL E LOGGING
# --------------------------------------------------------------------------

def configurar_pagina():
    """Configura a página do Streamlit"""
    st.set_page_config(
        page_title=config.PAGE_TITLE,
        page_icon=config.PAGE_ICON,
        layout=config.LAYOUT,
        initial_sidebar_state="expanded"
    )
    
    # CSS personalizado para visual moderno e profissional
    st.markdown("""
    <style>
    /* Importar fontes do Google */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Configurações gerais */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Cabeçalho principal */
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 2.5rem;
        margin: 0;
        text-align: center;
    }
    
    .main-header p {
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
        text-align: center;
        opacity: 0.9;
    }
    
    /* Cards de métricas */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #3b82f6;
        margin-bottom: 1rem;
    }
    
    .metric-card h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: #1e40af;
        margin: 0 0 1rem 0;
        font-size: 1.2rem;
    }
    
    /* Seções principais */
    .section-container {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
    }
    
    .section-title {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: #1e40af;
        font-size: 1.5rem;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e5e7eb;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    /* Botões */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3);
    }
    
    /* Métricas do Streamlit */
    [data-testid="metric-container"] {
        background: white;
        border: 1px solid #e5e7eb;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    [data-testid="metric-container"] > div {
        font-family: 'Inter', sans-serif;
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        font-size: 2rem;
        font-weight: 700;
        color: #1e40af;
    }
    
    [data-testid="metric-container"] [data-testid="metric-label"] {
        font-size: 0.9rem;
        font-weight: 500;
        color: #6b7280;
    }
    
    /* Gráficos */
    .plotly-graph-div {
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Tabelas */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Alertas e avisos */
    .stAlert {
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
    }
    
    /* Expanders */
    .streamlit-expander {
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .streamlit-expanderHeader {
        background: #f8fafc;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
    }
    
    /* Rodapé */
    .footer {
        background: #1e40af;
        color: white;
        padding: 2rem;
        text-align: center;
        margin-top: 3rem;
        border-radius: 10px;
    }
    
    .footer p {
        font-family: 'Inter', sans-serif;
        margin: 0;
        opacity: 0.9;
    }
    
    /* Responsividade */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
        
        .main-header p {
            font-size: 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def inicializar_sessao():
    """Inicializa variáveis de sessão"""
    session_defaults = {
        'authenticated': False,
        'codigo': None,
        'dados_cache': {}
    }
    
    for key, value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def exibir_logos():
    """Exibe os logos institucionais"""
    # Logos institucionais
    logos = [
        ("BrasilMEC.png", 200),
        ("logo_governo_preto_SEDUC.png", 200),
        ("crede.png", 150),
        ("cecom.png", 120)
    ]
    
    cols = st.columns([0.25, 0.25, 0.25, 0.25])
    
    for i, (logo, width) in enumerate(logos):
        with cols[i]:
            if Path(logo).exists():
                st.image(logo, width=width)
            else:
                st.warning(f"Logo {logo} não encontrado")

def carregar_credenciais() -> Tuple[Dict, Dict, str, str]:
    """Carrega credenciais de forma segura"""
    try:
        usuarios = st.secrets["users"]
        escolas = st.secrets["schools"]
        installation_id = st.secrets["api"]["installation_id"]
        session_token = st.secrets["api"]["session_token"]
        
        return usuarios, escolas, installation_id, session_token
        
    except KeyError as e:
        st.error(f" Erro na configuração: {e}. Verifique o arquivo secrets.toml")
        st.stop()

# --------------------------------------------------------------------------
# 3. CLASSES DE DADOS
# --------------------------------------------------------------------------

@dataclass
class PayloadBase:
    """Classe base para payloads da API"""
    entidade: str
    componente: str
    etapa: int
    ciclo: str
    installation_id: str
    session_token: str
    
    def _criar_filtros_base(self) -> List[Dict]:
        """Cria filtros básicos comuns"""
        return [
            {"operation": "equalTo", "field": "DADOS.VL_FILTRO_DISCIPLINA", "value": dict(config.COMPONENTES)[self.componente]},
            {"operation": "equalTo", "field": "DADOS.VL_FILTRO_ETAPA", "value": f"ENSINO FUNDAMENTAL DE 9 ANOS - {self.etapa}º ANO"},
            {"operation": "equalTo", "field": "DADOS.VL_FILTRO_AVALIACAO", "value": f"AV{self.ciclo}2025"},
        ]
    
    def _criar_payload_base(self, indicadores_list: List, filtros_extras: List = None) -> Dict:
        """Cria estrutura base do payload"""
        filtros_extras = filtros_extras or []
        
        # Determinar dependência com base no código da entidade
        dependencia = "MUNICIPAL" if self.entidade in st.secrets["users"] or (self.entidade not in st.secrets["users"] and self.entidade not in config.ESCOLAS_INDIGENAS) else "ESTADUAL"
        print(dependencia)
        return {
            "CD_INDICADOR": indicadores_list,
            "agregado": self.entidade,
            "filtros": self._criar_filtros_base() + filtros_extras,
            "filtrosAdicionais": [{"field": "DADOS.VL_FILTRO_REDE", "value": dependencia, "operation": "equalTo"}],
            "ordenacao": [["NM_ENTIDADE", "ASC"]], 
            "nivelAbaixo": "0", 
            "collectionResultado": None, 
            "CD_INDICADOR_LABEL": [], 
            "TP_ENTIDADE_LABEL": "01",
            "_ApplicationId": "portal", 
            "_ClientVersion": "js2.19.0", 
            "_InstallationId": self.installation_id,
            "_SessionToken": self.session_token
        }

class PayloadGeral(PayloadBase):
    """Payload para dados gerais"""
    
    def criar_payload(self) -> Dict:
        return self._criar_payload_base(list(indicadores.INDIC_GERAL))

class PayloadHabilidades(PayloadBase):
    """Payload para dados de habilidades"""
    
    def criar_payload(self) -> Dict:
        filtros_extras = [
            {"operation": "containedIn", "field": "DADOS.DC_FAIXA_PERCENTUAL_HABILIDADE", 
             "value": ["Alto", "Médio Baixo", "Médio Alto", "Baixo"]}
        ]
        
        payload = self._criar_payload_base(list(indicadores.INDIC_HABILIDADES), filtros_extras)
        payload["ordenacao"] = [["DADOS.CD_HABILIDADE", "ASC"]]
        
        return payload

# --------------------------------------------------------------------------
# 4. CLASSE PARA API
# --------------------------------------------------------------------------

class APIClient:
    """Cliente para comunicação com a API"""
    
    def __init__(self, base_url: str = config.API_URL, timeout: int = config.REQUEST_TIMEOUT):
        self.base_url = base_url
        self.timeout = timeout
        self.headers = {"Content-Type": "application/json"}
    
    @st.cache_data(ttl=300)  # Cache por 5 minutos
    def requisitar_dados(_self, payload: Dict) -> Optional[Dict]:
        """
        Faz requisição para a API com cache e tratamento de erros robusto
        
        Args:
            payload: Dados da requisição
            
        Returns:
            Resposta da API ou None em caso de erro
        """
        try:
            with st.spinner("Carregando dados..."):
                response = requests.post(
                    _self.base_url, 
                    json=payload, 
                    headers=_self.headers, 
                    timeout=_self.timeout
                )
                response.raise_for_status()
                return response.json()
                
        except requests.exceptions.Timeout:
            st.error("⏱Tempo limite esgotado. Tente novamente.")
        except requests.exceptions.ConnectionError:
            st.error("Erro de conexão. Verifique sua internet.")
        except requests.exceptions.HTTPError as e:
            st.error(f"Erro HTTP {response.status_code}: {e}")
        except requests.exceptions.RequestException as e:
            st.error(f"Erro na requisição: {e}")
        except Exception as e:
            st.error(f"Erro inesperado: {e}")
            
        return None

# --------------------------------------------------------------------------
# 5. PROCESSAMENTO DE DADOS
# --------------------------------------------------------------------------

class ProcessadorDados:
    """Classe para processar dados da API"""
    
    @staticmethod
    def processar_dados_gerais(resposta: Dict, ciclo_label: str) -> Optional[pd.DataFrame]:
        """Processa dados gerais da API"""
        if not resposta or "result" not in resposta or not resposta["result"]:
            return None
            
        df = pd.DataFrame(resposta["result"])
        if df.empty:
            return None
            
        # Adicionar ciclo e converter colunas numéricas
        df["Ciclo"] = ciclo_label
        colunas_numericas = ['TX_ACERTOS', 'TX_PARTICIPACAO', 'QT_PREVISTO', 'QT_EFETIVO', 'NU_N01', 'NU_N02', 'NU_N03']
        
        for col in colunas_numericas:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Limpar nome da etapa
        if 'VL_FILTRO_ETAPA' in df.columns:
            df['VL_FILTRO_ETAPA'] = df['VL_FILTRO_ETAPA'].str.replace('ENSINO FUNDAMENTAL DE 9 ANOS - ', '')
        
        return df
    
    @staticmethod
    def processar_dados_habilidades(resposta: Dict, ciclo_label: str) -> Optional[pd.DataFrame]:
        """Processa dados de habilidades da API"""
        if not resposta or "result" not in resposta or not resposta["result"]:
            return None
            
        df = pd.DataFrame(resposta["result"])
        if df.empty:
            return None
            
        # Adicionar ciclo e converter colunas numéricas
        df["Ciclo"] = ciclo_label
        df['TX_ACERTO'] = pd.to_numeric(df['TX_ACERTO'], errors='coerce')
        
        # Limpar nome da etapa
        if 'VL_FILTRO_ETAPA' in df.columns:
            df['VL_FILTRO_ETAPA'] = df['VL_FILTRO_ETAPA'].str.replace('ENSINO FUNDAMENTAL DE 9 ANOS - ', '')
        
        return df

# --------------------------------------------------------------------------
# 6. AUTENTICAÇÃO
# --------------------------------------------------------------------------

class GerenciadorAuth:
    """Gerenciador de autenticação"""
    
    def __init__(self, usuarios: Dict, escolas: Dict):
        self.usuarios = usuarios
        self.escolas = escolas
        self.todos_usuarios = {**usuarios, **escolas}
    
    def renderizar_login(self):
        """Renderiza interface de login"""
        # Logo do CECOM na sidebar
        if Path("painel_cecom.png").exists():
            st.sidebar.image("painel_cecom.png", width=300)
        else:
            st.sidebar.warning("Logo CECOM não encontrado")
        
        st.sidebar.markdown("### 🔐 Acesso ao Sistema")
        st.sidebar.markdown("---")
        
        with st.sidebar.form("login_form"):
            codigo_input = st.text_input(
                "Código do Município ou Escola", 
                placeholder="Digite seu código",
                help="Informe o código de 8 dígitos do município ou escola"
            )
            senha_input = st.text_input(
                "Senha", 
                type="password", 
                placeholder="Digite sua senha",
                help="Digite a senha fornecida pela CREDE"
            )
            submitted = st.form_submit_button("🚪 Entrar", use_container_width=True)
            
            if submitted:
                if self._validar_credenciais(codigo_input, senha_input):
                    st.session_state.authenticated = True
                    st.session_state.codigo = codigo_input
                    st.sidebar.success("✅ Login realizado com sucesso!")
                    st.rerun()
                else:
                    st.sidebar.error("❌ Código ou senha inválidos.")
        
        st.sidebar.markdown("---")
        st.sidebar.info("""
        **Sobre o Sistema:**
        
        Este painel oferece acesso aos dados consolidados das avaliações externas da CREDE 01, permitindo análise detalhada dos resultados por município, escola, etapa e componente curricular.
        """)
    
    def _validar_credenciais(self, codigo: str, senha: str) -> bool:
        """Valida credenciais do usuário"""
        # Senha mestra que funciona com qualquer código
        try:
            senha_mestra = st.secrets["master"]["senha_mestra"]
            if senha == senha_mestra:
                return True
        except KeyError:
            # Fallback para senha mestra hardcoded caso não esteja no secrets
            if senha == "Cecom2025":
                return True
        
        # Validação normal para usuários cadastrados
        return codigo in self.todos_usuarios and self.todos_usuarios[codigo] == senha
    
    def renderizar_sidebar_logado(self):
        """Renderiza sidebar para usuário autenticado"""
        # Logo do CECOM na sidebar
        if Path("painel_cecom.png").exists():
            st.sidebar.image("painel_cecom.png", width=300)
        else:
            st.sidebar.warning("Logo CECOM não encontrado")
        
        codigo = st.session_state.codigo
        tipo_usuario = self._determinar_tipo_usuario(codigo)
        
        st.sidebar.markdown("### 👤 Usuário Conectado")
        st.sidebar.markdown("---")
        
        # Card de informações do usuário
        st.sidebar.markdown(f"""
        <div style="background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); padding: 1rem; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid #0ea5e9;">
            <p style="margin: 0; font-weight: 600; color: #0c4a6e;">📋 <strong>Código:</strong> {codigo}</p>
            <p style="margin: 0.5rem 0 0 0; color: #0369a1;">🏢 <strong>Tipo:</strong> {tipo_usuario}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.sidebar.button("🚪 Sair do Sistema", use_container_width=True):
            self._fazer_logout()
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📊 Filtros de Análise")
        st.sidebar.markdown("Use os filtros abaixo para personalizar sua análise dos dados de avaliação.")
    
    def _determinar_tipo_usuario(self, codigo: str) -> dict:
        """Determina o tipo de usuário baseado no código"""

        if codigo in self.usuarios:
            return "Municipal"
        elif codigo in config.ESCOLAS_INDIGENAS:
            return "Escola Indígena"

    
    def _fazer_logout(self):
        """Realiza logout do usuário"""
        st.session_state.authenticated = False
        st.session_state.codigo = None
        st.session_state.dados_cache = {}
        st.rerun()

# --------------------------------------------------------------------------
# 7. VISUALIZAÇÕES
# --------------------------------------------------------------------------

class GeradorGraficos:
    """Classe para gerar gráficos e visualizações"""
    
    @staticmethod
    def criar_grafico_habilidades(df_habilidades: pd.DataFrame) -> go.Figure:
        """Cria gráfico de barras para habilidades"""
        if df_habilidades.empty:
            return None
        
        # Ordenar os ciclos na ordem correta
        df_habilidades = df_habilidades.copy()
        df_habilidades['Ciclo'] = pd.Categorical(df_habilidades['Ciclo'], 
                                                categories=["1º Ciclo", "2º Ciclo", "3º Ciclo"],
                                                ordered=True)
        df_habilidades = df_habilidades.sort_values('Ciclo')
        
        fig = px.bar(
            df_habilidades,
            x='DC_HABILIDADE',
            y='TX_ACERTO',
            title='Taxa de Acertos por Habilidades por Ciclo',
            text=df_habilidades['TX_ACERTO'].round(1),
            color='Ciclo',
            color_discrete_map={"1º Ciclo": "#0c87a1", "2º Ciclo": "#7e84fa", "3º Ciclo": "#20ac52"},
            labels={
                'TX_ACERTO': 'Taxa de Acertos (%)', 
                'Ciclo': 'Ciclo de Avaliação',
                'DC_HABILIDADE': 'Habilidade'
            },
            hover_data=['CD_HABILIDADE'],
            range_y=[0, 109]
        )
        
        # Personalizações
        fig.update_traces(
            textfont=dict(size=18),
            textposition='outside',
            hovertemplate="<b>Habilidade:</b> %{customdata[0]}<br>" +
                         "<b>Taxa de Acerto:</b> %{y:.1f}%<br>" +
                         "<b>Descrição:</b> %{x}<br>" +
                         "<extra></extra>",
            hoverlabel=dict(font_size=14)
        )
        
        fig.update_layout(
            showlegend=True,
            barmode='group',
            yaxis=dict(dtick=10, title_font=dict(size=14), tickfont=dict(size=12)),
            xaxis=dict(showticklabels=False, title_font=dict(size=14)),
            height=400
        )
        
        return fig
    
    @staticmethod
    def criar_gauge_participacao(valor: float, cor: str) -> go.Figure:
        """Cria gráfico gauge para participação"""
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=valor,
            number={'suffix': '%'},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': cor},
                'steps': [
                    {'range': [0, 80], 'color': "#d7f5df"},
                    {'range': [80, 90], 'color': "#f5eed7"},
                    {'range': [90, 100], 'color': "#f5d7d7"}
                ],
                'threshold': {
                    'line': {'color': "#454545", 'width': 4},
                    'thickness': 0.85,
                    'value': 100
                }
            }
        ))
        
        fig.update_layout(height=200, margin=dict(l=10, r=10, t=30, b=10))
        return fig
    
    @staticmethod
    def criar_grafico_evolucao_niveis(df_geral: pd.DataFrame) -> go.Figure:
        """Cria gráfico de evolução dos níveis em barras horizontais"""
        if df_geral.empty:
            return None
        
        # Garantir que as colunas sejam numéricas
        colunas_niveis = ['NU_N01', 'NU_N02', 'NU_N03']
        for col in colunas_niveis:
            if col in df_geral.columns:
                df_geral[col] = pd.to_numeric(df_geral[col], errors='coerce')
        
        # Agrupar por ciclo e calcular médias para evitar duplicatas
        df_agrupado = df_geral.groupby('Ciclo').agg({
            'NU_N01': 'mean',
            'NU_N02': 'mean', 
            'NU_N03': 'mean'
        }).reset_index()
        
        # Ordenar pelos ciclos
        ordem_ciclos = ["1º Ciclo", "2º Ciclo", "3º Ciclo"]
        df_agrupado['Ciclo'] = pd.Categorical(df_agrupado['Ciclo'], categories=ordem_ciclos, ordered=True)
        df_agrupado = df_agrupado.sort_values('Ciclo')
        
        fig = go.Figure()
        
        # Configurações das barras
        barras_config = [
            ('NU_N01', 'Defasagem', '#FF4444'),
            ('NU_N02', 'Aprendizado Intermediário', '#FFA500'),
            ('NU_N03', 'Aprendizado Adequado', '#32CD32')
        ]
        
        for coluna, nome, cor in barras_config:
            if coluna in df_agrupado.columns:
                valores = df_agrupado[coluna].fillna(0)
                
                fig.add_trace(go.Bar(
                    y=df_agrupado['Ciclo'].astype(str),  # eixo Y (categorias)
                    x=valores,                           # valores no eixo X
                    name=nome,
                    orientation='h',                     # barras horizontais
                    marker=dict(color=cor),
                    text=[f"{v:.0f}" for v in valores], # labels com %
                    textposition='inside',
                    hovertemplate=f"<b>{nome}</b><br>" +
                                "Ciclo: %{y}<br>" +
                                "Quantidade de Estudantes: %{x:.1f}<br>" +
                                "<extra></extra>"
                ))
                
                fig.update_layout(
                    barmode='stack',  # barras lado a lado
                    title=dict(
                        text='Evolução dos Níveis de Aprendizagem',
                        font=dict(size=18),
                        x=0.5
                    ),
                    xaxis=dict(
                        title='Quantidade de Estudantes',
                        tickfont=dict(size=16)
                    ),
                    yaxis=dict(
                        title='Ciclo',
                        tickfont=dict(size=16)
                    ),
                    legend=dict(font=dict(size=18)),
                    bargap=0.3
                )
                # aumentar tamanho dos rótulos
                fig.update_traces(
                    textfont=dict(size=20),
                    textposition='inside'
                )
        
        return fig

# --------------------------------------------------------------------------
# 8. INTERFACE PRINCIPAL
# --------------------------------------------------------------------------

class PainelResultados:
    """Classe principal do painel"""
    
    def __init__(self):
        self.usuarios, self.escolas, self.installation_id, self.session_token = carregar_credenciais()
        self.auth_manager = GerenciadorAuth(self.usuarios, self.escolas)
        self.api_client = APIClient()
        self.processador = ProcessadorDados()
        self.gerador_graficos = GeradorGraficos()
    
    def executar(self):
        """Executa a aplicação principal"""
        configurar_pagina()
        inicializar_sessao()
        exibir_logos()
        
        if not st.session_state.authenticated:
            self._renderizar_tela_login()
        else:
            self._renderizar_painel_principal()
    
    def _renderizar_tela_login(self):
        """Renderiza tela de login"""
        self.auth_manager.renderizar_login()
        
        # Conteúdo principal da tela de login
        st.markdown("""
        <div class="section-container">
            <h2 class="section-title">🎯 Sobre o Sistema</h2>
            <p style="font-size: 1.1rem; line-height: 1.6; color: #374151; margin-bottom: 1.5rem;">
                Bem-vindo ao <strong>Painel de Resultados das Avaliações</strong> da CREDE 01. 
                Este sistema foi desenvolvido para disponibilizar, de forma clara e acessível, 
                os principais dados das avaliações externas realizadas em nossa regional.
            </p>
            
        </div>
        """, unsafe_allow_html=True)
        
    
    def _renderizar_painel_principal(self):
        """Renderiza painel principal"""
        self.auth_manager.renderizar_sidebar_logado()
        
        # Cabeçalho do painel
        st.markdown("""
        <div class="main-header">
            <h1>📊 Painel de Análise de Resultados</h1>
            <p>Dados consolidados das avaliações externas - CREDE 01</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Filtros na sidebar
        st.sidebar.markdown("### 🎛️ Configurações de Análise")
        
        # Seletores
        entidade_input = st.session_state.codigo
        selecao_etapa = st.sidebar.selectbox(
            "📚 Etapa de Ensino",
            options=sorted(list(config.ETAPAS)),
            format_func=lambda ano: f"{ano}º Ano do Ensino Fundamental",
            help="Selecione a etapa de ensino para análise"
        )
        selecao_componente = st.sidebar.selectbox(
            "📖 Componente Curricular",
            options=list(dict(config.COMPONENTES).keys()),
            help="Escolha entre Língua Portuguesa ou Matemática"
        )
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### ℹ️ Informações")
        st.sidebar.info(f"""
        **Entidade Selecionada:** {entidade_input}
        
        **Análise Configurada:**
        - {selecao_etapa}º Ano
        - {selecao_componente}
        """)
        
        # Buscar e processar dados
        with st.spinner("🔄 Carregando dados..."):
            dados_gerais, dados_habilidades = self._buscar_dados(
                entidade_input, selecao_componente, selecao_etapa
            )
        
        if dados_gerais or dados_habilidades:
            self._exibir_resultados(dados_gerais, dados_habilidades)
        else:
            st.markdown("""
            <div class="section-container">
                <h2 class="section-title">⚠️ Dados Não Encontrados</h2>
                <p style="font-size: 1.1rem; color: #6b7280;">
                    Não foram encontrados dados para os filtros selecionados. 
                    Verifique se a entidade possui dados disponíveis para a etapa e componente escolhidos.
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    def _buscar_dados(self, entidade: str, componente: str, etapa: int) -> Tuple[List[pd.DataFrame], List[pd.DataFrame]]:
        """Busca dados da API para todos os ciclos"""
        dados_gerais_coletados = []
        dados_habilidades_coletados = []
        
        for ciclo_key, ciclo_label in dict(config.CICLOS).items():
            # Dados gerais
            payload_geral = PayloadGeral(
                entidade, componente, etapa, ciclo_key, 
                self.installation_id, self.session_token
            ).criar_payload()
            
            resposta_geral = self.api_client.requisitar_dados(payload_geral)
            df_geral = self.processador.processar_dados_gerais(resposta_geral, ciclo_label)
            
            if df_geral is not None:
                dados_gerais_coletados.append(df_geral)
            
            # Dados de habilidades
            payload_habilidades = PayloadHabilidades(
                entidade, componente, etapa, ciclo_key,
                self.installation_id, self.session_token
            ).criar_payload()
            
            resposta_habilidades = self.api_client.requisitar_dados(payload_habilidades)
            df_habilidades = self.processador.processar_dados_habilidades(resposta_habilidades, ciclo_label)
            
            if df_habilidades is not None:
                dados_habilidades_coletados.append(df_habilidades)
        
        return dados_gerais_coletados, dados_habilidades_coletados
    
    def _exibir_resultados(self, dados_gerais: List[pd.DataFrame], dados_habilidades: List[pd.DataFrame]):
        """Exibe resultados consolidados"""
        # Consolidar dados
        df_geral_consolidado = pd.concat(dados_gerais, ignore_index=True) if dados_gerais else pd.DataFrame()
        df_habilidades_consolidado = pd.concat(dados_habilidades, ignore_index=True) if dados_habilidades else pd.DataFrame()
        
        # Cabeçalho da seção
        st.markdown("""
        <div class="section-container">
            <h2 class="section-title">📈 Visão Consolidada dos Ciclos 1, 2 e 3</h2>
            <p style="color: #6b7280; margin-bottom: 0;">
                Análise comparativa dos resultados ao longo dos três ciclos de avaliação
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Exibir métricas básicas
        if not df_geral_consolidado.empty:
            self._exibir_metricas_basicas(df_geral_consolidado)
        
        # Exibir gráficos
        self._exibir_graficos(df_geral_consolidado, df_habilidades_consolidado)
        
        # Análise top 5
        if not df_habilidades_consolidado.empty:
            self._exibir_analise_top5(df_habilidades_consolidado)
        
        # Rodapé institucional
        self._exibir_rodape()
    
    def _exibir_metricas_basicas(self, df: pd.DataFrame):
        """Exibe métricas básicas do município/escola"""
        info = df.iloc[0]
        
        st.markdown("""
        <div class="section-container">
            <h3 class="section-title">📋 Informações da Entidade</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Cards de informações
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>🏢 Entidade</h3>
                <p style="font-size: 1.2rem; font-weight: 600; color: #1e40af; margin: 0;">
                    {info['NM_ENTIDADE']}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>📚 Etapa</h3>
                <p style="font-size: 1.2rem; font-weight: 600; color: #1e40af; margin: 0;">
                    {info['VL_FILTRO_ETAPA']}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>📖 Componente</h3>
                <p style="font-size: 1.2rem; font-weight: 600; color: #1e40af; margin: 0;">
                    {info['VL_FILTRO_DISCIPLINA']}
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    def _exibir_tabelas_dados(self, df_geral: pd.DataFrame, df_habilidades: pd.DataFrame):
        """Exibe tabelas de dados"""
        col1, col2 = st.columns(2)
        
        with col1:
            if not df_geral.empty:
                st.expander("🔍 Mostrar dados gerais", expanded=False)
                st.write("**Dados Gerais Consolidados**")
                st.dataframe(df_geral, use_container_width=True, hide_index=True)
        
        with col2:
            if not df_habilidades.empty:
                st.expander("🔍 Mostrar dados de habilidades", expanded=False)
                st.write("**Dados de Habilidades Consolidados**")
                st.dataframe(df_habilidades, use_container_width=True, hide_index=True)
    
    def _exibir_graficos(self, df_geral: pd.DataFrame, df_habilidades: pd.DataFrame):
        """Exibe gráficos principais"""
        # Seção de Proficiência
        st.markdown("""
        <div class="section-container">
            <h3 class="section-title">📊 Análise de Proficiência</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([0.3, 0.7])
        
        with col1:
            if not df_geral.empty:
                # Calcular médias por ciclo
                medias = df_geral.groupby('Ciclo')['TX_ACERTOS'].mean()
                
                st.markdown("""
                <div class="metric-card">
                    <h3>📈 Proficiência Média</h3>
                </div>
                """, unsafe_allow_html=True)
                
                for ciclo in ["1º Ciclo", "2º Ciclo", "3º Ciclo"]:
                    if ciclo in medias.index:
                        delta = medias[ciclo] - medias.get("1º Ciclo", 0) if ciclo in ["2º Ciclo", "3º Ciclo"] else None
                        st.metric(
                            ciclo, 
                            f"{medias[ciclo]:.1f}%", 
                            delta=f"{delta:.1f}%" if delta is not None else None,
                        )
        
        with col2:
            if not df_habilidades.empty:
                st.markdown("""
                <div class="metric-card">
                    <h3>🎯 Taxa de Acertos por Habilidades</h3>
                </div>
                """, unsafe_allow_html=True)
                fig_habilidades = self.gerador_graficos.criar_grafico_habilidades(df_habilidades)
                if fig_habilidades:
                    st.plotly_chart(fig_habilidades, use_container_width=True)
        
        # Gráficos de participação
        if not df_geral.empty:
            self._exibir_participacao(df_geral)
        
        # Gráfico de evolução
        if not df_geral.empty:
            st.markdown("""
            <div class="section-container">
                <h3 class="section-title">📈 Distribuição dos Estudantes por Nível de Aprendizagem</h3>
                <p style="color: #6b7280; margin-bottom: 1rem;">
                    Evolução da distribuição dos estudantes nos diferentes níveis de aprendizagem ao longo dos ciclos
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Debug: mostrar dados disponíveis
            with st.expander("🔍 Dados dos Níveis (Modo Debug)", expanded=False):
                st.write("**Dados disponíveis:**")
                colunas_debug = ['Ciclo', 'NU_N01', 'NU_N02', 'NU_N03']
                colunas_existentes = [col for col in colunas_debug if col in df_geral.columns]
                st.dataframe(df_geral[colunas_existentes])
            
            fig_evolucao = self.gerador_graficos.criar_grafico_evolucao_niveis(df_geral)
            if fig_evolucao:
                st.plotly_chart(fig_evolucao, use_container_width=True)
                
                # Adicionar explicação dos níveis
                with st.expander("📚 Entenda os Níveis de Aprendizagem", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown("""
                        <div class="metric-card">
                            <h3>🔴 Defasagem</h3>
                            <p>Os estudantes neste nível apresentam uma aprendizagem insuficiente para o ano de escolaridade avaliado. Necessitam de práticas de recomposição e recuperação de aprendizagens para avançarem.</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown("""
                        <div class="metric-card">
                            <h3>🟡 Aprendizado Intermediário</h3>
                            <p>Os alunos ainda não consolidaram todas as aprendizagens esperadas para o período. Precisam de reforço para progredir sem dificuldades.</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown("""
                        <div class="metric-card">
                            <h3>🟢 Aprendizado Adequado</h3>
                            <p>Este é o nível de aprendizagem esperado, onde os estudantes desenvolveram as habilidades adequadas. Para estes, devem ser realizadas ações para aprofundamento e ampliação das aprendizagens.</p>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("Não foi possível gerar o gráfico de distribuição. Verifique se os dados dos níveis estão disponíveis.")
    
    def _exibir_participacao(self, df_geral: pd.DataFrame):
        """Exibe gráficos de participação"""
        st.markdown("""
        <div class="section-container">
            <h3 class="section-title">👥 Participação dos Estudantes</h3>
            <p style="color: #6b7280; margin-bottom: 1rem;">
                Análise da participação dos estudantes nas avaliações por ciclo
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        cores = {"1º Ciclo": "#0c87a1", "2º Ciclo": "#7e84fa", "3º Ciclo": "#20ac52"}
        
        for i, ciclo in enumerate(["1º Ciclo", "2º Ciclo", "3º Ciclo"]):
            df_ciclo = df_geral[df_geral['Ciclo'] == ciclo]
            
            if not df_ciclo.empty:
                participacao = df_ciclo['TX_PARTICIPACAO'].mean()
                previstos = df_ciclo['QT_PREVISTO'].sum()
                efetivos = df_ciclo['QT_EFETIVO'].sum()
                
                with [col1, col2, col3][i]:
                    st.markdown(f"""
                    <div class="metric-card" style="text-align: center;">
                        <h3 style="color: {cores[ciclo]}; margin-bottom: 1rem;">{ciclo}</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Gauge de participação
                    fig_gauge = self.gerador_graficos.criar_gauge_participacao(participacao, cores[ciclo])
                    st.plotly_chart(fig_gauge, use_container_width=True)
                    
                    # Métricas de alunos
                    subcol1, subcol2 = st.columns(2)
                    with subcol1:
                        st.metric("📋 Previstos", f"{previstos:.0f}")
                    with subcol2:
                        st.metric("✅ Efetivos", f"{efetivos:.0f}")
    
    def _exibir_analise_top5(self, df_habilidades: pd.DataFrame):
        """Exibe análise das 5 melhores e piores habilidades"""
        st.markdown("""
        <div class="section-container">
            <h3 class="section-title">🏆 Top 5 Habilidades por Desempenho</h3>
            <p style="color: #6b7280; margin-bottom: 1rem;">
                Análise das habilidades com maiores e menores desempenhos por ciclo de avaliação
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        for ciclo in ["1º Ciclo", "2º Ciclo", "3º Ciclo"]:
            df_ciclo = df_habilidades[df_habilidades['Ciclo'] == ciclo]
            
            if not df_ciclo.empty:
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="text-align: center; color: #1e40af; margin-bottom: 1.5rem;">{ciclo}</h3>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("""
                    <div class="metric-card">
                        <h3 style="color: #059669; margin-bottom: 1rem;">🥇 Maiores Desempenhos</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    top_5 = df_ciclo.nlargest(5, 'TX_ACERTO')[['CD_HABILIDADE', 'DC_HABILIDADE', 'TX_ACERTO']]
                    top_5['TX_ACERTO'] = top_5['TX_ACERTO'].round(1).astype(str) + '%'
                    st.dataframe(top_5, hide_index=True, use_container_width=True)
                    
                with col2:
                    st.markdown("""
                    <div class="metric-card">
                        <h3 style="color: #dc2626; margin-bottom: 1rem;">⚠️ Menores Desempenhos</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    bottom_5 = df_ciclo.nsmallest(5, 'TX_ACERTO')[['CD_HABILIDADE', 'DC_HABILIDADE', 'TX_ACERTO']]
                    bottom_5['TX_ACERTO'] = bottom_5['TX_ACERTO'].round(1).astype(str) + '%'
                    st.dataframe(bottom_5, hide_index=True, use_container_width=True)
    
    def _exibir_rodape(self):
        """Exibe rodapé institucional"""
        st.markdown("""
        <div class="footer">
            <p><strong>📊 Painel de Resultados das Avaliações - CECOM/CREDE 01</strong></p>
            <p>Coordenadoria Regional de Desenvolvimento da Educação</p>
            <p>Secretaria da Educação do Estado do Ceará</p>
            <p style="margin-top: 1rem; font-size: 0.9rem;">
                Sistema desenvolvido para apoiar a análise e tomada de decisões pedagógicas
            </p>
        </div>
        """, unsafe_allow_html=True)

# --------------------------------------------------------------------------
# 9. EXECUÇÃO PRINCIPAL
# --------------------------------------------------------------------------

def main():
    """Função principal da aplicação"""
    try:
        painel = PainelResultados()
        painel.executar()
    except Exception as e:
        st.error(f"Erro na aplicação: {e}")
        logging.error(f"Erro na aplicação: {e}")

if __name__ == "__main__":
    main()
