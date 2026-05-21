import pickle
import random
import requests
import streamlit as st
import firebase_admin
from pathlib import Path
from firebase_admin import auth, credentials, firestore

# basic page setup
st.set_page_config(page_title="CineLove ❤️", page_icon="❤️", layout="wide")

FIREBASE_API_KEY = "AIzaSyCo_rYNY_vArV_LBR-XWHYFAgyveBG5sr4"
TMDB_API_KEY = "8265bd1679663a7ea12ac168da84d2e8"
BASE_DIR = Path(__file__).resolve().parent

# initialize firebase only once
if not firebase_admin._apps:
    firebase_admin.initialize_app(credentials.Certificate(
        BASE_DIR / "movie-recomendation-36cbe-firebase-adminsdk-fbsvc-58163f7d4e.json"
    ))
db = firestore.client()

COUNTRY_OPTIONS = [
    "India", "United States", "United Kingdom", "Canada", "Australia", "Germany", "France",
    "Italy", "Spain", "Netherlands", "Sweden", "Norway", "Denmark", "Switzerland", "Ireland",
    "Portugal", "Belgium", "Austria", "Poland", "Czech Republic", "Hungary", "Greece",
    "Turkey", "United Arab Emirates", "Saudi Arabia", "Qatar", "Kuwait", "South Africa",
    "Nigeria", "Egypt", "Kenya", "Morocco", "Brazil", "Argentina", "Chile", "Colombia",
    "Mexico", "Japan", "South Korea", "China", "Singapore", "Malaysia", "Thailand",
    "Indonesia", "Philippines", "Vietnam", "Pakistan", "Bangladesh", "Sri Lanka", "Nepal", "New Zealand"
]
SEX_OPTIONS = ["Male", "Female", "Other", "Prefer not to say"]

CATEGORIES = {
    "🔥 Action": 28, "😂 Comedy": 35, "💀 Horror": 27, "🚀 Sci-Fi": 878,
    "💕 Romance": 10749, "🎭 Drama": 18, "🧩 Thriller": 53, "🧸 Animation": 16
}
INTEREST_CATEGORIES = {
    "🔥 Action": 28, "🗺️ Adventure": 12, "🧙 Fantasy": 14, "🚀 Sci-Fi": 878,
    "🕵️ Mystery": 9648, "🧩 Thriller": 53, "💀 Horror": 27, "😂 Comedy": 35,
    "💕 Romance": 10749, "🎭 Drama": 18, "🧸 Animation": 16, "👨‍👩‍👧‍👦 Family": 10751,
    "🧨 Crime": 80, "📜 History": 36, "⚔️ War": 10752, "🎵 Music": 10402,
    "🤠 Western": 37, "🎞️ Documentary": 99
}

