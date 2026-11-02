# EKATRIT

**Together, we make giving matter.**

EKATRIT is a community giving platform prototype built with Streamlit. It brings local fundraising campaigns together in one place, with clear goals, visible progress and clearly labelled promotion.

> **Prototype only.** EKATRIT does not process real payments, verify organisations or issue receipts. All amounts, campaigns and contributions are simulated.

STREAMLIT APP LINK: https://ekatrit-app-prototype-dibyajyoti.streamlit.app/ 

---

## Features

| Area | What it does |
| --- | --- |
| **Welcome** | Enter your name and email to get in. No password. Returning emails are recognised automatically. |
| **Overview** | Hero banner, headline metrics and featured campaigns closest to their goal. |
| **Discover Campaigns** | Search by title, city, organiser or description. Filter by category and sort by funding or progress. |
| **Donations** | Record a simulated contribution (₹10 to ₹1,00,000). Campaign totals update immediately and you earn 1 point per ₹10. |
| **Create Campaign** | Submit a cause with title, category, organiser, city, goal, closing date and description. New campaigns start as *Pending Review*. |
| **My Activity** | Your total contributed, points earned, contribution history and profile details. |
| **Advertise** | Three promotional formats and the currently promoted campaigns, always tagged **PROMOTED**. |
| **Insights & Ideas** | Principles for trustworthy campaigns and a roadmap for a production version. |
| **Analytics** | Funds raised by category, top campaigns and a performance table with progress percentages. |

---

## Quick start

**Requirements:** Python 3.9 or newer.

```bash
# 1. Get the files into a folder
#    app.py, requirements.txt, .streamlit/config.toml

# 2. (Recommended) create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run
streamlit run app.py
```

Streamlit opens the app at `http://localhost:8501`.

### Project structure

```
ekatrit/
├── app.py                  # The whole application
├── requirements.txt        # streamlit, pandas, plotly
├── README.md
├── .streamlit/
│   └── config.toml         # Light theme (keeps text readable in dark mode)
└── ekatrit_data/           # Created on first run
    ├── users.csv
    ├── campaigns.csv
    ├── donations.csv
    └── advertisements.csv
```

Restart Streamlit after adding or editing `.streamlit/config.toml`. The theme file is only read at startup.

---

## How it works

- **Storage:** plain CSV files in `ekatrit_data/`, created and seeded with six sample campaigns and three sample ads on first launch.
- **Sessions:** the signed-in member is held in Streamlit's session state. "Sign out" returns you to the welcome page.
- **Safety:** every piece of user text shown inside custom HTML passes through `html.escape`, so names and campaign descriptions cannot inject markup.
- **Styling:** custom CSS (Plus Jakarta Sans and DM Sans, navy, teal and gold palette) with an explicit contrast guard, so text stays readable on every surface.

### Data reference

| File | Columns |
| --- | --- |
| `users.csv` | `user_id, name, email, city, pw_hash, salt` (`pw_hash` and `salt` are unused and kept empty) |
| `campaigns.csv` | `campaign_id, title, category, organiser, city, description, goal, raised, donors, status, deadline, owner_email` |
| `donations.csv` | `donation_id, email, campaign_id, amount, points_earned, donated_at` |
| `advertisements.csv` | `ad_id, campaign_id, headline, description, placement, status` |

### Common tasks

- **Approve a pending campaign:** open `ekatrit_data/campaigns.csv` and change its `status` from `Pending Review` to `Active`. It then appears in Discover.
- **Reset all data:** stop the app and delete the `ekatrit_data/` folder. Fresh sample data is created on the next run.
- **Add a category:** edit the `CATEGORIES` list near the top of `app.py`.

---

## Known limitations

- Email-only entry has **no authentication**. Anyone can enter any email address.
- CSV storage is not safe for many users writing at once.
- No payment gateway, receipts, campaign verification or fund-utilisation reporting.
- No admin screen yet. Campaign approval is done by editing the CSV.

## Roadmap

1. Campaign and organiser verification with a visible status badge
2. Regulated payment gateway with server-side confirmation and receipts
3. Published budgets, expense updates and downloadable campaign reports
4. Impact measurement (meals served, kits delivered, trees planted)
5. Odia and Hindi language support, plus screen-reader improvements
6. Published advertising rules and sponsored-content disclosure checks
7. Admin dashboard and a proper database (SQLite or PostgreSQL)
8. Explainable, interest-based campaign recommendations

---

## Troubleshooting

| Problem | Fix |
| --- | --- |
| `streamlit: command not found` | Run `python -m streamlit run app.py`, or activate your virtual environment. |
| Text hard to read | Confirm `.streamlit/config.toml` is in place, then restart Streamlit and hard-refresh the browser. |
| Changes not showing | Click **Rerun** in the Streamlit menu, or stop and restart the app. |
| Strange or old data | Delete the `ekatrit_data/` folder to reset to the sample data. |

---

## Credits

Designed and developed by **Dibyajyoti Swain**.


