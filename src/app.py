import streamlit as st
import pandas as pd
import json
import time
import db
from solidos_platonicos import circulo_svg, solidos_platonicos

# Initialize the database on startup
db.init_db()

st.set_page_config(page_title="Flashcards", page_icon="📇", layout="wide")

if "authenticated_user" not in st.session_state:
    st.session_state.authenticated_user = None

if st.session_state.authenticated_user is None:
    st.title("Login")
    with st.form("login_form"):
        email = st.text_input("E-mail")
        password = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar", use_container_width=True)

    if submitted:
        user = db.authenticate_user(email, password)
        if user:
            st.session_state.authenticated_user = user
            st.rerun()
        else:
            st.error("E-mail ou senha inválidos.")
    st.stop()

# Custom CSS para melhor responsividade
st.markdown("""
<style>
    /* Mobile-first responsive adjustments */
    @media (max-width: 640px) {
        [data-testid="stColumns"] {
            margin-left: -0.5rem;
            margin-right: -0.5rem;
        }
        .stButton button {
            width: 100%;
        }
        .stSelectbox > div > div > select {
            font-size: 14px;
        }
    }
    
    /* Melhorar readabilidade em flashcards */
    [data-testid="stMetricValue"] {
        font-size: clamp(1.5rem, 4vw, 2.5rem);
    }
    
    /* Responsividade para dataframes */
    [data-testid="stDataFrame"] {
        overflow-x: auto;
    }
</style>
""", unsafe_allow_html=True)

# Cache para funções de banco de dados
@st.cache_data(ttl=60)
def cached_get_collections():
    return db.get_collections()

@st.cache_data(ttl=60)
def cached_get_decks(collection_id):
    return db.get_decks(collection_id)

@st.cache_data(ttl=60)
def cached_get_deck_performance(deck_id):
    return db.get_deck_performance(deck_id)

@st.cache_data(ttl=300)
def cached_get_cards_prioritized(deck_id):
    return db.get_cards_prioritized(deck_id)

@st.cache_data(ttl=60)
def cached_get_cards(deck_id):
    return db.get_cards(deck_id)

@st.cache_data(ttl=60)
def cached_get_questions(deck_id):
    return db.get_questions(deck_id)

@st.cache_data(ttl=60)
def cached_get_tratak_history():
    return db.get_tratak_history()

st.title("📇 Flashcards@")
st.markdown("> *\"That's how knowledge works. It builds up, like compound interest.\" - Warren Buffett*")

# Navigation Sidebar
st.sidebar.title("Navegação")
st.sidebar.caption(st.session_state.authenticated_user["email"])
if st.sidebar.button("Sair", use_container_width=True):
    st.session_state.authenticated_user = None
    st.rerun()
menu = ["Estudar", "Estudar Questões", "Desempenho", "Upload de Cards", "Upload de Questões", "Gerenciar Coleções & Decks", "Gerenciar Cards", "Gerenciar Questões", "Meditação"]
choice = st.sidebar.radio("Ir para", menu)

