import sys
import base64
from pathlib import Path
import streamlit as st
import time

# Alignement du chemin vers le backend
sys.path.append(str(Path(__file__).resolve().parent.parent / "backend"))

# Imports
from ingestion import extract_document
from chunking import chunk_units
from vectorstore import index_chunks, list_indexed_documents, delete_document
from rag import ask

# Configuration
st.set_page_config(
    page_title="Cahier AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ICÔNES SVG ---
def get_svg(icon_name, color="#4F46E5", size=20):
    icons = {
        "logo": f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="{size}" height="{size}"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>''',
        "user": f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="{size}" height="{size}"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>''',
        "assistant": f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="{size}" height="{size}"><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/><circle cx="12" cy="12" r="4"/></svg>''',
        "trash": f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="{size}" height="{size}"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>''',
        "file": f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="{size}" height="{size}"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>''',
        "tag": f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="{size}" height="{size}"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>''',
        "book": f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="{size}" height="{size}"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>''',
        "sparkles": f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="{size}" height="{size}"><path d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707m0-12.728l.707.707m11.314 11.314l.707.707"/><circle cx="12" cy="12" r="7"/></svg>''',
        "upload": f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="{size}" height="{size}"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>''',
        "brain": f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="{size}" height="{size}"><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.98-3A2.5 2.5 0 0 1 9.5 2z"/><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.98-3A2.5 2.5 0 0 0 14.5 2z"/></svg>''',
        "library": f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="{size}" height="{size}"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/><line x1="8" y1="7" x2="16" y2="7"/><line x1="8" y1="11" x2="14" y2="11"/><line x1="8" y1="15" x2="12" y2="15"/></svg>''',
        "send": f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="{size}" height="{size}"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>''',
        "check": f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="{size}" height="{size}"><polyline points="20 6 9 17 4 12"/></svg>'''
    }
    return icons.get(icon_name, "")

def get_svg_avatar_uri(icon_name: str, color: str = "#4F46E5") -> str:
    svg_content = get_svg(icon_name, color, 24)
    b64_encoded = base64.b64encode(svg_content.encode("utf-8")).decode("utf-8")
    return f"data:image/svg+xml;base64,{b64_encoded}"

# --- CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    .stApp { background: #F8FAFC; }
    
    [data-testid="stSidebar"] {
        background: #FFFFFF;
        border-right: 1px solid #E2E8F0;
        padding: 1.5rem 0;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding: 0 1.2rem;
    }
    
    .sidebar-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 1.5rem;
        padding: 0.5rem 0;
    }
    .logo-box {
        background: linear-gradient(135deg, #4F46E5, #7C3AED);
        width: 40px;
        height: 40px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
        flex-shrink: 0;
    }
    .logo-box svg { width: 22px; height: 22px; stroke: white; }
    .logo-title { font-size: 1.3rem; font-weight: 700; color: #0F172A; letter-spacing: -0.5px; }
    .logo-sub { font-size: 0.6rem; font-weight: 600; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.3px; }
    
    .stats-card {
        background: linear-gradient(135deg, #4F46E5, #7C3AED);
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1.5rem;
        color: white;
        box-shadow: 0 4px 16px rgba(79, 70, 229, 0.25);
    }
    .stats-label { font-size: 0.65rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; opacity: 0.9; display: flex; align-items: center; gap: 8px; }
    .stats-number { font-size: 2rem; font-weight: 800; margin: 2px 0; letter-spacing: -1px; }
    .stats-sub { font-size: 0.7rem; opacity: 0.85; }
    
    .section-header {
        font-size: 0.65rem;
        font-weight: 700;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin: 1.2rem 0 0.5rem 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .doc-card {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 0.5rem 0.75rem;
        margin-bottom: 0.4rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        transition: all 0.2s;
    }
    .doc-card:hover { border-color: #4F46E5; box-shadow: 0 2px 8px rgba(79, 70, 229, 0.08); }
    .doc-info { display: flex; align-items: center; gap: 8px; flex: 1; min-width: 0; }
    .doc-name { font-size: 0.8rem; font-weight: 500; color: #1E293B; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    
    .empty-state {
        text-align: center;
        padding: 2.5rem 1.5rem;
        background: white;
        border-radius: 12px;
        border: 2px dashed #E2E8F0;
        margin: 1.5rem 0;
    }
    .empty-state svg { width: 48px; height: 48px; stroke: #94A3B8; margin-bottom: 0.75rem; }
    .empty-title { font-size: 1.2rem; font-weight: 600; color: #0F172A; }
    .empty-desc { font-size: 0.9rem; color: #64748B; max-width: 400px; margin: 0.25rem auto; }
    
    .source-tag {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #F1F5F9;
        color: #475569;
        font-size: 0.7rem;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 6px;
        margin: 3px 4px 3px 0;
        border: 1px solid #E2E8F0;
    }
    
    .main-title {
        font-size: 1.8rem;
        font-weight: 800;
        color: #0F172A;
        letter-spacing: -0.5px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .main-subtitle { color: #64748B; font-size: 0.9rem; margin-top: 0; }
    
    #MainMenu, footer, [data-testid="stDecoration"] { display: none !important; }
    
    .stChatInput > div > div {
        border-radius: 10px !important;
        border: 2px solid #E2E8F0 !important;
    }
    .stChatInput > div > div:focus-within {
        border-color: #4F46E5 !important;
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1) !important;
    }
    
    .stButton button {
        border-radius: 8px !important;
        font-weight: 500 !important;
        transition: all 0.2s !important;
    }
    .stButton button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.15) !important;
    }
    
    .element-container .stButton button {
        background: white !important;
        border: 1px solid #E2E8F0 !important;
        color: #1E293B !important;
    }
    .element-container .stButton button:hover {
        border-color: #4F46E5 !important;
        background: #F5F3FF !important;
        color: #4F46E5 !important;
    }
    
    .st-emotion-cache-1rsy7q7 {
        background: white !important;
        border-radius: 12px !important;
        border: 1px solid #E2E8F0 !important;
    }
    
    [data-testid="stChatMessage"] {
        padding: 0.75rem 0.5rem !important;
        border-bottom: 1px solid #F1F5F9;
    }
    [data-testid="stChatMessage"]:last-child {
        border-bottom: none;
    }
</style>
""", unsafe_allow_html=True)

# --- STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "processed_names" not in st.session_state:
    st.session_state.processed_names = [d["name"] for d in list_indexed_documents()]

# --- FUNCTIONS ---
def process_document(uploaded_file):
    temp_dir = Path("../data/temp_upload")
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_path = temp_dir / uploaded_file.name
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    try:
        units = extract_document(str(temp_path))
        chunks = chunk_units(units)
        if chunks:
            index_chunks(chunks)
            return True
    except Exception as e:
        st.sidebar.error(f"Error: {str(e)}")
        return False
    finally:
        if temp_path.exists():
            temp_path.unlink()
    return False

def generate_answer(query):
    try:
        res = ask(query)
        return res.get("answer", "No response."), res.get("sources", [])
    except Exception as e:
        return f"Technical error: {str(e)}", []

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-header">
        <div class="logo-box">{get_svg("logo", "white", 22)}</div>
        <div>
            <div class="logo-title">Cahier</div>
            <div class="logo-sub">Assistant d'Étude</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    ready_docs = list_indexed_documents()
    
    st.markdown(f"""
    <div class="stats-card">
        <div class="stats-label">{get_svg("library", "white", 16)} Bibliothèque</div>
        <div class="stats-number">{len(ready_docs)}</div>
        <div class="stats-sub">documents indexés • prêts à l'analyse</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="section-header">{get_svg("upload", "#94A3B8", 14)} Ajouter des documents</div>
    """, unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "Déposez vos fichiers ici",
        type=["pdf", "docx", "doc", "pptx", "ppt", "txt"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    if uploaded_files:
        new_files_added = False
        for f in uploaded_files:
            if f.name not in st.session_state.processed_names:
                with st.spinner(f"Indexing {f.name[:30]}..."):
                    if process_document(f):
                        st.session_state.processed_names.append(f.name)
                        new_files_added = True
                        st.toast(f"✅ {f.name} indexed")
        if new_files_added:
            time.sleep(0.3)
            st.rerun()

    st.markdown(f"""
    <div class="section-header">{get_svg("book", "#94A3B8", 14)} Vos documents</div>
    """, unsafe_allow_html=True)
    
    if not ready_docs:
        st.markdown(f"""
        <div style="text-align:center;padding:1.5rem 0.5rem;">
            {get_svg("file", "#CBD5E1", 36)}
            <div style="color:#94A3B8;font-size:0.85rem;font-weight:500;">Aucun document</div>
            <div style="color:#CBD5E1;font-size:0.75rem;">Importez vos cours</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for doc in ready_docs:
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                st.markdown(f"""
                <div class="doc-card">
                    <div class="doc-info">
                        {get_svg("file", "#4F46E5", 16)}
                        <span class="doc-name" title="{doc['name']}">{doc['name']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("✕", key=f"del_{doc['name']}", help=f"Delete {doc['name']}"):
                    delete_document(doc['name'])
                    if doc['name'] in st.session_state.processed_names:
                        st.session_state.processed_names.remove(doc['name'])
                    st.toast(f"🗑️ {doc['name']} deleted")
                    st.rerun()

# --- MAIN ---
st.markdown(f"""
<div style="margin-bottom:1.5rem;">
    <div class="main-title">{get_svg("brain", "#4F46E5", 28)} Mon Espace d'Étude</div>
    <div class="main-subtitle">Posez vos questions, générez des synthèses et testez vos connaissances</div>
</div>
""", unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown(f"""
    <div class="empty-state">
        {get_svg("sparkles", "#94A3B8", 48)}
        <div class="empty-title">Prêt à travailler ?</div>
        <div class="empty-desc">Importez vos cours dans la bibliothèque à gauche pour commencer à interagir avec vos documents.</div>
    </div>
    """, unsafe_allow_html=True)
    
    if ready_docs:
        st.markdown("##### Actions rapides")
        cols = st.columns(3)
        actions = [
            ("Résumer mes cours", "Fais-moi une synthèse structurée des concepts clés de mes cours."),
            ("Générer un quiz", "Crée un questionnaire à choix multiples de 5 questions basé sur mes documents."),
            ("Questions clés", "Quelles sont les questions les plus importantes que je devrais maîtriser sur ce sujet ?")
        ]
        for col, (label, query) in zip(cols, actions):
            with col:
                if st.button(label, use_container_width=True):
                    st.session_state.messages.append({"role": "user", "content": query})
                    st.rerun()

# Display messages
def display_sources(sources):
    if not sources:
        return
    st.markdown("---")
    st.markdown("**Sources**")
    seen = set()
    for s in sources:
        key = f"{s['filename']}_{s['unit_type']}_{s['unit_number']}"
        if key not in seen:
            seen.add(key)
            st.markdown(f"""
            <span class="source-tag">
                {get_svg("tag", "#64748B", 12)}
                {s['filename']} <span style="color:#94A3B8;font-weight:400;">• {s['unit_type']} {s['unit_number']}</span>
            </span>
            """, unsafe_allow_html=True)

for msg in st.session_state.messages:
    avatar = "user" if msg["role"] == "user" else "assistant"
    color = "#1E293B" if msg["role"] == "user" else "#4F46E5"
    with st.chat_message(msg["role"], avatar=get_svg_avatar_uri(avatar, color)):
        st.markdown(msg["content"])
        if msg.get("sources"):
            display_sources(msg["sources"])

# Auto-response
if ready_docs and st.session_state.messages:
    last = st.session_state.messages[-1]
    if last["role"] == "user":
        with st.chat_message("assistant", avatar=get_svg_avatar_uri("assistant", "#4F46E5")):
            with st.spinner("Analyse en cours..."):
                answer, sources = generate_answer(last["content"])
            st.markdown(answer)
            display_sources(sources)
        st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})
        st.rerun()

# Chat input
if ready_docs:
    if question := st.chat_input("Posez votre question sur vos cours..."):
        st.session_state.messages.append({"role": "user", "content": question})
        st.rerun()
else:
    st.info("Importez des documents dans la bibliothèque pour commencer à poser des questions.")