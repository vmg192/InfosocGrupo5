import streamlit as st
import pandas as pd
import google.generativeai as genai
import json

# Este código utiliza o Streamlit como a interface gráfica e host do site.

# Em sua essência, cada vez que app é executado uma tela é carregada com o conteúdo desejado de acordo com o estado atual.
# Cada vez que um botão é selecionado, o estado muda e o app é executado novamente.
# O conteúdo dos cursos estão armazenado no arquivo .csv
# Pela natureza do funcionamento do site e como o código foi feito, basta editar o arquivo que novas aula e até mesmo módulos podem ser adicionados.

# Tenta acessar a chave da api do gemini salva de maneira segura no streamlit cloud para gerar as perguntas
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("Chave da API do Gemini não encontrada. Verifique o arquivo secrets.toml.")

def carregar_conteudo_do_csv(caminho_arquivo="conteudo_curso.csv"):# Nome padrão de arquivo csv, que pode ser alterado
    # Função para extrair o conteúdo do arquivo
    try:
        df = pd.read_csv(caminho_arquivo).fillna('')
    except FileNotFoundError:
        st.error(f"Erro: Arquivo '{caminho_arquivo}' não encontrado. Verifique se o arquivo está na pasta correta.")
        return {}

    conteudo_curso = {}
    
    # Extrai cada elemento da aula do arquivo de acordo com a formatação feita
    for index, linha in df.iterrows():
        modulo = linha['Modulo']
        aula = linha['Aula']
        
        if modulo not in conteudo_curso:
            conteudo_curso[modulo] = {}
            
        opcoes = [
            linha['OpcaoA'],
            linha['OpcaoB'],
            linha['OpcaoC'],
            linha['OpcaoD']
        ]
        
        fontes_str = linha.get('Fontes', '') 
        fontes_lista = [fonte.strip() for fonte in fontes_str.split(';')] if fontes_str else []

        # Adiciona o conteúdo ao dicionário que será utilizado no programa principal
        conteudo_curso[modulo][aula] = {
            "texto": linha['Texto'],
            "pergunta": linha['Pergunta'],
            "opcoes": [opt for opt in opcoes if opt],
            "resposta_correta": linha['RespostaCorreta'],
            "fontes": fontes_lista 
        }
        
    return conteudo_curso