if choice == "Estudar":
    # st.header("Estudar Flashcards (Spaced Repetition)")
    collections = cached_get_collections()
    if not collections:
        st.info("Nenhuma coleção encontrada. Vá para 'Gerenciar Coleções & Decks' para criar uma.")
    else:
        coll_dict = {c[1]: c[0] for c in collections}
        selected_coll_name = st.selectbox("Selecione uma Coleção", list(coll_dict.keys()), key="study_coll")
        selected_coll_id = coll_dict[selected_coll_name]
        
        decks = cached_get_decks(selected_coll_id)
        if not decks:
            st.info("Nenhum deck encontrado nesta coleção.")
        else:
            deck_dict = {d[2]: d[0] for d in decks}
            selected_deck_name = st.selectbox("Selecione um Deck", list(deck_dict.keys()), key="study_deck")
            selected_deck_id = deck_dict[selected_deck_name]
            
            # Prioritized cards
            cards = cached_get_cards_prioritized(selected_deck_id)
            if not cards:
                st.info("Nenhum card encontrado neste deck. Adicione alguns em 'Gerenciar Cards' ou 'Upload'.")
            else:
                if 'current_card_index' not in st.session_state:
                    st.session_state.current_card_index = 0
                if 'show_answer' not in st.session_state:
                    st.session_state.show_answer = False
                if 'start_time' not in st.session_state:
                    st.session_state.start_time = time.time()
                
                # Check bounds
                if st.session_state.current_card_index >= len(cards):
                    st.session_state.current_card_index = 0
                
                card = cards[st.session_state.current_card_index]
                
                # Progress indicator
                progress = (st.session_state.current_card_index + 1) / len(cards)
                col_prog, col_text = st.columns([20, 1])
                with col_prog:
                    st.progress(progress)
                with col_text:
                    st.caption(f"{st.session_state.current_card_index + 1}/{len(cards)}")
                
                # Flashcard Display - responsivo
                st.markdown("### Pergunta (Frente):")
                st.info(card['front'])
                if card['tags']:
                    st.caption(f"Tags: {card['tags']}")
                
                if st.session_state.show_answer:
                    st.markdown("### Resposta (Verso):")
                    st.success(card['back'])
                    
                    st.write("Como você foi?")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("❌ Errei", use_container_width=True, key=f"wrong_{card['id']}"):
                            duration_ms = int((time.time() - st.session_state.start_time) * 1000)
                            db.record_review(card['id'], False, duration_ms)
                            st.session_state.current_card_index += 1
                            st.session_state.show_answer = False
                            st.session_state.start_time = time.time()
                            st.cache_data.clear()
                            st.rerun()
                    with col2:
                        if st.button("✅ Acertei", use_container_width=True, key=f"correct_{card['id']}"):
                            duration_ms = int((time.time() - st.session_state.start_time) * 1000)
                            db.record_review(card['id'], True, duration_ms)
                            st.session_state.current_card_index += 1
                            st.session_state.show_answer = False
                            st.session_state.start_time = time.time()
                            st.cache_data.clear()
                            st.rerun()
                else:
                    if st.button("Revelar Resposta", use_container_width=True, key=f"reveal_{card['id']}"):
                        st.session_state.show_answer = True
                        st.rerun()

elif choice == "Estudar Questões":
    st.header("Estudar Questões")
    collections = cached_get_collections()
    if not collections:
        st.info("Nenhuma coleção encontrada. Vá para 'Gerenciar Coleções & Decks' para criar uma.")
    else:
        coll_dict = {c[1]: c[0] for c in collections}
        selected_coll_name = st.selectbox("Selecione uma Coleção", list(coll_dict.keys()), key="question_study_coll")
        decks = cached_get_decks(coll_dict[selected_coll_name])
        if not decks:
            st.info("Nenhum deck encontrado nesta coleção.")
        else:
            deck_dict = {d[2]: d[0] for d in decks}
            selected_deck_name = st.selectbox("Selecione um Deck", list(deck_dict.keys()), key="question_study_deck")
            questions = cached_get_questions(deck_dict[selected_deck_name])
            if not questions:
                st.info("Nenhuma questão encontrada neste deck. Cadastre uma em 'Gerenciar Questões'.")
            else:
                if 'current_question_index' not in st.session_state:
                    st.session_state.current_question_index = 0
                if st.session_state.current_question_index >= len(questions):
                    st.session_state.current_question_index = 0

                question = questions[st.session_state.current_question_index]
                question_options = question[3]
                option_keys = ["A", "B", "C", "D"]
                available_options = {
                    key: str(question_options.get(key, ""))
                    for key in option_keys
                    if question_options.get(key, "")
                }

                st.progress((st.session_state.current_question_index + 1) / len(questions))
                st.caption(f"Questão {st.session_state.current_question_index + 1}/{len(questions)}")
                st.subheader(question[2])
                selected_answer = st.radio(
                    "Escolha uma alternativa",
                    list(available_options),
                    format_func=lambda key: f"{key}) {available_options[key]}",
                    key=f"question_answer_{question[0]}",
                )

                if 'question_feedback' not in st.session_state:
                    st.session_state.question_feedback = None

                if st.session_state.question_feedback is None:
                    if st.button("Responder", use_container_width=True, key=f"answer_{question[0]}"):
                        st.session_state.question_feedback = (
                            selected_answer == question[4],
                            question[4],
                            available_options.get(question[4], question[4]),
                        )
                        st.rerun()
                else:
                    is_correct, correct_key, correct_text = st.session_state.question_feedback
                    if is_correct:
                        st.success("Resposta correta!")
                    else:
                        st.error(f"Resposta incorreta. A resposta correta é {correct_key}) {correct_text}.")
                    if st.button("Próxima questão", use_container_width=True, key=f"next_question_{question[0]}"):
                        st.session_state.current_question_index += 1
                        st.session_state.question_feedback = None
                        st.rerun()

