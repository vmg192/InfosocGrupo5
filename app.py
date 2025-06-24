import streamlit as st



#Este código utiliza o Streamlit como a interface gráfica e host do site.

#Em sua essência, cada vez que app é executado uma tela é carregada com o conteúdo desejado de acordo com o estado atual.
#Cada vez que um botão é selecionado, o estado muda e o app é executado novamente.



# Conteúdo das aulas e temas
AULAS_POR_TEMA = {
    "Parte 1": ["1", "2", "3"],
    "Parte 2": ["4", "5", "6"]
}

# Telas

def exibir_tela_1_temas():
    
    st.title("Olá! O que quer aprender hoje?")
    st.info("Clique em um tema para ver as aulas disponíveis.")
    st.markdown("""
    ---
    - Descrição
    - Informações úteis
    ---
    """)
    # Cria um botão para cada tema definido em nosso dicionário
    for nome_tema in AULAS_POR_TEMA.keys():
        if st.button(nome_tema, use_container_width=True):
            st.session_state.tema_selecionado = nome_tema
            st.rerun()

def exibir_tela_2_lista_aulas(tema_escolhido):
    
    st.title(f"Tela 2: Aulas de '{tema_escolhido}'")
    st.info("Info")

    # Pega a lista de aulas para o tema escolhido
    lista_de_aulas = AULAS_POR_TEMA[tema_escolhido]

    # Cria um botão para cada aula na lista
    for nome_aula in lista_de_aulas:
        if st.button(nome_aula, use_container_width=True):
            st.session_state.aula_selecionada = nome_aula
            st.rerun()
    
    st.divider()

    # Botão para voltar à tela anterior
    if st.button("<- Voltar"):
        st.session_state.tema_selecionado = None
        st.rerun()

def exibir_tela_3_aula(nome_da_aula):
    """Desenha a página final da aula selecionada."""
    st.title(f"Tela 3: {nome_da_aula}")
    
    st.success("Esta é a página final da aula!")
    st.markdown("""
    ---
    - Aula
    ---
    """)

     # Base Quiz
    st.subheader("Quiz")
    

    escolha_usuario = st.radio(
        "Pergunta",
        ["a","b","c","d","e"],
        index=None, 
        key="pergunta" 
    )
    
    # Botão para voltar à tela anterior
    if st.button("<- Voltar"):
        st.session_state.aula_selecionada = None
        st.rerun()

# Lógica de navegação

# Inicioaliza o estado da sessão e cria os atributos necessários nele
if "tema_selecionado" not in st.session_state:
    st.session_state.tema_selecionado = None
if "aula_selecionada" not in st.session_state:
    st.session_state.aula_selecionada = None

# Escolhe a tela de acordo com o estado
if st.session_state.aula_selecionada:
    exibir_tela_3_aula(st.session_state.aula_selecionada)

elif st.session_state.tema_selecionado:
    exibir_tela_2_lista_aulas(st.session_state.tema_selecionado)

else:
    exibir_tela_1_temas()
