import joblib
import numpy as np
import pandas as pd
import streamlit as st
import urllib.parse

st.set_page_config(page_title="AnimeXfind", layout="wide")

# -------------------- Caching Data --------------------
@st.cache_data
def load_data():
    chunks = pd.read_csv("../AnimeXfind/cleaned_data.csv", chunksize=50000, low_memory=False)
    return pd.concat(chunks, ignore_index=True)

@st.cache_resource  # <--- Use resource for large objects
def load_similarity(name):
    return joblib.load(name)

# -------------------- Load Anime Data --------------------
Data = load_data()

# Load similarity matrices only when needed
def get_sim_matrix(sim_type):
    if sim_type == "Hybrid":
        return load_similarity("../AnimeXfind/hybrid_cosine_sim.pkl")
    elif sim_type == "Tags Only":
        return load_similarity("../AnimeXfind/tag_cosine_sim.pkl")
    else:
        return load_similarity("../AnimeXfind/desc_cosine_sim.pkl")


# -------------------- Image URL Fetcher --------------------
def fetch_image_url(query):
    encoded = urllib.parse.quote_plus(query + " anime")
    return f"https://www.google.com/search?tbm=isch&q={encoded}"

# -------------------- Recommendation Engine --------------------
def get_recommendations(title, sim_matrix):
    try:
        idx = Data[Data['Name'] == title].index[0]
        sim_scores = list(enumerate(sim_matrix[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_indices = [i[0] for i in sim_scores[1:11]]
        return Data.iloc[sim_indices][['Name']]
    except Exception as e:
        st.error(f"Error during recommendation: {str(e)}")
        return pd.DataFrame(columns=['Name'])

# -------------------- UI Configuration --------------------
st.markdown("<h1 style='text-align: center;'>🌸 Anime Recommendation System 🌸</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Find your next favorite anime by similarity in tags and storylines!</p>", unsafe_allow_html=True)

# -------------------- Sidebar UI --------------------
st.sidebar.title("⚙️ Options")
selected_anime = st.sidebar.selectbox("🎞️ Select an Anime", sorted(Data['Name'].dropna().unique()))
sim_type = st.sidebar.radio("🧠 Choose Recommendation Type", ["Hybrid", "Tags Only", "Description Only"])
recommend = st.sidebar.button("🚀 Recommend")

# -------------------- Recommendation Results --------------------
if recommend:
    st.markdown(f"## 📌 Top 10 Recommendations for **{selected_anime}**")
    sim_matrix = get_sim_matrix(sim_type)
    recs = get_recommendations(selected_anime, sim_matrix)

    if recs.empty:
        st.error("😢 No recommendations found.")
    else:
        cols = st.columns(2)
        for i, row in enumerate(recs.iterrows()):
            name = row[1]['Name']
            col = cols[i % 2]
            with col:
                st.markdown(f"### 🎬 {name}")
                link = fetch_image_url(name)
                st.markdown(f"[🖼️ View Image]( {link} )", unsafe_allow_html=True)
                st.image("https://media.tenor.com/yheo1GGu3FwAAAAd/running-anime.gif", width=250)

# -------------------- Footer --------------------
st.markdown("---")
st.markdown("<center>Made with ❤️ by Heart </center>", unsafe_allow_html=True)