elif choice == "Desempenho":
    st.header("📊 Desempenho")
    collections = cached_get_collections()
    if collections:
        coll_dict = {c[1]: c[0] for c in collections}
        selected_coll = st.selectbox("Coleção", list(coll_dict.keys()), key="perf_coll")
        decks = cached_get_decks(coll_dict[selected_coll])
        if decks:
            deck_dict = {d[2]: d[0] for d in decks}
            selected_deck = st.selectbox("Deck", list(deck_dict.keys()), key="perf_deck")
            
            stats = cached_get_deck_performance(deck_dict[selected_deck])
            global_stats = stats['global']
            
            total_reviews = global_stats[0] if global_stats[0] else 0
            correct = global_stats[1] if global_stats[1] else 0
            incorrect = global_stats[2] if global_stats[2] else 0
            avg_duration_ms = global_stats[3] if global_stats[3] else 0
            
            if total_reviews > 0:
                acc_rate = (correct / total_reviews) * 100
                st.subheader("Métricas Globais do Deck")
                
                # Responsivo: 2 colunas em mobile, 4 em desktop
                cols = st.columns(2)
                with cols[0]:
                    st.metric("Total de Revisões", total_reviews)
                with cols[1]:
                    st.metric("Acertos", f"{correct} ({acc_rate:.1f}%)")
                
                cols = st.columns(2)
                with cols[0]:
                    st.metric("Erros", incorrect)
                with cols[1]:
                    st.metric("Tempo Médio/Card", f"{avg_duration_ms/1000:.1f}s")
                
                st.subheader("Visualizações Recentes dos Cards")
                cards_stats = stats['cards']
                df = pd.DataFrame(cards_stats, columns=['ID', 'Frente', 'Verso','Última Vez Visto'])
                df['Última Vez Visto'] = df['Última Vez Visto'].fillna('Nunca')
                st.dataframe(df, hide_index=True, use_container_width=True,height="content")
            else:
                st.info("Nenhuma revisão feita neste deck ainda. Comece a estudar!")
        else:
            st.warning("Nenhum deck nesta coleção.")
    else:
        st.warning("Nenhuma coleção criada.")

elif choice == "Upload de Cards":
    st.header("📤 Upload de Cards (CSV / JSON)")
    st.markdown("Faça upload de um arquivo contendo as colunas/chaves: `front` (frente), `back` (verso) e `tags` (opcional).")
    
    collections = cached_get_collections()
    if collections:
        coll_dict = {c[1]: c[0] for c in collections}
        selected_coll = st.selectbox("Selecione a Coleção Base", list(coll_dict.keys()), key="upload_coll")
        decks = cached_get_decks(coll_dict[selected_coll])
        
        if decks:
            deck_dict = {d[2]: d[0] for d in decks}
            selected_deck = st.selectbox("Selecione o Deck de Destino", list(deck_dict.keys()), key="upload_deck")
            
            uploaded_file = st.file_uploader("Escolha um arquivo CSV ou JSON", type=["csv", "json"])
            
            if uploaded_file is not None:
                try:
                    cards_list = []
                    if uploaded_file.name.endswith(".csv"):
                        df = pd.read_csv(uploaded_file)
                        if 'front' not in df.columns or 'back' not in df.columns:
                            st.error("Erro: O arquivo CSV deve conter colunas 'front' e 'back'.")
                        else:
                            for _, row in df.iterrows():
                                tags = row['tags'] if 'tags' in df.columns else ''
                                # Convert nans to string
                                tags = str(tags) if pd.notna(tags) else ''
                                cards_list.append({'front': str(row['front']), 'back': str(row['back']), 'tags': tags})
                                
                    elif uploaded_file.name.endswith(".json"):
                        data = json.load(uploaded_file)
                        for item in data:
                            if 'front' in item and 'back' in item:
                                cards_list.append({
                                    'front': str(item['front']),
                                    'back': str(item['back']),
                                    'tags': str(item.get('tags', ''))
                                })
                            else:
                                st.warning("Alguns itens no JSON foram ignorados por falta de 'front' ou 'back'.")
                    
                    if cards_list:
                        st.write(f"{len(cards_list)} cards lidos do arquivo.")
                        if st.button(f"Iniciar Importação para o deck {selected_deck}", use_container_width=True):
                            db.bulk_insert_cards(deck_dict[selected_deck], cards_list)
                            st.cache_data.clear()
                            st.success(f"{len(cards_list)} cards inseridos com sucesso!")
                except Exception as e:
                    st.error(f"Ocorreu um erro ao ler o arquivo: {e}")
        else:
            st.warning("Nenhum deck nesta coleção. Crie um deck primeiro.")
    else:
        st.warning("Nenhuma coleção criada.")

