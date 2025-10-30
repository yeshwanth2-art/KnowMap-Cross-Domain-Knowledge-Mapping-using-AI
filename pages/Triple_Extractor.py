import streamlit as st
import spacy
import pandas as pd

if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.error("You must be logged in to view this page.")
    st.stop()

@st.cache_resource
def load_spacy_model():
    """Load the SpaCy model once."""
    try:
        return spacy.load("en_core_web_sm")
    except Exception as e:
        st.error(f"Failed to load SpaCy model. Did you run 'python -m spacy download en_core_web_sm'? Error: {e}")
        return None

nlp = load_spacy_model()

def extract_entities_and_triples(text):
    """Simple function to extract entities (nodes) and mock triples."""
    if not nlp:
        return [], []
        
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    
    mock_triples = []
    
    if len(entities) >= 2:
        e1, e2 = entities[0][0], entities[1][0]
        mock_triples.append((e1, "is_related_to", e2))
    
    return entities, mock_triples

st.title("🧠 Automated Triple Extractor")
st.warning("This page uses a simple SpaCy model to **simulate** the entity and triple extraction process.")

if "uploaded_df" not in st.session_state:
    st.error("Please upload a dataset first via the 'Dataset Manager' page.")
    st.stop()

df = st.session_state["uploaded_df"]
text_column = st.session_state.get("text_column_selector", df.columns[0])

st.markdown(f"**Data Source:** `{st.session_state['data_source_name']}` | **Text Column Used:** `{text_column}`")

st.markdown("---")
if st.button("▶️ Run Triple Extraction on Data", type="primary", use_container_width=True):
    with st.spinner(f"Extracting entities and triples from column '{text_column}'..."):
        
        all_triples = []
        all_entities = set()
        
        for index, row in df.iterrows():
            text = str(row[text_column])
            entities, triples = extract_entities_and_triples(text)
            
            for e, label in entities:
                all_entities.add((e, label))
            
            all_triples.extend(triples)
        
        st.session_state["extracted_entities"] = list(all_entities)
        st.session_state["extracted_triples"] = all_triples
        st.success(f"Extraction complete! Found **{len(all_entities)}** unique entities and **{len(all_triples)}** mock triples.")
        
st.markdown("---")

if "extracted_triples" in st.session_state:
    st.subheader("Extracted Results")
    
    tab_e, tab_t = st.tabs(["Entities", "Triples"])
    
    with tab_e:
        st.markdown(f"**Unique Entities Found:** {len(st.session_state['extracted_entities'])}")
        entities_df = pd.DataFrame(st.session_state['extracted_entities'], columns=["Entity/Node", "Type/Label"])
        st.dataframe(entities_df, use_container_width=True)
        
    with tab_t:
        st.markdown(f"**Mock Triples Found:** {len(st.session_state['extracted_triples'])}")
        triples_df = pd.DataFrame(st.session_state['extracted_triples'], columns=["Subject", "Predicate", "Object"])
        st.dataframe(triples_df, use_container_width=True)
        
        if st.button("Add Extracted Triples to Knowledge Graph (Simulated)", key="add_to_kg_btn"):
            st.success(f"**{len(st.session_state['extracted_triples'])}** triples successfully prepared for integration.")