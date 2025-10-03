import os
import pickle
import requests
import streamlit as st

# -----------------------------
# TMDB API Key
# -----------------------------
API_KEY = "38b5eed58f70d6d5e77493efef5bba16"  # replace with your TMDB key

# -----------------------------
# Poster caching folder
# -----------------------------
POSTER_DIR = "posters"
os.makedirs(POSTER_DIR, exist_ok=True)


# -----------------------------
# Fetch poster function
# -----------------------------
def fetch_poster(movie_id):
    """Fetch poster from TMDB or load cached one."""
    poster_file = os.path.join(POSTER_DIR, f"{movie_id}.jpg")

    if os.path.exists(poster_file):
        return poster_file

    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get("poster_path")
        if poster_path:
            full_url = "https://image.tmdb.org/t/p/w500" + poster_path
            img_data = requests.get(full_url, timeout=10).content
            with open(poster_file, "wb") as f:
                f.write(img_data)
            return poster_file
    except Exception as e:
        print(f"Error fetching poster for ID {movie_id}: {e}")

    # Fallback placeholder
    return "https://via.placeholder.com/500x750?text=No+Poster"


# -----------------------------
# Recommendation function
# -----------------------------
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    recommended_movie_names = []
    recommended_movie_posters = []

    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_names.append(movies.iloc[i[0]].title)
        recommended_movie_posters.append(fetch_poster(movie_id))

    return recommended_movie_names, recommended_movie_posters


# -----------------------------
# Streamlit App Config
# -----------------------------
st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide"
)

# -----------------------------
# Dark Mode Custom CSS
# -----------------------------
st.markdown(
    """
    <style>
    /* Backgrounds */
    .main {background-color: #0E1117; color: #FAFAFA;}
    .stApp {background-color: #0E1117;}
    /* Headers */
    h1, h4 {color: #FF4B4B;}
    /* Buttons */
    .stButton>button {background-color: #FF4B4B; color: white; border-radius: 8px;}
    /* Selectbox */
    div[data-baseweb="select"] > div {background-color: #262730; color: white;}
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Load movie data
# -----------------------------
movies = pickle.load(open("movie_list.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

# -----------------------------
# Header
# -----------------------------
st.markdown("<h1 style='text-align: center;'>🎬 Movie Recommender 🍿</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: gray;'>Discover movies similar to your favorites</h4>",
            unsafe_allow_html=True)
st.write("---")

# -----------------------------
# Movie selection
# -----------------------------
movie_list = movies["title"].values
selected_movie = st.selectbox(
    "🎥 Select a movie", movie_list,
    index=0
)

# -----------------------------
# Show Recommendations
# -----------------------------
if st.button("🔍 Show Recommendations"):
    names, posters = recommend(selected_movie)

    cols = st.columns(5, gap="large")
    for idx, col in enumerate(cols):
        with col:
            st.image(posters[idx], use_container_width=True)
            st.markdown(
                f"<p style='text-align:center; font-weight:bold; color:#FAFAFA;'>{names[idx]}</p>",
                unsafe_allow_html=True
            )