"""EKATRIT - Community Giving Platform Prototype
Run:  pip install streamlit pandas plotly
      streamlit run app.py
Prototype only: no real payments, verification or financial reporting.
"""
import hashlib, html, uuid
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

DATA = Path("ekatrit_data")
CATEGORIES = ["Education", "Health", "Food & Nutrition", "Environment", "Livelihood", "Disaster Relief"]
SCHEMA = {
    "users": ["user_id", "name", "email", "city", "pw_hash", "salt"],
    "campaigns": ["campaign_id", "title", "category", "organiser", "city", "description", "goal", "raised", "donors", "status", "deadline", "owner_email"],
    "donations": ["donation_id", "email", "campaign_id", "amount", "points_earned", "donated_at"],
    "advertisements": ["ad_id", "campaign_id", "headline", "description", "placement", "status"],
}

# ---------------------------------------------------------------- helpers
def safe(x):
    return html.escape(str(x if x is not None else ""))

def money(x):
    try: return f"₹{float(x):,.0f}"
    except Exception: return "₹0"

def progress(raised, goal):
    try: return int(min(100, round(float(raised) / float(goal) * 100))) if float(goal) > 0 else 0
    except Exception: return 0

def load_data(name):
    p = DATA / f"{name}.csv"
    if not p.exists(): return pd.DataFrame(columns=SCHEMA[name])
    return pd.read_csv(p, dtype=str, keep_default_na=False)

def save_data(name, df):
    DATA.mkdir(exist_ok=True)
    df.to_csv(DATA / f"{name}.csv", index=False)

def initialise_data():
    DATA.mkdir(exist_ok=True)
    if (DATA / "campaigns.csv").exists(): return
    soon = lambda d: (date.today() + timedelta(days=d)).isoformat()
    seed = [
        ("Learning kits for 200 village students", "Education", "Utkal Shiksha Sathi", "Bhubaneswar", "Notebooks, geometry boxes and school bags for children in government primary schools.", 120000, 78500, 64, "Active", soon(40)),
        ("Mobile health camp for coastal hamlets", "Health", "Sagar Seva Trust", "Puri", "Monthly check-ups, basic medicines and referral support for fishing communities.", 250000, 164000, 112, "Active", soon(55)),
        ("Community kitchen for daily-wage families", "Food & Nutrition", "Anna Daan Collective", "Cuttack", "Hot, nutritious meals served five days a week near the central market.", 90000, 91200, 143, "Completed", soon(-5)),
        ("10,000 native saplings for Chilika's edge", "Environment", "Green Odisha Youth", "Khordha", "Mangrove and native tree plantation with local volunteers and a 12-month care plan.", 150000, 52000, 41, "Active", soon(70)),
        ("Sewing units for women artisans", "Livelihood", "Nari Shakti Samavaya", "Sambalpur", "Machines and training to help 25 women start home-based tailoring work.", 180000, 97500, 58, "Active", soon(35)),
        ("Flood-season emergency supply stock", "Disaster Relief", "Jan Raksha Mandal", "Balasore", "Pre-positioned tarpaulins, water purifiers and dry rations ahead of the monsoon.", 300000, 0, 0, "Pending Review", soon(90)),
    ]
    rows = [[f"C{i+1:03d}", *s[:3], s[3], s[4], s[5], s[6], s[7], s[8], s[9], "seed@ekatrit.demo"] for i, s in enumerate(seed)]
    save_data("campaigns", pd.DataFrame(rows, columns=SCHEMA["campaigns"]))
    save_data("users", pd.DataFrame(columns=SCHEMA["users"]))
    save_data("donations", pd.DataFrame(columns=SCHEMA["donations"]))
    ads = [("A001", "C001", "Help a child start the school year ready", "Fund a complete learning kit.", "Homepage feature", "Active"),
           ("A002", "C002", "Bring a doctor to the shoreline", "Support the next health camp.", "Discover spotlight", "Active"),
           ("A003", "C004", "Plant a future for Chilika", "Every ₹15 plants one sapling.", "Category feature", "Paused")]
    save_data("advertisements", pd.DataFrame(ads, columns=SCHEMA["advertisements"]))

