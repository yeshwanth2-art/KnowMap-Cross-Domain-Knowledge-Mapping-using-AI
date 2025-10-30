import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity
import streamlit.components.v1 as components
import os
import tempfile
import sys 

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    HAS_ST = True
except ImportError:
    st.warning("`sentence-transformers` not found. Falling back to TF-IDF (less accurate semantic search). Run: `pip install sentence-transformers numpy scikit-learn`")
    from sklearn.feature_extraction.text import TfidfVectorizer
    HAS_ST = False


if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.error("You must be logged in to view this page.")
    st.stop()


TRIPLES = [
    ("Asia", "has_topic", "Classical Mechanics"),
    ("Asia", "has_topic", "Quantum Mechanics"),
    ("Asia", "related_to", "Mathematics"),
    ("Classical Mechanics", "has_concept", "Newton's Laws"),
    ("Classical Mechanics", "has_concept", "Energy Conservation"),
    ("Quantum Mechanics", "has_concept", "Wave Function"),
    ("Quantum Mechanics", "has_concept", "Uncertainty Principle"),
    ("Mathematics", "has_topic", "Calculus"),
    ("Calculus", "used_in", "Classical Mechanics"),
    ("Quantum Mechanics", "influences", "Philosophy"),
    ("Philosophy", "has_topic", "Epistemology"),
    ("History of Science", "has_figure", "Isaac Newton"),
    ("History of Science", "has_figure", "Albert Einstein"),
    ("Isaac Newton", "born_in", "1643"),
    ("Albert Einstein", "born_in", "1879"),
    ("Technology", "related_to", "Asia"),
    ("Biology", "has_topic", "Genetics"),
    ("Genetics", "has_concept", "DNA"),
    ("DNA", "discovered_by", "Watson & Crick"),
    ("Astronomy", "has_topic", "Astrophysics"),
    ("Astrophysics", "related_to", "Asia"),
    ("Concept A", "subconcept_of", "Asia"),
    ("Concept B", "subconcept_of", "Asia"),
    ("Sun", "is_a", "Star"),
    ("Sun", "related_to", "Astrophysics"),
    ("Sun", "has_feature", "Solar Flares"),
    ("Solar Flares", "affects", "Space Weather"),
    ("Space Weather", "affects", "Satellite Operations"),
    ("Concept C", "linked_to", "History of Science"),
    ("Sub-A1", "part_of", "Concept A"),
    ("Sub-A2", "part_of", "Concept A"),
    ("Sub-B1", "part_of", "Concept B"),
    ("Sub-C1", "part_of", "Concept C"),
    ("Technology", "used_in", "Satellite Operations"),
    ("Philosophy", "influences", "History of Science"),
    ("Mathematics", "used_in", "Astrophysics"),
]

NODE_SENTENCES = {
    "Asia": "Physics is the natural science that studies matter, motion and behavior through space and time.",
    "Classical Mechanics": "Classical mechanics deals with the motion of bodies under forces such as Newton's laws and energy conservation.",
    "Quantum Mechanics": "Quantum mechanics studies physical phenomena at the scale of atoms and subatomic particles and includes the wave function and uncertainty principle.",
    "Mathematics": "Mathematics provides the language and tools used in physical theories, including calculus and linear algebra.",
    "Calculus": "Calculus is used for describing change and motion, including derivatives and integrals.",
    "Newton's Laws": "Newton's laws are foundational principles describing how forces affect motion.",
    "Energy Conservation": "Conservation of energy is a key principle in many physical and engineering systems.",
    "Wave Function": "The wave function is a mathematical description of the quantum state of a system.",
    "Uncertainty Principle": "Heisenberg's uncertainty principle limits the precision of position and momentum measurements.",
    "Philosophy": "Philosophy studies fundamental questions about knowledge, existence, and reasoning.",
    "History of Science": "The history of science traces the development of scientific ideas and influential figures.",
    "Isaac Newton": "Isaac Newton, born 1643, formulated laws of motion and universal gravitation.",
    "Albert Einstein": "Albert Einstein, born 1879, developed the theory of relativity and shaped modern physics.",
    "Technology": "Technology is the application of scientific knowledge for practical purposes, such as satellites.",
    "Biology": "Biology studies living organisms and life processes, including genetics and evolution.",
    "Genetics": "Genetics is the study of heredity and genes, including DNA structure and function.",
    "DNA": "DNA stores genetic information in living organisms.",
    "Sun": "The Sun is a G-type main-sequence star at the center of the Solar System; it produces light and solar activity.",
    "Solar Flares": "Solar flares are sudden eruptions of energy from the Sun's atmosphere that can affect space weather.",
    "Space Weather": "Space weather describes variable conditions in space driven by solar activity and can impact satellites and communications.",
    "Satellite Operations": "Satellite operations manage the functioning and control of satellites orbiting Earth.",
    "Astrophysics": "Astrophysics applies principles of physics and mathematics to study astronomical objects and phenomena.",
    "Concept A": "Concept A is a placeholder central concept in this demo KG.",
    "Concept B": "Concept B is another demo concept that connects to Concept A.",
    "Concept C": "Concept C deals with historical aspects in the demo.",
    "Sub-A1": "Sub-A1 is a subtopic of Concept A.",
    "Sub-A2": "Sub-A2 is a subtopic of Concept A.",
    "Sub-B1": "Sub-B1 is a subtopic of Concept B.",
    "Sub-C1": "Sub-C1 is a subtopic of Concept C.",
}