elif choice == "Upload de Questões":
    st.header("Upload de Questões (CSV / JSON)")
    st.markdown(
        "Use `pergunta`, `opcao_a`, `opcao_b`, `opcao_c`, `opcao_d` e `resposta`. "
        "A resposta deve ser A, B, C ou D."
    )

    collections = cached_get_collections()
    if collections:
        coll_dict = {c[1]: c[0] for c in collections}
        selected_coll = st.selectbox("Selecione a Coleção Base", list(coll_dict.keys()), key="question_upload_coll")
        decks = cached_get_decks(coll_dict[selected_coll])

        if decks:
            deck_dict = {d[2]: d[0] for d in decks}
            selected_deck = st.selectbox("Selecione o Deck de Destino", list(deck_dict.keys()), key="question_upload_deck")
            uploaded_file = st.file_uploader(
                "Escolha um arquivo CSV ou JSON",
                type=["csv", "json"],
                key="question_upload_file",
            )

            if uploaded_file is not None:
                try:
                    questions_list = []
                    if uploaded_file.name.endswith(".csv"):
                        data = pd.read_csv(uploaded_file).fillna("").to_dict("records")
                    else:
                        data = json.load(uploaded_file)

                    for item in data:
                        options = item.get("opcoes")
                        if isinstance(options, str):
                            options = json.loads(options)
                        if not isinstance(options, dict):
                            options = {
                                "A": str(item.get("opcao_a", "")),
                                "B": str(item.get("opcao_b", "")),
                                "C": str(item.get("opcao_c", "")),
                                "D": str(item.get("opcao_d", "")),
                            }

                        answer = str(item.get("resposta", "")).strip().upper()
                        question = str(item.get("pergunta", "")).strip()
                        options = {key: str(options.get(key, "")).strip() for key in ["A", "B", "C", "D"]}
                        if question and all(options.values()) and answer in options:
                            questions_list.append({
                                "pergunta": question,
                                "opcoes": options,
                                "resposta": answer,
                            })

                    if questions_list:
                        st.write(f"{len(questions_list)} questões lidas do arquivo.")
                        if st.button("Iniciar Importação", use_container_width=True, key="import_questions"):
                            db.bulk_insert_questions(deck_dict[selected_deck], questions_list)
                            st.cache_data.clear()
                            st.success(f"{len(questions_list)} questões inseridas com sucesso!")
                    else:
                        st.warning("Nenhuma questão válida foi encontrada no arquivo.")
                except (ValueError, json.JSONDecodeError) as error:
                    st.error(f"Erro no formato do arquivo: {error}")
        else:
            st.warning("Nenhum deck nesta coleção. Crie um deck primeiro.")
    else:
        st.warning("Nenhuma coleção criada.")