# ---------------------------------------------------------------- styling
def add_styles():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');
:root{--ink:#10233F;--ink2:#1B3A63;--teal:#1F8A80;--teal-l:#E3F3F1;--gold:#E8A93A;--bg:#F4F6FA;--line:#E1E6EE;--mute:#667489;--card:#fff}
html,body,[class*="css"],.stApp{font-family:'DM Sans',sans-serif;color:var(--ink)}
.stApp{background:var(--bg)}
.block-container{max-width:1180px;padding:2rem 2rem 3rem}
#MainMenu,footer,header[data-testid="stHeader"]{visibility:hidden}
h1,h2,h3,.brand{font-family:'Plus Jakarta Sans',sans-serif;letter-spacing:-.02em}
section[data-testid="stSidebar"]{background:var(--ink);border-right:0}
section[data-testid="stSidebar"] *{color:#DCE4F0}
section[data-testid="stSidebar"] hr{border-color:rgba(255,255,255,.12)}
section[data-testid="stSidebar"] .stRadio label{padding:.45rem .6rem;border-radius:8px;width:100%}
section[data-testid="stSidebar"] .stRadio label:hover{background:rgba(255,255,255,.07)}
.brand{font-size:28px;font-weight:800;color:#fff!important}.brand span{color:var(--gold)}
.side-note{font-size:12px;line-height:1.6;color:#9FB0C8!important}
.page-title{font-family:'Plus Jakarta Sans';font-size:32px;font-weight:800;margin:0 0 4px}
.page-sub{color:var(--mute);margin-bottom:22px;font-size:15px}
.hero{background:linear-gradient(120deg,var(--ink) 0%,var(--ink2) 60%,#1F6E78 100%);color:#fff;border-radius:20px;padding:44px 48px;margin-bottom:26px;position:relative;overflow:hidden}
.hero:after{content:"";position:absolute;right:-60px;top:-60px;width:260px;height:260px;border-radius:50%;border:38px solid rgba(232,169,58,.18)}
.hero h1{font-size:40px;line-height:1.12;margin:6px 0 14px;color:#fff}
.hero p{max-width:560px;color:#C9D6E8;font-size:16px;line-height:1.65}
.kicker{font-size:12px;font-weight:700;color:var(--gold);letter-spacing:.08em}
.slogan{display:inline-block;margin-top:14px;padding:6px 14px;border-radius:99px;background:rgba(255,255,255,.12);font-size:13px;font-weight:600}
.metric{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--teal);border-radius:14px;padding:18px 20px}
.metric .v{font-family:'Plus Jakarta Sans';font-size:28px;font-weight:800}
.metric .l{font-size:13px;font-weight:600;color:var(--ink2)}.metric .n{font-size:12px;color:var(--mute)}
.section-title{font-family:'Plus Jakarta Sans';font-size:20px;font-weight:700;margin:30px 0 4px}
.section-sub{color:var(--mute);font-size:14px;margin-bottom:14px}
.campaign,.insight,.panel{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:20px 22px;margin-bottom:14px;box-shadow:0 1px 2px rgba(16,35,63,.04)}
.campaign h3,.insight h3{font-size:17px;margin:8px 0 6px}
.campaign p,.insight p{color:var(--mute);font-size:14px;line-height:1.6;margin:4px 0}
.insight{border-left:4px solid var(--gold)}.panel{background:var(--teal-l);border-color:#BFE3DE}
.tag{display:inline-block;font-size:11px;font-weight:700;color:var(--teal);background:var(--teal-l);padding:3px 10px;border-radius:99px}
.tag.gold{color:#8A5B07;background:#FCEFD2}
.bar{height:8px;background:#E8ECF3;border-radius:99px;overflow:hidden;margin:12px 0 6px}
.bar>div{height:100%;background:linear-gradient(90deg,var(--teal),#35B0A3);border-radius:99px}
.meta{display:flex;justify-content:space-between;font-size:13px;color:var(--mute)}.meta b{color:var(--ink)}
.stButton>button,.stFormSubmitButton>button{background:var(--ink);color:#fff;border:0;border-radius:10px;font-weight:600;padding:.55rem 1.2rem}
.stButton>button:hover,.stFormSubmitButton>button:hover{background:var(--teal);color:#fff}
.stButton>button:focus-visible,input:focus-visible{outline:3px solid var(--gold)!important}
div[data-testid="stForm"]{background:#fff;border:1px solid var(--line);border-radius:16px;padding:22px}
.stTabs [data-baseweb="tab"]{font-weight:600}
@media(max-width:760px){.block-container{padding:1rem}.hero{padding:28px 22px}.hero h1{font-size:28px}}

/* ---- contrast guard: force readable text on every surface ---- */
:root{color-scheme:light}
[data-testid="stMain"],[data-testid="stMain"] p,[data-testid="stMain"] li,[data-testid="stMain"] label,
[data-testid="stMain"] [data-testid="stWidgetLabel"] p,[data-testid="stMain"] [data-testid="stCaptionContainer"],
[data-testid="stMain"] summary,[data-testid="stMain"] .stTabs [data-baseweb="tab"]{color:var(--ink)!important}
[data-testid="stMain"] [data-testid="stCaptionContainer"]{color:var(--mute)!important}
[data-testid="stMain"] .campaign h3,[data-testid="stMain"] .insight b,[data-testid="stMain"] .insight h3{color:var(--ink)!important}
[data-testid="stMain"] .campaign p,[data-testid="stMain"] .insight p{color:var(--mute)!important}
[data-testid="stMain"] .tag{color:var(--teal)!important}[data-testid="stMain"] .tag.gold{color:#8A5B07!important}
[data-testid="stMain"] .hero h1,[data-testid="stMain"] .hero .slogan{color:#fff!important}
[data-testid="stMain"] .hero p{color:#D5E0EF!important}[data-testid="stMain"] .hero .kicker{color:var(--gold)!important}
[data-testid="stMain"] .metric .v{color:var(--ink)!important}[data-testid="stMain"] .metric .l{color:var(--ink2)!important}
[data-testid="stMain"] .metric .n,[data-testid="stMain"] .meta{color:var(--mute)!important}[data-testid="stMain"] .meta b{color:var(--ink)!important}
input,textarea,[data-baseweb="input"],[data-baseweb="select"]>div,[data-baseweb="textarea"]{background:#fff!important;color:var(--ink)!important;-webkit-text-fill-color:var(--ink)!important}
[data-baseweb="input"],[data-baseweb="select"]>div,[data-baseweb="textarea"]{border:1px solid #C9D2DF!important;border-radius:10px!important}
input::placeholder,textarea::placeholder{color:#8A96A8!important;-webkit-text-fill-color:#8A96A8!important}
[data-baseweb="popover"] *,[data-baseweb="menu"] *{background:#fff;color:var(--ink)!important}
[data-baseweb="menu"] li:hover,[data-baseweb="menu"] li:hover *{background:var(--teal-l)}
[data-testid="stAlert"] *{color:var(--ink)!important}
[data-testid="stExpander"]{background:#fff;border:1px solid var(--line);border-radius:12px}
.stButton>button p,.stFormSubmitButton>button p,.stButton>button *,.stFormSubmitButton>button *{color:#fff!important}
section[data-testid="stSidebar"] .stButton>button{background:var(--gold);border:0}
section[data-testid="stSidebar"] .stButton>button *{color:var(--ink)!important}
section[data-testid="stSidebar"] .brand,section[data-testid="stSidebar"] .brand span{color:#fff!important}
section[data-testid="stSidebar"] .brand span{color:var(--gold)!important}
.welcome{max-width:520px;margin:0 auto}
</style>""", unsafe_allow_html=True)

def page_heading(title, sub):
    st.markdown(f'<div class="page-title">{safe(title)}</div><div class="page-sub">{safe(sub)}</div>', unsafe_allow_html=True)

def metric(label, value, note=""):
    st.markdown(f'<div class="metric"><div class="l">{safe(label)}</div><div class="v">{safe(value)}</div><div class="n">{safe(note)}</div></div>', unsafe_allow_html=True)

def campaign_card(r):
    p = progress(r.raised, r.goal)
    st.markdown(f'''<div class="campaign"><span class="tag">{safe(r.category)}</span>
<h3>{safe(r.title)}</h3><p>{safe(r.description)}</p>
<div class="bar"><div style="width:{p}%"></div></div>
<div class="meta"><span><b>{money(r.raised)}</b> raised of {money(r.goal)}</span><span><b>{p}%</b></span></div>
<div class="meta" style="margin-top:6px"><span>{safe(r.organiser)} · {safe(r.city)}</span><span>{safe(r.donors)} supporters · {safe(r.status)}</span></div></div>''', unsafe_allow_html=True)

def num(df, cols):
    for col in cols: df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df

def require_login():
    if st.session_state.user: return True
    st.info("Please enter your name and email to continue.")
    return False

# ---------------------------------------------------------------- pages
def overview():
    c = num(load_data("campaigns"), ["raised", "goal", "donors"])
    st.markdown('<div class="hero"><div class="kicker">COMMUNITY GIVING PLATFORM</div><h1>Small contributions.<br>Shared, visible progress.</h1><p>EKATRIT brings community campaigns together with clear goals, open progress tracking and responsible promotion.</p><div class="slogan">Together, we make giving matter.</div></div>', unsafe_allow_html=True)
    a, b, z, d = st.columns(4)
    with a: metric("Funds raised", money(c.raised.sum()), "Sample records")
    with b: metric("Active campaigns", str(int((c.status == "Active").sum())), "Open for support")
    with z: metric("Supporters", f"{int(c.donors.sum()):,}", "Simulated contributions")
    with d: metric("Cities", str(c.city.nunique()), "Across Odisha")
    st.markdown('<div class="section-title">Featured campaigns</div><div class="section-sub">Closest to their goal and still open.</div>', unsafe_allow_html=True)
    act = c[c.status == "Active"].copy()
    act["p"] = act.apply(lambda r: progress(r.raised, r.goal), axis=1)
    cols = st.columns(2)
    for i, r in enumerate(act.sort_values("p", ascending=False).head(4).itertuples()):
        with cols[i % 2]: campaign_card(r)

def discover():
    page_heading("Discover campaigns", "Search by cause, city or organiser.")
    c = num(load_data("campaigns"), ["raised", "goal", "donors"])
    c = c[c.status.isin(["Active", "Completed"])]
    f1, f2, f3 = st.columns([2, 1, 1])
    q = f1.text_input("Search", placeholder="Try 'health', 'Cuttack' or an organiser")
    cat = f2.selectbox("Category", ["All"] + CATEGORIES)
    sort = f3.selectbox("Sort by", ["Most funded", "Closest to goal", "Newest"])
    if cat != "All": c = c[c.category == cat]
    if q:
        m = c[["title", "city", "organiser", "description"]].apply(lambda s: s.str.contains(q, case=False)).any(axis=1)
        c = c[m]
    if sort == "Most funded": c = c.sort_values("raised", ascending=False)
    elif sort == "Closest to goal": c = c.assign(p=c.apply(lambda r: progress(r.raised, r.goal), axis=1)).sort_values("p", ascending=False)
    else: c = c.sort_values("campaign_id", ascending=False)
    if c.empty:
        st.info("No campaigns match these filters. Clear the search or choose another category."); return
    cols = st.columns(2)
    for i, r in enumerate(c.itertuples()):
        with cols[i % 2]: campaign_card(r)

def donations():
    page_heading("Contribute", "Choose a campaign and record a simulated contribution.")
    st.caption("Prototype only: no real money is collected.")
    if not require_login(): return
    c = load_data("campaigns"); c = c[c.status == "Active"]
    if c.empty: st.info("No active campaigns right now."); return
    with st.form("donate"):
        title = st.selectbox("Campaign", c.title.tolist())
        amount = st.number_input("Amount (INR)", min_value=10, max_value=100000, value=500, step=50)
        ok = st.form_submit_button("Confirm contribution")
    if ok:
        row = c[c.title == title].iloc[0]
        allc = load_data("campaigns"); idx = allc.index[allc.campaign_id == row.campaign_id][0]
        allc.loc[idx, "raised"] = str(float(allc.loc[idx, "raised"] or 0) + amount)
        allc.loc[idx, "donors"] = str(int(float(allc.loc[idx, "donors"] or 0)) + 1)
        save_data("campaigns", allc)
        d = load_data("donations")
        new = pd.DataFrame([[uuid.uuid4().hex[:8], st.session_state.user["email"], row.campaign_id, amount, amount // 10, datetime.now().strftime("%d %b %Y, %H:%M")]], columns=SCHEMA["donations"])
        save_data("donations", pd.concat([d, new], ignore_index=True))
        st.success(f"Thank you. {money(amount)} recorded for “{title}” and {amount // 10} points earned.")
        st.balloons()

def create_campaign():
    page_heading("Create a campaign", "Submit a cause for review. Listings go live after verification.")
    if not require_login(): return
    with st.form("create"):
        t = st.text_input("Campaign title")
        l, r = st.columns(2)
        cat = l.selectbox("Category", CATEGORIES)
        org = r.text_input("Organiser or group name")
        l, r = st.columns(2)
        city = l.text_input("City")
        goal = r.number_input("Goal (INR)", min_value=1000, value=50000, step=1000)
        end = st.date_input("Closing date", value=date.today() + timedelta(days=45), min_value=date.today())
        desc = st.text_area("What will the funds support?", height=120, placeholder="Describe the need, who benefits and how progress will be shared.")
        ok = st.form_submit_button("Submit for review")
    if ok:
        if not all([t.strip(), org.strip(), city.strip(), len(desc.strip()) >= 30]):
            st.error("Please complete every field. The description needs at least 30 characters."); return
        c = load_data("campaigns")
        row = [f"C{len(c)+1:03d}", t.strip(), cat, org.strip(), city.strip(), desc.strip(), goal, 0, 0, "Pending Review", end.isoformat(), st.session_state.user["email"]]
        save_data("campaigns", pd.concat([c, pd.DataFrame([row], columns=SCHEMA["campaigns"])], ignore_index=True))
        st.success("Campaign submitted. It will appear in Discover once it is reviewed.")

def activity():
    page_heading("My activity", "Your contributions and points in one place.")
    if not require_login(): return
    user = st.session_state.user
    d, c = num(load_data("donations"), ["amount", "points_earned"]), load_data("campaigns")
    mine = d[d.email == user.get("email")]
    a, b, z = st.columns(3)
    with a: metric("Total contributed", money(mine.amount.sum()), "Simulated amount")
    with b: metric("Points earned", f"{int(mine.points_earned.sum()):,}", "1 point per ₹10")
    with z: metric("Contributions", str(len(mine)), "Simulated contribution records")
    st.markdown('<div class="section-title">Contribution history</div>', unsafe_allow_html=True)
    if mine.empty:
        st.info("Your contribution history will appear here.")
    else:
        v = mine.merge(c[["campaign_id", "title"]], on="campaign_id", how="left")[["donated_at", "title", "amount", "points_earned"]]
        st.dataframe(v.rename(columns={"donated_at": "Date", "title": "Campaign", "amount": "Amount (INR)", "points_earned": "Points"}), use_container_width=True, hide_index=True)
    with st.expander("Profile details"):
        st.write("**Name:**", user.get("name", ""))
        st.write("**Email:**", user.get("email", ""))
        st.write("**City:**", user.get("city", ""))

def advertise():
    page_heading("Advertise & promote", "Explore transparent promotional placements for community campaigns.")
    st.markdown('<div class="hero"><div class="kicker">CAMPAIGN VISIBILITY</div><h1>Help the right people<br>discover your cause.</h1><p>Promotional placements can help campaigns reach relevant supporters. Sponsored content should always be clearly identified.</p><div class="slogan">Visibility with transparency.</div></div>', unsafe_allow_html=True)
    ads, c = load_data("advertisements"), load_data("campaigns")
    a, b, z = st.columns(3)
    with a: metric("Active placements", str(int((ads.status == "Active").sum())), "Sample inventory")
    with b: metric("Available formats", "3", "Homepage, discovery, category")
    with z: metric("Promotion policy", "Disclosed", "Promoted content is labelled")
    st.markdown('<div class="section-title">Promotional formats</div>', unsafe_allow_html=True)
    cols = st.columns(3)
    for col, (title, desc) in zip(cols, [("Homepage feature", "Prominent placement on the overview page."), ("Discover spotlight", "Highlighted card in campaign discovery."), ("Category feature", "Visibility within a relevant cause category.")]):
        with col:
            st.markdown(f'<div class="campaign"><span class="tag">PROMOTION FORMAT</span><h3>{safe(title)}</h3><p>{safe(desc)}</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Current promoted campaigns</div>', unsafe_allow_html=True)
    active = ads[ads.status == "Active"]
    if active.empty: st.info("No active sample promotional placements.")
    for ad in active.itertuples():
        match = c[c.campaign_id == ad.campaign_id]
        title = match.iloc[0].title if not match.empty else "Campaign"
        st.markdown(f'<div class="insight"><span class="tag gold">PROMOTED</span><h3>{safe(ad.headline)}</h3><b>{safe(title)}</b><p>{safe(ad.description)} · {safe(ad.placement)}</p></div>', unsafe_allow_html=True)
    st.caption("Prototype only. No advertising payments, impressions or reach guarantees are provided.")

def insights():
    page_heading("Insights & ideas", "Practical guidance and product ideas for stronger community campaigns.")
    st.markdown('<div class="section-title">Community giving: useful principles</div>', unsafe_allow_html=True)
    facts = [("Trust begins with clarity", "Explain who is organising the campaign, what funds support, how progress will be reported and when it closes."), ("Specific goals are easier to understand", "Break broad fundraising targets into clear needs such as learning materials, meals, transport or equipment."), ("Progress updates matter", "Regular updates and outcome summaries help supporters understand what happened after contributing."), ("Local partnerships add context", "Community partners can improve coordination, local knowledge and accountability.")]
    for title, body in facts:
        st.markdown(f'<div class="insight"><b>{safe(title)}</b><p>{safe(body)}</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">How EKATRIT could become better</div><div class="section-sub">A possible roadmap for a future production-ready platform.</div>', unsafe_allow_html=True)
    ideas = [("Campaign verification", "Add identity and organisation checks, supporting documents and visible verification status."), ("Transparent fund utilisation", "Publish planned budgets, expense updates and downloadable campaign reports."), ("Secure payment integration", "Connect a regulated payment gateway with server-side verification and digital receipts."), ("Impact measurement", "Track outcomes such as meals served, learning kits delivered, trees planted or families assisted."), ("Accessibility and languages", "Support mobile layouts, screen readers and regional languages such as Odia and Hindi."), ("Responsible promotion", "Publish advertising rules, disclose sponsored placements and prevent misleading claims."), ("AI-assisted discovery", "Explore recommendations based on user-selected interests, with clear explanations for suggestions.")]
    cols = st.columns(2)
    for i, (title, body) in enumerate(ideas):
        with cols[i % 2]:
            st.markdown(f'<div class="insight"><b>{safe(title)}</b><p>{safe(body)}</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="panel"><b>Prototype note:</b> These are general product-design suggestions, not verified live impact statistics. A public service needs documented verification, privacy, payment and financial-reporting processes.</div>', unsafe_allow_html=True)

def analytics():
    c = num(load_data("campaigns"), ["raised", "goal", "donors"])
    page_heading("Impact analytics", "Explore campaign performance using the sample records stored in EKATRIT.")
    a, b, z = st.columns(3)
    with a: metric("Funds raised", money(c.raised.sum()), "Sample campaign records")
    with b: metric("Campaigns listed", str(len(c)), "Includes pending submissions")
    with z: metric("Active campaigns", str(int((c.status == "Active").sum())), "Currently listed as active")
    left, right = st.columns(2)
    style = dict(plot_bgcolor="white", paper_bgcolor="white", font_family="DM Sans", margin=dict(l=10, r=10, t=55, b=15))
    with left:
        g = c.groupby("category", as_index=False).raised.sum()
        fig = px.bar(g, x="category", y="raised", title="Funds raised by category", labels={"category": "Category", "raised": "Amount (INR)"}, color_discrete_sequence=["#1B3A63"])
        fig.update_layout(**style, xaxis_title=None)
        st.plotly_chart(fig, use_container_width=True)
    with right:
        g = c.sort_values("raised", ascending=True).tail(7)
        fig = px.bar(g, x="raised", y="title", orientation="h", title="Top campaigns by funds raised", labels={"title": "Campaign", "raised": "Amount (INR)"}, color_discrete_sequence=["#1F8A80"])
        fig.update_layout(**style, yaxis_title=None)
        st.plotly_chart(fig, use_container_width=True)
    st.markdown('<div class="section-title">Campaign performance</div>', unsafe_allow_html=True)
    view = c[["title", "category", "raised", "goal", "donors", "status"]].copy()
    view["Progress"] = view.apply(lambda r: f"{progress(r.raised, r.goal)}%", axis=1)
    st.dataframe(view.rename(columns={"title": "Campaign", "category": "Category", "raised": "Raised (INR)", "goal": "Goal (INR)", "donors": "Supporters", "status": "Status"}), use_container_width=True, hide_index=True)

# ---------------------------------------------------------------- app
def welcome():
    st.markdown('<div class="hero" style="margin-top:2vh"><div class="kicker">WELCOME TO EKATRIT</div><h1>Together, we make<br>giving matter.</h1><p>Tell us who you are to explore campaigns, record contributions and track your impact. No password needed.</p></div>', unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 2, 1])
    with mid, st.form("entry"):
        st.markdown("**Continue as a member**")
        name = st.text_input("Your name", placeholder="e.g. Ananya Mohanty")
        email = st.text_input("Email address", placeholder="you@example.com")
        go = st.form_submit_button("Enter EKATRIT", use_container_width=True)
    if go:
        e = email.strip().lower()
        if len(name.strip()) < 2 or "@" not in e or "." not in e.split("@")[-1]:
            st.error("Enter your name and a valid email address, for example name@example.com."); return
        u = load_data("users"); m = u[u.email == e]
        if m.empty:
            row = pd.DataFrame([[uuid.uuid4().hex[:8], name.strip(), e, "", "", ""]], columns=SCHEMA["users"])
            save_data("users", pd.concat([u, row], ignore_index=True)); user = row.iloc[0].to_dict()
        else:
            user = m.iloc[0].to_dict(); user["name"] = user["name"] or name.strip()
        st.session_state.user = user; st.session_state.page = "Overview"; st.rerun()

def main():
    st.set_page_config(page_title="EKATRIT | Community Giving Platform Prototype", page_icon="🤝", layout="wide", initial_sidebar_state="expanded")
    initialise_data()
    if "user" not in st.session_state: st.session_state.user = None
    if "page" not in st.session_state: st.session_state.page = "Overview"
    add_styles()
    if not st.session_state.user:
        st.markdown("<style>section[data-testid='stSidebar'],[data-testid='stSidebarCollapsedControl']{display:none}</style>", unsafe_allow_html=True)
        welcome(); return
    pages = ["Overview", "Discover Campaigns", "Donations", "Create Campaign", "My Activity", "Advertise", "Insights & Ideas", "Analytics"]
    with st.sidebar:
        st.markdown('<div class="brand">EKA<span>TRIT</span></div><div class="side-note">Together, we make giving matter.</div>', unsafe_allow_html=True)
        st.markdown("---")
        st.session_state.page = st.radio("Navigation", pages, index=pages.index(st.session_state.page) if st.session_state.page in pages else 0)
        st.markdown("---")
        if st.session_state.user:
            st.markdown(f'**{safe(st.session_state.user.get("name", "Member"))}**')
            st.markdown(f'<div class="side-note">{safe(st.session_state.user.get("email", ""))}</div>', unsafe_allow_html=True)
            if st.button("Sign out", use_container_width=True):
                st.session_state.user = None
                st.rerun()
        else:
            st.markdown('<div class="side-note">You are signed in. Contribute, submit campaigns and track your activity.</div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown('<div class="side-note"><b>EKATRIT</b><br>Community Giving Platform Prototype<br><br>Developed by Dibyajyoti Swain</div>', unsafe_allow_html=True)
    {"Overview": overview, "Discover Campaigns": discover, "Donations": donations, "Create Campaign": create_campaign,
     "My Activity": activity, "Advertise": advertise, "Insights & Ideas": insights, "Analytics": analytics}[st.session_state.page]()
    st.markdown("<div style='text-align:center;color:#98A3B2;font-size:11px;padding:28px 8px 8px'>EKATRIT · Together, we make giving matter · Community Giving Platform Prototype</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()