def build_graph(triples, sentences_map):
    G = nx.Graph()
    for s, p, o in triples:
        if not G.has_node(s):
            G.add_node(s, sentences=[sentences_map.get(s, s)])
        if not G.has_node(o):
            G.add_node(o, sentences=[sentences_map.get(o, o)])
        if not G.has_edge(s, o):
            G.add_edge(s, o, predicate=p)
    return G

@st.cache_resource(show_spinner="Preparing corpus and model...")
def prepare_corpus_and_model(_graph, has_st_flag):
    nodes = list(_graph.nodes())
    docs = [f"{n}: {' '.join(_graph.nodes[n].get('sentences', [n]))}" for n in nodes]
    
    if has_st_flag:
        try:
            model = SentenceTransformer("all-MiniLM-L6-v2")
            embeddings = model.encode(docs, show_progress_bar=False, convert_to_numpy=True)
            return nodes, docs, model, embeddings, None
        except Exception:
            st.error("Failed to load Sentence Transformer model. Falling back to TF-IDF.")
            has_st_flag = False

    if not has_st_flag:
        from sklearn.feature_extraction.text import TfidfVectorizer
        vectorizer = TfidfVectorizer(stop_words="english")
        embeddings = vectorizer.fit_transform(docs)
        return nodes, docs, None, embeddings, vectorizer

def semantic_search(query, nodes, docs, model, embeddings, vectorizer, top_k=5):
    if not query:
        return []
    
    if model is not None:
        q_emb = model.encode([query], convert_to_numpy=True)
        sims = cosine_similarity(q_emb, embeddings)[0]
    elif vectorizer is not None:
        q_vec = vectorizer.transform([query])
        sims = linear_kernel(q_vec, embeddings).flatten()
    else:
        return [] 

    idxs = sims.argsort()[::-1][:top_k]
    return [(nodes[i], float(sims[i])) for i in idxs]

def build_subgraph_from_matches(graph, matched_nodes, depth=1):
    nodes = set(matched_nodes)
    frontier = set(matched_nodes)
    for _ in range(depth):
        new = set()
        for n in frontier:
            new.update(graph.neighbors(n))
        frontier = new - nodes
        nodes.update(new)
    return graph.subgraph(nodes).copy()

def visualize_graph(G, height=500):
    net = Network(height=f"{height}px", width="100%", bgcolor="#222222", font_color="white", cdn_resources="local")
    
    # Add nodes and edges
    for n, attr in G.nodes(data=True):
        net.add_node(n, label=n, title=" ".join(attr.get("sentences", [n])), color="#87ceeb", size=20)
    for u, v, attr in G.edges(data=True):
        net.add_edge(u, v, title=attr.get("predicate", ""), color="#7fffd4")
        
    tmp_dir = tempfile.gettempdir()
    tmp_path = os.path.join(tmp_dir, "graph.html")
    net.save_graph(tmp_path)
    
    with open(tmp_path, "r", encoding="utf-8") as f:
        html = f.read()
    components.html(html, height=height)


st.title("🌐 Knowledge Graph & Semantic Search")
st.info("Upload your dataset, explore knowledge graphs, and perform semantic search.")

st.sidebar.header("📂 Dataset Upload")
uploaded_file = st.sidebar.file_uploader("Upload dataset (CSV or Excel)", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        if all(col in df.columns for col in ["subject", "predicate", "object"]):
            uploaded_triples = list(df[["subject", "predicate", "object"]].itertuples(index=False, name=None))
            TRIPLES = uploaded_triples  
            st.sidebar.success(f"Loaded {len(uploaded_triples)} triples from uploaded dataset.")
            
            st.cache_data.clear()
            st.cache_resource.clear()
        else:
            st.sidebar.error("File must contain columns: subject, predicate, object.")
    except Exception as e:
        st.sidebar.error(f"Error reading file: {e}")

KG = build_graph(TRIPLES, NODE_SENTENCES)
nodes, docs, model, embeddings, vectorizer = prepare_corpus_and_model(KG, HAS_ST)


col1, col2 = st.columns([3, 2])
with col1:
    st.subheader("Full Graph View")
    visualize_graph(KG, height=600)

with col2:
    st.subheader("🔍 Semantic Search")
    q = st.text_input("Enter search query", placeholder="e.g. quantum mechanics, Sun, calculus")
    k = st.slider("Top-K matches", 1, 10, 5)
    depth = st.slider("Expansion depth", 0, 3, 1)
    
    if st.button("Search", use_container_width=True):
        if not q.strip():
            st.warning("Please enter a query to search.")
        else:
            results = semantic_search(q, nodes, docs, model, embeddings, vectorizer, top_k=k)
            
            if not results:
                st.warning("No matches found.")
            else:
                st.markdown("**Top Matches:**")
                results_df = pd.DataFrame(results, columns=['Concept', 'Similarity Score'])
                st.dataframe(results_df, hide_index=True, use_container_width=True)
                
                matched_nodes = [n for n, _ in results]
                sub = build_subgraph_from_matches(KG, matched_nodes, depth)
                st.markdown("### Subgraph View")
                visualize_graph(sub, height=400)