elif choice == "Gerenciar Coleções & Decks":
    # ── ADD COLLECTION ───────────────────────────────────────────────────────
    st.header("Gerenciar Coleções")
    with st.form("add_collection_form"):
        st.subheader("➕ Adicionar Nova Coleção")
        coll_name = st.text_input("Nome")
        coll_desc = st.text_area("Descrição")
        if st.form_submit_button("Adicionar"):
            if coll_name:
                if db.add_collection(coll_name, coll_desc):
                    st.cache_data.clear()
                    st.success("Coleção adicionada!")
                else:
                    st.error("Coleção com este nome já existe.")
            else:
                st.warning("O nome da coleção é obrigatório.")

    # ── DELETE COLLECTION ────────────────────────────────────────────────────
    collections = cached_get_collections()
    if collections:
        coll_dict_all = {c[1]: c[0] for c in collections}
        st.subheader("🗑️ Excluir Coleção")
        st.warning("⚠️ Excluir uma coleção remove **todos** os decks, cards e histórico de revisões associados. Esta ação é irreversível!")
        coll_to_delete = st.selectbox("Selecione a coleção para excluir", list(coll_dict_all.keys()), key="del_coll")
        if st.button("Excluir Coleção Selecionada", type="primary", use_container_width=True):
            db.delete_collection(coll_dict_all[coll_to_delete])
            st.cache_data.clear()
            st.success(f"Coleção '{coll_to_delete}' e todos os dados vinculados foram excluídos.")
            st.rerun()

    st.markdown("---")

    # ── ADD DECK ─────────────────────────────────────────────────────────────
    st.header("Gerenciar Decks")
    collections = cached_get_collections()
    if collections:
        coll_dict = {c[1]: c[0] for c in collections}
        with st.form("add_deck_form"):
            st.subheader("➕ Adicionar Novo Deck")
            selected_coll = st.selectbox("Atribuir à Coleção", list(coll_dict.keys()), key="add_deck_coll")
            deck_name = st.text_input("Nome do Deck")
            deck_desc = st.text_area("Descrição do Deck")
            if st.form_submit_button("Adicionar"):
                if deck_name:
                    db.add_deck(coll_dict[selected_coll], deck_name, deck_desc)
                    st.cache_data.clear()
                    st.success("Deck adicionado!")
                else:
                    st.warning("Nome do deck é obrigatório.")

        # ── DELETE DECK ──────────────────────────────────────────────────────
        st.subheader("🗑️ Excluir Deck")
        st.warning("⚠️ Excluir um deck remove **todos** os cards e histórico de revisões desse deck. Esta ação é irreversível!")
        del_coll_name = st.selectbox("Coleção do Deck a excluir", list(coll_dict.keys()), key="del_deck_coll")
        decks_in_coll = cached_get_decks(coll_dict[del_coll_name])
        if decks_in_coll:
            deck_del_dict = {d[2]: d[0] for d in decks_in_coll}
            deck_to_delete = st.selectbox("Selecione o deck para excluir", list(deck_del_dict.keys()), key="del_deck")
            if st.button("Excluir Deck Selecionado", type="primary", use_container_width=True):
                db.delete_deck(deck_del_dict[deck_to_delete])
                st.cache_data.clear()
                st.success(f"Deck '{deck_to_delete}' e todos os dados vinculados foram excluídos.")
                st.rerun()
        else:
            st.info("Nenhum deck disponível nesta coleção.")

elif choice == "Gerenciar Cards":
    st.header("Gerenciar Cards")
    collections = cached_get_collections()
    if collections:
        coll_dict = {c[1]: c[0] for c in collections}
        selected_coll = st.selectbox("Coleção", list(coll_dict.keys()), key="manage_coll")
        decks = cached_get_decks(coll_dict[selected_coll])
        
        if decks:
            deck_dict = {d[2]: d[0] for d in decks}
            selected_deck = st.selectbox("Deck", list(deck_dict.keys()), key="manage_deck")
            
            with st.form("add_card_form"):
                st.subheader("Adicionar Novo Card (Manual)")
                front = st.text_area("Frente (Pergunta)")
                back = st.text_area("Verso (Resposta)")
                tags = st.text_input("Tags (Opcional)")
                if st.form_submit_button("Adicionar Card", use_container_width=True):
                    if front and back:
                        db.add_card(deck_dict[selected_deck], front, back, tags)
                        st.cache_data.clear()
                        st.success("Card adicionado!")
                    else:
                        st.warning("Frente e verso são obrigatórios.")
            
            st.markdown("---")
            st.subheader("Cards Existentes no Deck")
            cards = cached_get_cards(deck_dict[selected_deck])
            if cards:
                df = pd.DataFrame(cards, columns=['ID', 'Deck ID', 'Frente', 'Verso', 'Tags'])
                
                # Exibir em abas se muitos cards
                if len(cards) > 10:
                    with st.expander(f"Ver {len(cards)} cards", expanded=True):
                        st.dataframe(df[['ID', 'Frente', 'Verso', 'Tags']], hide_index=True, use_container_width=True)
                else:
                    st.dataframe(df[['ID', 'Frente', 'Verso', 'Tags']], hide_index=True, use_container_width=True)
                
                col1, col2 = st.columns([3, 2])
                with col1:
                    card_to_delete = st.selectbox("Selecione o ID do Card para Deletar", df['ID'].tolist())
                with col2:
                    st.write("")  # espaçamento
                    if st.button("Deletar Card Selecionado", type="primary", use_container_width=True):
                        db.delete_card(card_to_delete)
                        st.cache_data.clear()
                        st.success(f"Card {card_to_delete} deletado.")
                        st.rerun()
            else:
                st.info("Nenhum card neste deck.")
        else:
            st.warning("Nenhum deck encontrado.")