def gerar_pergunta_com_ia(contexto):
    # Basicamente vai gerar um quiz usando como base todo o conteúdo dos textos como xontexto para gerar a pergunta
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Cria um prompt bem definido para garantir que a resposta seja no formato JSON
    prompt = f"""
    Com base no seguinte conteúdo de um curso, gere UMA nova pergunta de múltipla escolha.

    O formato da resposta DEVE ser um objeto JSON válido, sem nenhum texto antes ou depois, contendo as seguintes chaves: "pergunta", "opcoes" (uma lista de 4 strings), "resposta_correta" (a string exata de uma das opções) e "explicacao" (uma explicação curta do porquê a resposta está correta).

    Conteúdo do curso:
    ---
    {contexto}
    ---

    Exemplo de formato de saída JSON:
    {{
      "pergunta": "Qual o principal risco de usar imagens da internet para treinar uma IA?",
      "opcoes": [
        "As imagens terem baixa qualidade",
        "Violação de direitos autorais dos criadores das imagens",
        "O modelo ficar viciado em um estilo específico",
        "O site de onde as imagens foram tiradas processar a empresa"
      ],
      "resposta_correta": "Violação de direitos autorais dos criadores das imagens",
      "explicacao": "Mesmo imagens públicas na internet são protegidas por direitos autorais, e seu uso para treinamento de IA sem permissão é um risco legal."
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        # Limpa a resposta para garantir que seja apenas o JSON
        json_response = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(json_response)
    except Exception as e:
        st.error(f"Ocorreu um erro ao gerar a pergunta: {e}")
        return None

# Carregando o conteúdo
if 'conteudo_curso' not in st.session_state:
    st.session_state.conteudo_curso = carregar_conteudo_do_csv()

#Telas
def exibir_tela_1_temas():
    st.title("Olá! Escolha o Módulo que irá estudar hoje!")
    st.info("Esse site contém um conjunto de aulas, selecionados pela sua empresa, para que você possa se capacitar mais em áreas de extrema importância para todos nós!")
    # Vai criar um botão por módulo
    for nome_tema in st.session_state.conteudo_curso.keys():
        if st.button(nome_tema, use_container_width=True):
            st.session_state.tema_selecionado = nome_tema
            st.rerun()
            
    st.divider()
    if st.button("🧠 Gerar Quiz com IA (Avançado)", use_container_width=True, type="primary"):
        st.session_state.mostrar_quiz_ia = True
        st.rerun()

def exibir_tela_2_lista_aulas(tema_escolhido):
    st.title(f"Aulas de '{tema_escolhido}'")
    st.info("Escolha uma aula para começar.")

    aulas_do_tema = st.session_state.conteudo_curso.get(tema_escolhido, {})
    # Um botão por aula
    for nome_aula in aulas_do_tema.keys():
        if st.button(nome_aula, use_container_width=True):
            st.session_state.aula_selecionada = nome_aula
            st.rerun()
    # Botão de voltar
    st.divider()
    if st.button("<- Voltar para os temas"):
        st.session_state.tema_selecionado = None
        st.rerun()

def exibir_tela_3_aula(tema_selecionado, aula_selecionada):
    # Basicamente pega o conteúdo da aula escolhida e formata adequadamente com a página
    st.title(aula_selecionada)

    aula_info = st.session_state.conteudo_curso[tema_selecionado][aula_selecionada]
    texto_aula = aula_info.get("texto", "Conteúdo não disponível.")
    pergunta_quiz = aula_info.get("pergunta", "")
    opcoes_quiz = aula_info.get("opcoes", [])
    resposta_certa = aula_info.get("resposta_correta", "")
    fontes = aula_info.get("fontes", []) 

    st.markdown("---")
    st.header("Aula")
    st.markdown(texto_aula.replace('\n', '\n\n'))
    
    if fontes:
        with st.expander("Ver fontes e referências"):
            for fonte_url in fontes:
                st.markdown(f"- [{fonte_url}]({fonte_url})")

    st.markdown("---")

    if pergunta_quiz and opcoes_quiz:
        st.header("Quiz")
        
        escolha_usuario = st.radio(
            pergunta_quiz,
            opcoes_quiz,
            index=None,
            key=f"quiz_{aula_selecionada}"
        )

        if st.button("Verificar Resposta", use_container_width=True):
            if escolha_usuario:
                if escolha_usuario.strip() == resposta_certa.strip():
                    st.success(f"Correto! A resposta é: **{resposta_certa}**")
                else:
                    st.error(f"Incorreto. A resposta certa é: **{resposta_certa}**")
            else:
                st.warning("Por favor, selecione uma opção.")

    st.divider()
    if st.button("<- Voltar para a lista de aulas"):
        st.session_state.aula_selecionada = None
        st.rerun()

def exibir_tela_quiz_ia():
    st.title("🧠 Quiz Gerado por IA BETA")
    st.warning("Atenção: Esta funcionalidade usa todo o conteúdo do curso como base. Recomenda-se que você tenha lido todas as aulas antes de prosseguir. Lembre-se de que o conteúdo gerado pode estar incorreto.")
    
    if st.button("Gerar Nova Pergunta"):
        # Concatena todo o texto de todas as aulas para usar como contexto
        todo_o_texto = "\n\n".join(
            aula['texto'] 
            for modulo in st.session_state.conteudo_curso.values() 
            for aula in modulo.values()
        )
        
        with st.spinner("Gerando uma nova pergunta com a ajuda do Gemini..."):
            pergunta_gerada = gerar_pergunta_com_ia(todo_o_texto)
            if pergunta_gerada:
                st.session_state.pergunta_gerada = pergunta_gerada
                # Limpa a resposta anterior
                if 'escolha_ia' in st.session_state:
                    del st.session_state['escolha_ia']

    st.markdown("---")

    if 'pergunta_gerada' in st.session_state:
        quiz = st.session_state.pergunta_gerada
        
        escolha = st.radio(
            quiz['pergunta'],
            quiz['opcoes'],
            index=None,
            key='quiz_ia'
        )

        if st.button("Verificar Resposta"):
            if escolha:
                st.session_state.escolha_ia = escolha # Armazena a escolha para mostrar o resultado
            else:
                st.warning("Por favor, selecione uma opção.")
        
        # Mostra o resultado depois que o usuário verifica
        if 'escolha_ia' in st.session_state:
            if st.session_state.escolha_ia == quiz['resposta_correta']:
                st.success(f"Correto! **Explicação:** {quiz['explicacao']}")
            else:
                st.error(f"Incorreto. A resposta certa é **{quiz['resposta_correta']}**. **Explicação:** {quiz['explicacao']}")


    st.divider()
    if st.button("<- Voltar para o Início"):
        st.session_state.mostrar_quiz_ia = False
        if 'pergunta_gerada' in st.session_state:
            del st.session_state.pergunta_gerada
        if 'escolha_ia' in st.session_state:
            del st.session_state.escolha_ia
        st.rerun()

# Lógica de navegação
# De acordo com o estado (resultado de pressionar determinados botões) a tela é selecionada

if "tema_selecionado" not in st.session_state:
    st.session_state.tema_selecionado = None
if "aula_selecionada" not in st.session_state:
    st.session_state.aula_selecionada = None
if "mostrar_quiz_ia" not in st.session_state:
    st.session_state.mostrar_quiz_ia = False

if st.session_state.conteudo_curso:
    if st.session_state.mostrar_quiz_ia:
        exibir_tela_quiz_ia()
    elif st.session_state.aula_selecionada:
        exibir_tela_3_aula(st.session_state.tema_selecionado, st.session_state.aula_selecionada)
    elif st.session_state.tema_selecionado:
        exibir_tela_2_lista_aulas(st.session_state.tema_selecionado)
    else:
        exibir_tela_1_temas()