# all the styling - css with animations
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');
:root {
    --bg-deep:#060d1f; --bg-card:#0d1b38; --bg-glass:rgba(13,27,56,0.75);
    --accent-blue:#3a8ef6; --accent-cyan:#38d9f5; --accent-glow:rgba(58,142,246,0.38);
    --text-main:#e8f0fe; --text-muted:#7a90b8; --border:rgba(58,142,246,0.20); --radius:16px;
}
@keyframes fadeSlideUp { from{opacity:0;transform:translateY(32px)} to{opacity:1;transform:translateY(0)} }
@keyframes shimmer { 0%{background-position:200% center} 100%{background-position:-200% center} }
@keyframes pulseGlow {
    0%,100%{box-shadow:0 0 28px rgba(58,142,246,0.30),0 0 60px rgba(56,217,245,0.10)}
    50%{box-shadow:0 0 48px rgba(58,142,246,0.55),0 0 90px rgba(56,217,245,0.22)}
}
@keyframes orbitSpin {
    from{transform:rotate(0deg) translateX(160px) rotate(0deg)}
    to{transform:rotate(360deg) translateX(160px) rotate(-360deg)}
}
@keyframes starTwinkle { 0%,100%{opacity:0.15;transform:scale(1)} 50%{opacity:0.9;transform:scale(1.5)} }
@keyframes gradientShift { 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }
@keyframes borderGlow { 0%,100%{border-color:rgba(58,142,246,0.25)} 50%{border-color:rgba(56,217,245,0.55)} }
@keyframes cardReveal { from{opacity:0;transform:translateY(40px) scale(0.96)} to{opacity:1;transform:translateY(0) scale(1)} }
@keyframes logoReveal { 0%{opacity:0;letter-spacing:0.5em;filter:blur(8px)} 100%{opacity:1;letter-spacing:normal;filter:blur(0)} }
@keyframes heartbeat { 0%,100%{transform:scale(1)} 14%{transform:scale(1.22)} 28%{transform:scale(1)} 42%{transform:scale(1.12)} }
@keyframes float { 0%,100%{transform:translateY(0px)} 50%{transform:translateY(-18px)} }
@keyframes floatB { 0%,100%{transform:translateY(0px)} 50%{transform:translateY(-22px)} }
html,body,[data-testid="stAppViewContainer"],[data-testid="stApp"] {
    background:var(--bg-deep) !important; font-family:'DM Sans',sans-serif; color:var(--text-main);
}
[data-testid="stAppViewContainer"] .block-container { padding-top:1.2rem !important; }
[data-testid="stAppViewContainer"]::before {
    content:""; position:fixed; inset:0;
    background: radial-gradient(ellipse 90% 65% at 10% 0%,rgba(58,142,246,0.22),transparent 55%),
                radial-gradient(ellipse 70% 55% at 90% 90%,rgba(56,217,245,0.16),transparent 50%);
    z-index:0; pointer-events:none; animation:gradientShift 12s ease infinite; background-size:400% 400%;
}
[data-testid="stAppViewContainer"]::after {
    content:""; position:fixed; inset:0; z-index:0; pointer-events:none;
    background:linear-gradient(transparent 50%,rgba(58,142,246,0.015) 50%); background-size:100% 4px;
}
[data-testid="stAppViewContainer"]>* { position:relative; z-index:1; }
.stApp>div:first-child::before,.stApp>div:first-child::after {
    content:""; position:fixed; border-radius:50%; pointer-events:none; z-index:0; filter:blur(80px);
}
.stApp>div:first-child::before {
    width:500px; height:500px; top:-120px; left:-120px;
    background:radial-gradient(circle,rgba(58,142,246,0.18),transparent 70%); animation:float 9s ease-in-out infinite;
}
.stApp>div:first-child::after {
    width:420px; height:420px; bottom:-100px; right:-100px;
    background:radial-gradient(circle,rgba(56,217,245,0.14),transparent 70%); animation:floatB 11s ease-in-out infinite;
}
#MainMenu,footer,header { visibility:hidden !important; }
[data-testid="stToolbar"],[data-testid="stDecoration"] { display:none !important; }
[data-testid="stSpinner"] p { display:none !important; }
[data-testid="stHeaderActionElements"],[data-testid="stHeaderActionLink"],
a.header-anchor,.stMarkdown h1 a,.stMarkdown h2 a,.stMarkdown h3 a { display:none !important; }
[data-testid="stSidebar"] { background:linear-gradient(180deg,#0a1628,#060d1f) !important; border-right:1px solid var(--border) !important; }
.hero { text-align:center; padding:1.4rem 1rem 1.2rem; }
.hero-title {
    font-family:'Outfit',sans-serif; font-weight:800; font-size:clamp(2.6rem,5vw,4.2rem); line-height:1.08;
    background:linear-gradient(135deg,#e8f0fe,var(--accent-cyan) 55%,var(--accent-blue)); background-size:200% auto;
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; margin:0 0 0.65rem;
    animation:logoReveal 1.1s cubic-bezier(0.22,1,0.36,1) both, shimmer 4s linear 1.2s infinite;
}
.hero-sub { font-size:1rem; color:var(--text-muted); font-weight:300; max-width:480px; margin:0 auto 2rem; line-height:1.65; animation:fadeSlideUp 0.9s 0.4s both; }
.glow-divider {
    height:1px; background:linear-gradient(90deg,transparent,var(--accent-blue),var(--accent-cyan),var(--accent-blue),transparent);
    background-size:200% auto; margin:0 auto 2.5rem; max-width:600px; opacity:0.6; animation:shimmer 3s linear infinite;
}
.glow-divider-auth {
    height:1px; background:linear-gradient(90deg,transparent,rgba(58,142,246,0.50),rgba(56,217,245,0.60),rgba(58,142,246,0.50),transparent);
    background-size:200% auto; margin:0.6rem auto 1.6rem; max-width:500px; animation:shimmer 3s linear infinite;
}
[data-testid="stSelectbox"] label { color:var(--text-muted) !important; font-size:0.8rem !important; letter-spacing:0.06em !important; text-transform:uppercase !important; }
[data-testid="stSelectbox"]>div>div { background:var(--bg-card) !important; border:1.5px solid var(--border) !important; border-radius:var(--radius) !important; color:var(--text-main) !important; }
[data-testid="stSelectbox"]>div>div:focus-within { border-color:var(--accent-blue) !important; box-shadow:0 0 20px var(--accent-glow) !important; }
.stButton>button {
    background:linear-gradient(135deg,var(--accent-blue),var(--accent-cyan)) !important; background-size:200% auto !important;
    color:#fff !important; font-family:'Outfit',sans-serif !important; font-weight:600 !important;
    border:none !important; border-radius:12px !important; padding:0.75rem 2.5rem !important;
    width:100%; box-shadow:0 6px 28px rgba(58,142,246,0.40) !important;
    transition:transform 0.22s,box-shadow 0.22s !important;
    text-shadow:0 1px 2px rgba(0,0,0,0.35) !important; letter-spacing:0.02em !important;
}
.stButton>button:hover { transform:translateY(-3px) !important; box-shadow:0 14px 40px rgba(58,142,246,0.62) !important; }
.stButton>button:active { transform:translateY(0px) !important; }
.section-label {
    font-family:'Outfit',sans-serif; font-weight:700; font-size:1.3rem; color:var(--text-main);
    margin:2.5rem 0 1.4rem; display:flex; align-items:center; gap:0.6rem;
}
.section-label::after { content:""; flex:1; height:1px; background:var(--border); }
.movie-card {
    background:var(--bg-glass); border:1px solid var(--border); border-radius:var(--radius);
    overflow:hidden; backdrop-filter:blur(12px);
    transition:transform 0.28s cubic-bezier(0.34,1.56,0.64,1),box-shadow 0.28s,border-color 0.28s; height:100%;
}
.movie-card:hover { transform:translateY(-10px) scale(1.02); box-shadow:0 24px 60px rgba(58,142,246,0.36); border-color:var(--accent-cyan); }
.movie-card img { width:100%; display:block; aspect-ratio:2/3; object-fit:cover; }
.movie-card-body { padding:0.85rem 0.9rem 1rem; text-align:center; }
.rank-pill {
    display:inline-block; background:linear-gradient(135deg,var(--accent-blue),var(--accent-cyan));
    color:#fff; font-family:'Outfit',sans-serif; font-weight:700; font-size:0.68rem;
    padding:0.18rem 0.6rem; border-radius:99px; margin-bottom:0.4rem;
}
.movie-title { font-family:'Outfit',sans-serif; font-weight:600; font-size:0.9rem; color:var(--text-main); line-height:1.35; }
.footer { text-align:center; padding:3.5rem 1rem 2rem; color:var(--text-muted); font-size:0.76rem; }
.footer span { color:var(--accent-cyan); }
.auth-logo-anim { text-align:center; padding:1.8rem 1rem 0.5rem; animation:fadeSlideUp 0.9s both; }
.auth-logo-title {
    font-family:'Outfit',sans-serif; font-weight:800; font-size:clamp(2.4rem,5vw,3.8rem);
    background:linear-gradient(135deg,#e8f0fe,#38d9f5 40%,#3a8ef6 70%,#38d9f5); background-size:300% auto;
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
    display:inline-block; animation:logoReveal 1.1s cubic-bezier(0.22,1,0.36,1) both, shimmer 5s linear 1.2s infinite;
}
.auth-logo-heart { display:inline-block; animation:heartbeat 2.2s ease-in-out 1.5s infinite; -webkit-text-fill-color:#ff4d6d !important; }
.auth-logo-sub { font-size:1rem; color:var(--text-muted); font-weight:300; max-width:460px; margin:0 auto 0.5rem; line-height:1.65; animation:fadeSlideUp 1s 0.5s both; }
.auth-card {
    background:var(--bg-glass); border:1px solid var(--border); border-radius:var(--radius);
    padding:1.8rem 1.5rem 1.4rem; backdrop-filter:blur(18px); position:relative; overflow:hidden;
    animation:cardReveal 0.85s 0.3s cubic-bezier(0.22,1,0.36,1) both, borderGlow 3.5s 1s ease-in-out infinite;
}
.auth-card::before {
    content:""; position:absolute; top:-60%; left:-60%; width:220%; height:220%;
    background:conic-gradient(from 0deg at 50% 50%,transparent 0deg,rgba(58,142,246,0.06) 60deg,rgba(56,217,245,0.09) 120deg,
        transparent 180deg,rgba(58,142,246,0.06) 240deg,rgba(56,217,245,0.09) 300deg,transparent 360deg);
    animation:orbitSpin 18s linear infinite; pointer-events:none;
}
.auth-head { font-family:'Outfit',sans-serif; font-size:1.22rem; font-weight:700; color:#f3f8ff; margin:0 0 0.25rem; position:relative; z-index:1; }
.auth-sub { color:#a8bcdd; font-size:0.92rem; line-height:1.7; margin:0 0 1rem; position:relative; z-index:1; }
.auth-feature { display:flex; align-items:flex-start; gap:0.7rem; margin:0.65rem 0; position:relative; z-index:1; }
.auth-feature-icon {
    flex-shrink:0; width:32px; height:32px; border-radius:8px; font-size:0.95rem;
    background:linear-gradient(135deg,rgba(58,142,246,0.20),rgba(56,217,245,0.20));
    border:1px solid rgba(58,142,246,0.30); display:flex; align-items:center; justify-content:center;
}
.auth-feature-text { font-size:0.87rem; color:#a8bcdd; line-height:1.5; padding-top:0.3rem; }
.auth-feature-title { font-weight:600; color:var(--text-main); font-size:0.9rem; }
.login-panel-head { animation:fadeSlideUp 0.7s 0.7s both; }
.auth-form-wrap { animation:fadeSlideUp 0.8s 0.9s both; }
[data-testid="stTabs"] { animation:cardReveal 0.9s 0.5s cubic-bezier(0.22,1,0.36,1) both; }
[data-testid="stTabs"]>div:first-child+div {
    background:var(--bg-glass) !important; border:1px solid var(--border) !important;
    border-radius:var(--radius) !important; padding:1.5rem 1.5rem 1.8rem !important;
    backdrop-filter:blur(18px) !important;
    box-shadow:0 8px 48px rgba(0,0,0,0.40),inset 0 1px 0 rgba(255,255,255,0.04) !important;
    animation:pulseGlow 4s ease-in-out infinite;
}
[data-testid="stTabs"] button { font-family:'Outfit',sans-serif !important; font-weight:600 !important; color:#afc1e0 !important; }
[data-testid="stTabs"] button[aria-selected="true"] { color:#38d9f5 !important; border-bottom:2px solid #38d9f5 !important; }
[data-testid="stTextInput"] label { color:var(--text-muted) !important; font-size:0.8rem !important; letter-spacing:0.06em !important; text-transform:uppercase !important; }
[data-testid="stTextInput"]>div>div>input {
    background:rgba(6,13,31,0.70) !important; border:1.5px solid rgba(58,142,246,0.25) !important;
    border-radius:12px !important; color:var(--text-main) !important; font-size:0.95rem !important;
    transition:border-color 0.3s,box-shadow 0.3s !important;
}
[data-testid="stTextInput"]>div>div>input:focus { border-color:var(--accent-cyan) !important; box-shadow:0 0 0 3px rgba(56,217,245,0.15),0 0 22px rgba(58,142,246,0.30) !important; }
[data-testid="stTextInput"]>div>div>input::placeholder { color:rgba(122,144,184,0.55) !important; }
.star-field { position:fixed; inset:0; z-index:0; pointer-events:none; overflow:hidden; }
.star { position:absolute; width:2px; height:2px; border-radius:50%; background:#fff; animation:starTwinkle var(--dur,3s) var(--delay,0s) ease-in-out infinite; }
.orbit-ring { position:fixed; border-radius:50%; border:1px solid rgba(58,142,246,0.08); pointer-events:none; z-index:0; }
.orbit-dot { position:absolute; width:8px; height:8px; border-radius:50%; background:var(--accent-cyan); box-shadow:0 0 10px var(--accent-cyan); top:-4px; left:50%; transform:translateX(-50%); }
.orbit-ring-1 { width:340px; height:340px; top:calc(50% - 170px); right:-120px; animation:float 14s ease-in-out infinite; }
.orbit-ring-2 { width:520px; height:520px; bottom:-200px; left:-180px; border-color:rgba(56,217,245,0.06); animation:floatB 18s ease-in-out infinite; }
</style>
<div class="star-field" id="starField"></div>
<div class="orbit-ring orbit-ring-1"><div class="orbit-dot"></div></div>
<div class="orbit-ring orbit-ring-2"></div>
<script>
(function(){
    var sf = document.getElementById('starField');
    if (!sf) return;
    for (var i = 0; i < 60; i++) {
        var s = document.createElement('div');
        s.className = 'star';
        var size = Math.random() * 2.5 + 0.5;
        s.style.cssText = 'width:'+size+'px;height:'+size+'px;top:'+(Math.random()*100)+'%;left:'+(Math.random()*100)+'%;--dur:'+(2+Math.random()*5)+'s;--delay:'+(Math.random()*6)+'s;opacity:'+(0.05+Math.random()*0.5);
        sf.appendChild(s);
    }
})();
</script>""", unsafe_allow_html=True)


# load ml model files
@st.cache_resource(show_spinner=False)
def load_data():
    movies = pickle.load(open('movie_list.pkl', 'rb'))
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    return movies, similarity


@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):
    try:
        data = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US", timeout=5).json()
        path = data.get('poster_path', '')
        if path:
            return f"https://image.tmdb.org/t/p/w500/{path}"
    except Exception:
        pass
    return "https://via.placeholder.com/500x750/0d1b38/3a8ef6?text=No+Poster"


@st.cache_data(ttl=86400, show_spinner=False)
def fetch_genre_pool(genre_id):
    pool = []
    for page in range(1, 4):
        try:
            res = requests.get(
                f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&with_genres={genre_id}&sort_by=vote_count.desc&vote_average.gte=7&page={page}",
                timeout=8
            ).json()
            for m in res.get("results", []):
                if m.get("poster_path") and m.get("title"):
                    pool.append({"title": m["title"], "poster": f"https://image.tmdb.org/t/p/w500/{m['poster_path']}"})
        except Exception:
            pass
    return pool


# content based filtering recommendation
def recommend(movie):
    movies, similarity = load_data()
    idx = movies[movies['title'] == movie].index[0]
    distances = sorted(enumerate(similarity[idx]), reverse=True, key=lambda x: x[1])
    names, posters = [], []
    for i in distances[1:6]:
        names.append(movies.iloc[i[0]].title)
        posters.append(fetch_poster(movies.iloc[i[0]].movie_id))
    return names, posters


# firebase rest api helpers
def firebase_request(action, payload):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:{action}?key={FIREBASE_API_KEY}"
    res = requests.post(url, json=payload, timeout=20)
    data = res.json()
    if res.status_code != 200:
        raise ValueError(data.get("error", {}).get("message", "Auth failed").replace("_", " ").title())
    return data

def firebase_login(email, password):
    return firebase_request("signInWithPassword", {"email": email, "password": password, "returnSecureToken": True})

def firebase_register(name, email, password):
    c = firebase_request("signUp", {"email": email, "password": password, "returnSecureToken": True})
    firebase_request("update", {"idToken": c["idToken"], "displayName": name, "returnSecureToken": True})
    return c

def firebase_auth_user_exists(email):
    try:
        auth.get_user_by_email(email.strip().lower())
        return True
    except auth.UserNotFoundError:
        return False

def firebase_send_password_reset(email, url="http://localhost:8501"):
    return firebase_request("sendOobCode", {"requestType": "PASSWORD_RESET", "email": email.strip().lower(), "continueUrl": url})

def firebase_password_reset_link(email, url="http://localhost:8501"):
    return auth.generate_password_reset_link(email.strip().lower(), auth.ActionCodeSettings(url=url, handle_code_in_app=False))


# firestore profile helpers
def load_profile(email):
    if not email:
        return {}
    doc = db.collection("users").document(email.lower()).get()
    return doc.to_dict() if doc.exists else {}

def profile_is_complete(profile):
    return bool(profile) and profile.get("age") is not None and profile.get("region") and profile.get("sex")

def save_profile(email, age, region, sex, interested_genres=None, ui_prefs=None):
    key = email.lower()
    doc = db.collection("users").document(key).get()
    current = doc.to_dict() if doc.exists else {}
    updated = {
        **current,
        "age": age, "region": region, "sex": sex,
        "interested_genres": list(interested_genres or current.get("interested_genres", [])),
        "ui_prefs": dict(ui_prefs or current.get("ui_prefs", {})),
    }
    db.collection("users").document(key).set(updated)
    return updated


# helper to render a row of 5 movie cards
def render_movie_row(label, movie_list):
    if not movie_list:
        return
    st.markdown(f'<div class="section-label">{label}</div>', unsafe_allow_html=True)
    cols = st.columns(5)
    for i, col in enumerate(cols):
        if i < len(movie_list):
            with col:
                st.markdown(f"""
                <div class="movie-card">
                    <img src="{movie_list[i]['poster']}" alt="{movie_list[i]['title']}"/>
                    <div class="movie-card-body">
                        <div class="movie-title">{movie_list[i]['title']}</div>
                    </div>
                </div>""", unsafe_allow_html=True)


def render_browse_section():
    st.markdown('<div class="glow-divider" style="margin-top:3rem;"></div>', unsafe_allow_html=True)
    st.markdown("""<div style="text-align:center;margin-bottom:2rem;">
        <h2 style="font-family:'Outfit',sans-serif;font-weight:800;font-size:1.6rem;
            background:linear-gradient(135deg,#e8f0fe,#38d9f5);-webkit-background-clip:text;
            -webkit-text-fill-color:transparent;background-clip:text;margin:0 0 0.4rem;">Browse by Category</h2>
        <p style="color:#7a90b8;font-size:0.9rem;margin:0;">Fresh picks every visit</p>
    </div>""", unsafe_allow_html=True)
    for label, genre_id in CATEGORIES.items():
        pool = fetch_genre_pool(genre_id)
        render_movie_row(label, random.sample(pool, min(5, len(pool))) if pool else [])


def render_user_nav(is_home):
    _, nav_col = st.columns([6.8, 1.2])
    with nav_col:
        with st.popover(st.session_state.get("user_name", "User"), use_container_width=True):
            st.markdown(f"**{st.session_state.get('user_name', 'User')}**")
            st.caption(st.session_state.get("user_email", ""))
            if st.button("Manage Account", key="manage_account_btn", use_container_width=True):
                st.session_state.active_page = "account"
                st.session_state.sync_account_interests = True
                st.rerun()
            if st.button("Logout", key="logout_btn_menu"):
                for k in ["is_authenticated", "user_name", "user_email", "id_token", "user_profile", "show_profile_popup"]:
                    st.session_state[k] = False if k == "is_authenticated" else ({} if k == "user_profile" else "")
                st.session_state.active_page = "home"
                st.rerun()
        if not is_home:
            st.markdown("<div style='height:0.45rem;'></div>", unsafe_allow_html=True)
            if st.button("Back to Home", key="back_home_btn", use_container_width=True):
                st.session_state.active_page = "home"
                st.rerun()


@st.dialog("Complete Your Profile")
def profile_popup():
    st.write("Please fill these details to complete your account setup.")
    age = st.number_input("Age", min_value=13, max_value=100, value=18, step=1)
    region = st.selectbox("Country", COUNTRY_OPTIONS, index=COUNTRY_OPTIONS.index("India"))
    sex = st.selectbox("Sex", SEX_OPTIONS)
    if st.button("Save Profile", use_container_width=True):
        try:
            st.session_state.user_profile = save_profile(st.session_state.user_email, int(age), region, sex)
            st.session_state.show_profile_popup = False
            st.toast("Profile saved successfully.", icon="✅")
            st.rerun()
        except Exception as err:
            st.error(f"Could not save profile to Firestore: {err}")


def render_auth_page():
    st.markdown("""
    <div class="auth-logo-anim">
        <div class="auth-logo-title">CineLove <span class="auth-logo-heart">❤️</span></div>
        <p class="auth-logo-sub">Sign in to save watchlists, sync likes, and get smarter recommendations made for your movie taste.</p>
    </div>
    <div class="glow-divider-auth"></div>""", unsafe_allow_html=True)

    left, right = st.columns([1.15, 1])
    with left:
        st.markdown("""<div class="auth-card">
            <h3 class="auth-head">Why Create an Account?</h3>
            <p class="auth-sub">Build your personal cinema profile and let CineLove shape a discovery feed that gets you.</p>
            <div class="auth-feature"><div class="auth-feature-icon">🎬</div><div class="auth-feature-text"><div class="auth-feature-title">Personal Recommendations</div>Content-based filtering tuned to your taste across 5,000+ titles.</div></div>
            <div class="auth-feature"><div class="auth-feature-icon">🔖</div><div class="auth-feature-text"><div class="auth-feature-title">Save &amp; Sync</div>Keep your watchlist and picks accessible across every device.</div></div>
            <div class="auth-feature"><div class="auth-feature-icon">🌍</div><div class="auth-feature-text"><div class="auth-feature-title">Region-Aware Picks</div>Trending titles filtered by your country and preferences.</div></div>
            <div class="auth-feature"><div class="auth-feature-icon">⚙️</div><div class="auth-feature-text"><div class="auth-feature-title">Full Control</div>Adjust strictness, genre interests, and mature-content settings anytime.</div></div>
        </div>""", unsafe_allow_html=True)

    with right:
        tabs = st.tabs(["Login", "Register"])
        with tabs[0]:
            st.markdown('<div class="login-panel-head"><h3 class="auth-head">Welcome Back</h3><p class="auth-sub">Lights, camera, continue watching.</p></div><div class="auth-form-wrap">', unsafe_allow_html=True)
            email = st.text_input("Email", key="login_email", placeholder="you@example.com")
            password = st.text_input("Password", key="login_password", type="password", placeholder="••••••••")
            st.markdown("</div>", unsafe_allow_html=True)
            if st.button("Login to CineLove ❤️", key="login_btn", use_container_width=True):
                if not email or not password:
                    st.warning("Please enter email and password.")
                else:
                    try:
                        user = firebase_login(email.strip(), password)
                        st.session_state.is_authenticated = True
                        st.session_state.user_email = email.strip().lower()
                        st.session_state.user_name = user.get("displayName") or email.split("@")[0].title()
                        st.session_state.id_token = user.get("idToken", "")
                        st.session_state.user_profile = load_profile(email.strip().lower())
                        st.session_state.show_profile_popup = not profile_is_complete(st.session_state.user_profile)
                        st.session_state.active_page = "home"
                        st.rerun()
                    except ValueError as err:
                        msg = str(err)
                        if "invalid login credentials" in msg.lower() or "invalid password" in msg.lower():
                            msg = "Invalid credentials / password."
                        st.error(msg)

        with tabs[1]:
            st.markdown('<div class="login-panel-head"><h3 class="auth-head">Create Your Account</h3><p class="auth-sub">Join CineLove ❤️ and start building your personal reel.</p></div><div class="auth-form-wrap">', unsafe_allow_html=True)
            name = st.text_input("Full Name", key="register_name", placeholder="Your Name")
            reg_email = st.text_input("Email Address", key="register_email", placeholder="you@example.com")
            reg_pass = st.text_input("Password", key="register_password", type="password", placeholder="At least 6 characters")
            st.markdown("</div>", unsafe_allow_html=True)
            if st.button("Register on CineLove ❤️", key="register_btn", use_container_width=True):
                if not name or not reg_email or len(reg_pass) < 6:
                    st.warning("Enter name, email and password (minimum 6 characters).")
                else:
                    try:
                        created = firebase_register(name.strip(), reg_email.strip(), reg_pass)
                        st.session_state.is_authenticated = True
                        st.session_state.user_email = reg_email.strip().lower()
                        st.session_state.user_name = name.strip()
                        st.session_state.id_token = created.get("idToken", "")
                        st.session_state.user_profile = {}
                        st.session_state.show_profile_popup = True
                        st.session_state.active_page = "home"
                        st.rerun()
                    except ValueError as err:
                        st.error(f"Registration failed: {err}")


def render_home_page():
    movies, _ = load_data()
    render_user_nav(is_home=True)
    st.markdown("""<div class="hero">
        <h1 class="hero-title">CineLove ❤️</h1>
        <p class="hero-sub">Discover your next favourite film - powered by content-based filtering on 5,000+ movies.</p>
    </div><div class="glow-divider"></div>""", unsafe_allow_html=True)

    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        selected_movie = st.selectbox("🎬  Pick a movie to get started", movies['title'].values)
        show = st.button("✦  Show Recommendations")

    if show:
        with st.spinner(" "):
            names, posters = recommend(selected_movie)
        st.markdown('<div class="section-label">🍿 &nbsp; Top 5 Picks For You</div>', unsafe_allow_html=True)
        for i, col in enumerate(st.columns(5)):
            with col:
                st.markdown(f"""<div class="movie-card">
                    <img src="{posters[i]}" alt="{names[i]}"/>
                    <div class="movie-card-body">
                        <div class="rank-pill">#{i+1}</div>
                        <div class="movie-title">{names[i]}</div>
                    </div></div>""", unsafe_allow_html=True)

    render_browse_section()


def render_account_page():
    email = st.session_state.get("user_email", "")
    if email:
        try:
            st.session_state.user_profile = load_profile(email)
        except Exception as err:
            st.error(f"Could not load profile from Firestore: {err}")
    profile = st.session_state.get("user_profile", {})

    render_user_nav(is_home=False)
    st.markdown("""<div class="hero">
        <h1 class="hero-title">Manage Account</h1>
        <p class="hero-sub">Keep your profile, preferences, and movie interests up to date. This helps CineLove ❤️ tailor recommendations, category browsing, and your personal discovery feed.</p>
    </div><div class="glow-divider"></div>""", unsafe_allow_html=True)

    st.markdown('<h3 class="auth-head">Account Overview</h3>', unsafe_allow_html=True)

    tabs = st.tabs(["Profile", "Interested", "Security & Privacy"])

    with tabs[0]:
        st.markdown('<div class="section-label">👤 &nbsp; Profile Details</div>', unsafe_allow_html=True)
        st.caption("These basics help personalize results (age-relevant picks, country availability, and demographic signals).")
        age = st.number_input("Age", min_value=13, max_value=100, value=int(profile.get("age", 18) or 18), step=1,
                              help="Used only to improve relevance.")
        country_index = COUNTRY_OPTIONS.index(profile.get("region", "India")) if profile.get("region") in COUNTRY_OPTIONS else 0
        region = st.selectbox("Country", COUNTRY_OPTIONS, index=country_index,
                              help="Some content availability and trends differ by country.")
        sex_index = SEX_OPTIONS.index(profile.get("sex", "Prefer not to say")) if profile.get("sex") in SEX_OPTIONS else 3
        sex = st.selectbox("Sex", SEX_OPTIONS, index=sex_index,
                           help="Optional. Helps diversify recommendations.")
        st.markdown('<div class="glow-divider" style="margin-top:1.8rem;"></div>', unsafe_allow_html=True)
        st.markdown('<h3 class="auth-head">Save Changes</h3>', unsafe_allow_html=True)
        st.caption("We'll store your updates and use them across the app while you're signed in.")
        if st.button("Update Account", key="update_account_profile", use_container_width=True):
            if not email:
                st.warning("You must be signed in to save account changes.")
            else:
                try:
                    saved_interests = st.session_state.get("account_interested_genres", profile.get("interested_genres", []))
                    updated = save_profile(email, int(age), region, sex,
                                           interested_genres=saved_interests,
                                           ui_prefs=profile.get("ui_prefs", {}))
                    st.session_state.user_profile = updated
                    st.toast("Account updated successfully.", icon="✅")
                    st.success("Saved. Your updated preferences will shape browsing and recommendations.")
                except Exception as err:
                    st.error(f"Could not save account to Firestore: {err}")

    with tabs[1]:
        st.markdown('<div class="section-label">⭐ &nbsp; Interested</div>', unsafe_allow_html=True)
        st.caption("Pick genres you're interested in. We'll use this to shape browsing rows and nudge recommendations toward your taste.")
        interest_labels = list(INTEREST_CATEGORIES.keys())
        if "account_interested_genres" not in st.session_state or st.session_state.pop("sync_account_interests", False):
            st.session_state.account_interested_genres = [g for g in profile.get("interested_genres", []) if g in interest_labels]
        selected_interests = st.multiselect("Interested categories", options=interest_labels,
                                            key="account_interested_genres", help="Select multiple. You can change this anytime.")
        preview = st.toggle("Show preview picks for selected genres", value=False)
        if preview and selected_interests:
            for label in selected_interests[:6]:
                genre_id = INTEREST_CATEGORIES.get(label)
                if genre_id:
                    pool = fetch_genre_pool(genre_id)
                    render_movie_row(f"{label} — quick picks", random.sample(pool, min(5, len(pool))) if pool else [])
        elif preview:
            st.info("Select at least one genre to preview picks.")
        st.markdown('<div class="glow-divider" style="margin-top:1.8rem;"></div>', unsafe_allow_html=True)
        st.markdown('<h3 class="auth-head">Save Changes</h3>', unsafe_allow_html=True)
        st.caption("We'll store your updates and use them across the app while you're signed in.")
        if st.button("Update Account", key="update_account_interested", use_container_width=True):
            if not email:
                st.warning("You must be signed in to save account changes.")
            else:
                try:
                    saved_interests = st.session_state.get("account_interested_genres", profile.get("interested_genres", []))
                    updated = save_profile(email, int(age), region, sex,
                                           interested_genres=saved_interests,
                                           ui_prefs=profile.get("ui_prefs", {}))
                    st.session_state.user_profile = updated
                    st.toast("Account updated successfully.", icon="✅")
                    st.success("Saved. Your updated preferences will shape browsing and recommendations.")
                except Exception as err:
                    st.error(f"Could not save account to Firestore: {err}")

    with tabs[2]:
        st.markdown('<div class="section-label">🔒 &nbsp; Security & Privacy</div>', unsafe_allow_html=True)
        st.caption("Your login is handled by Firebase Authentication. Profile preferences are stored in Firestore.")
        st.info("Production tip: in a real deployment, preferences should live in a secured database per-user. For this PBL build, we use Firestore for cloud sync.")
        st.write("If you need to change your password:")
        st.write("- Use the button below to send a Firebase password reset email to your account.")
        st.write("- If you are using a shared device, always log out after use.")
        if st.button("Send password reset email", use_container_width=True):
            if not email:
                st.warning("You must be signed in to request a password reset.")
            elif not firebase_auth_user_exists(email):
                st.error("No Firebase login exists for this email. Password reset only works for accounts created via Login/Register here.")
            else:
                try:
                    firebase_send_password_reset(email)
                    reset_link = firebase_password_reset_link(email)
                    st.session_state.password_reset_link = reset_link
                    st.success(f"Reset request submitted for **{email}**. Check your inbox and spam folder.")
                except ValueError as err:
                    st.error(str(err))
                except Exception as err:
                    st.error(f"Could not send password reset: {err}")
        if st.session_state.get("password_reset_link"):
            with st.expander("Didn't get the email? Use this reset link"):
                st.caption("Firebase may block or delay emails on free projects. This one-time link works the same as the email button.")
                st.markdown(st.session_state.password_reset_link)
                st.link_button("Open reset page", st.session_state.password_reset_link)


# session state setup
for key, default in [
    ("is_authenticated", False), ("user_name", ""), ("user_email", ""),
    ("id_token", ""), ("user_profile", {}), ("show_profile_popup", False),
    ("active_page", "home"), ("password_reset_link", ""),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# main router
if st.session_state.is_authenticated:
    if st.session_state.show_profile_popup and st.session_state.user_email:
        profile_popup()
    if st.session_state.active_page == "account":
        render_account_page()
    else:
        render_home_page()
else:
    render_auth_page()

st.markdown('<div class="footer">Crafted with <span style="color:#ff4d6d;">cine love ❤️</span> · CineLove ❤️</div>', unsafe_allow_html=True)