elif choice == "Gerenciar Questões":
    st.header("Gerenciar Questões")
    collections = cached_get_collections()
    if collections:
        coll_dict = {c[1]: c[0] for c in collections}
        selected_coll = st.selectbox("Coleção", list(coll_dict.keys()), key="question_manage_coll")
        decks = cached_get_decks(coll_dict[selected_coll])

        if decks:
            deck_dict = {d[2]: d[0] for d in decks}
            selected_deck = st.selectbox("Deck", list(deck_dict.keys()), key="question_manage_deck")
            selected_deck_id = deck_dict[selected_deck]

            with st.form("add_question_form"):
                st.subheader("Adicionar Nova Questão")
                pergunta = st.text_area("Pergunta")
                option_a = st.text_input("Alternativa A")
                option_b = st.text_input("Alternativa B")
                option_c = st.text_input("Alternativa C")
                option_d = st.text_input("Alternativa D")
                resposta = st.selectbox("Resposta correta", ["A", "B", "C", "D"])
                if st.form_submit_button("Adicionar Questão", use_container_width=True):
                    options = {"A": option_a, "B": option_b, "C": option_c, "D": option_d}
                    if pergunta and all(options.values()):
                        db.add_question(selected_deck_id, pergunta, options, resposta)
                        st.cache_data.clear()
                        st.success("Questão adicionada!")
                    else:
                        st.warning("Pergunta e todas as quatro alternativas são obrigatórias.")

            st.markdown("---")
            st.subheader("Questões existentes no deck")
            questions = cached_get_questions(selected_deck_id)
            if questions:
                question_rows = [
                    [question[0], question[2], question[4]]
                    for question in questions
                ]
                df = pd.DataFrame(question_rows, columns=["ID", "Pergunta", "Resposta"])
                st.dataframe(df, hide_index=True, use_container_width=True)

                question_to_delete = st.selectbox("Selecione o ID da questão para deletar", df["ID"].tolist())
                if st.button("Deletar Questão Selecionada", type="primary", use_container_width=True):
                    db.delete_question(question_to_delete)
                    st.cache_data.clear()
                    st.success(f"Questão {question_to_delete} deletada.")
                    st.rerun()
            else:
                st.info("Nenhuma questão neste deck.")
        else:
            st.warning("Nenhum deck encontrado.")
    else:
        st.warning("Nenhuma coleção criada.")

elif choice == "Meditação":
    st.header("🧘 Meditação")
    meditation_mode = st.radio(
        "Escolha a prática",
        ["Tratak", "Sólidos Platônicos"],
        horizontal=True,
        key="meditation_mode",
    )

    st.subheader("🔵 Tratak")
    st.markdown("""
    > *Tratak é uma prática de meditação em que você foca o olhar num único ponto sem piscar.*  
    > Escolha a duração, inicie e mantenha o foco no ponto central do círculo.
    """)

    # ── Session state init ────────────────────────────────────────────────────
    if 'tratak_running' not in st.session_state:
        st.session_state.tratak_running = False
    if 'tratak_remaining' not in st.session_state:
        st.session_state.tratak_remaining = 0
    if 'tratak_total' not in st.session_state:
        st.session_state.tratak_total = 0
    if 'tratak_last_tick' not in st.session_state:
        st.session_state.tratak_last_tick = 0.0
    if 'tratak_saved' not in st.session_state:
        st.session_state.tratak_saved = False

    # ── Duration selector ────────────────────────────────────────────────────
    duration_options = {"1 minuto": 60, "5 minutos": 300, "10 minutos": 600, "15 minutos": 900}
    if not st.session_state.tratak_running:
        selected_label = st.radio(
            "Duração da sessão:",
            list(duration_options.keys()),
            horizontal=True,
            key="tratak_dur_radio"
        )
        chosen_seconds = duration_options[selected_label]
    else:
        chosen_seconds = st.session_state.tratak_total

    # ── Circle widget (Responsivo) ────────────────────────────────────────────
    remaining = st.session_state.tratak_remaining
    total     = st.session_state.tratak_total if st.session_state.tratak_total > 0 else chosen_seconds
    mins, secs = divmod(remaining, 60)
    timer_text = f"{mins:02d}:{secs:02d}"

    if meditation_mode == "Tratak":
        st.markdown(circulo_svg, unsafe_allow_html=True)
    else:
        solid_names = ["tetraedro", "cubo", "octaedro", "dodecaedro", "icosaedro"]
        solid_name = solid_names[int(time.time()) % len(solid_names)]
        st.markdown(solidos_platonicos[solid_name], unsafe_allow_html=True)

    # ── Cronômetro separado ────────────────────────────────────────────────────
    timer_html = f"""
    <div style="display:flex; justify-content:center; margin: 0 0 24px 0;">
      <span style="
        font-family: 'Courier New', monospace;
        font-size: clamp(2.5rem, 10vw, 4rem);
        font-weight: 800;
        letter-spacing: 6px;
        color: #3949ab;
        background: #f0f2ff;
        border: 3px solid #c5cae9;
        border-radius: 16px;
        padding: clamp(5px, 2vw, 10px) clamp(20px, 5vw, 36px);
      ">{timer_text}</span>
    </div>
    """
    st.markdown(timer_html, unsafe_allow_html=True)

    # ── Start / Stop buttons ──────────────────────────────────────────────────
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if not st.session_state.tratak_running:
            if st.button("▶ Iniciar", use_container_width=True, type="primary"):
                st.session_state.tratak_total     = chosen_seconds
                st.session_state.tratak_remaining = chosen_seconds
                st.session_state.tratak_running   = True
                st.session_state.tratak_last_tick = time.time()
                st.session_state.tratak_saved     = False
                st.rerun()
        else:
            if st.button("⏹ Parar", use_container_width=True):
                elapsed = st.session_state.tratak_total - st.session_state.tratak_remaining
                if elapsed > 0 and not st.session_state.tratak_saved:
                    db.save_tratak_session(elapsed)
                    st.session_state.tratak_saved = True
                st.session_state.tratak_running   = False
                st.session_state.tratak_remaining = 0
                st.rerun()

    # ── Countdown tick ────────────────────────────────────────────────────────
    if st.session_state.tratak_running:
        now = time.time()
        elapsed_tick = now - st.session_state.tratak_last_tick
        st.session_state.tratak_last_tick = now
        st.session_state.tratak_remaining = max(
            0, st.session_state.tratak_remaining - int(elapsed_tick)
        )

        if st.session_state.tratak_remaining <= 0:
            # Session complete
            if not st.session_state.tratak_saved:
                db.save_tratak_session(st.session_state.tratak_total)
                st.session_state.tratak_saved = True
            st.session_state.tratak_running = False
            st.success("✅ Sessão concluída! Muito bem.")
            st.balloons()
        else:
            time.sleep(1)
            st.rerun()

    # ── Evolution chart ───────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("📈 Evolução das Sessões")

    history = cached_get_tratak_history()
    if history:
        df_hist = pd.DataFrame(history, columns=["ID", "Duração (s)", "Data/Hora"])
        df_hist["Data/Hora"] = pd.to_datetime(df_hist["Data/Hora"])
        df_hist["Data"] = df_hist["Data/Hora"].dt.strftime("%d/%m %H:%M")
        df_hist["Duração (min)"] = (df_hist["Duração (s)"] / 60).round(2)

        # Summary metrics (responsivo: 1 coluna em mobile, 3 em desktop)
        metric_cols = st.columns(1) if st.session_state.get('is_mobile') else st.columns(3)
        
        total_sessions = len(df_hist)
        total_minutes  = df_hist["Duração (s)"].sum() // 60
        avg_minutes    = df_hist["Duração (s)"].mean() / 60

        m_cols = st.columns(2)
        m_cols[0].metric("Total de Sessões", total_sessions)
        m_cols[1].metric("Total de Minutos", int(total_minutes))
        st.metric("Média por Sessão", f"{avg_minutes:.1f} min")

        # Bar chart (chronological order)
        df_chart = df_hist.iloc[::-1].reset_index(drop=True)
        st.bar_chart(
            data=df_chart.set_index("Data")["Duração (min)"],
            use_container_width=True,
            height=300
        )

        # Full history table
        with st.expander("Ver histórico completo"):
            st.dataframe(
                df_hist[["Data/Hora", "Duração (s)", "Duração (min)"]],
                hide_index=True,
                use_container_width=True
            )
    else:
        st.info("Nenhuma sessão registrada ainda. Complete sua primeira prática!")


