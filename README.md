# Fundraise — Community Giving Platform

A polished Streamlit portfolio project developed by **Dibyajyoti Swain**.

## Features
- Executive-style overview dashboard
- Campaign discovery, search, category filters and sorting
- Account registration and sign-in
- Simulated contribution workflow and supporter points
- Campaign submission marked Pending Review
- Personal contribution history
- Dedicated campaign advertising and promotion page
- Insights & Ideas page with product-improvement recommendations
- Impact analytics with Plotly charts
- CSV storage created automatically on first run

## Run locally
```bash
python -m venv .venv
# Windows PowerShell:
.venv\\Scripts\\activate
# macOS / Linux:
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

The application creates its sample CSV datasets inside `data/` on first launch.

## Important limitations
This is a portfolio demonstration. Donations are simulated; no money is transferred and no payment gateway is connected. Campaign submissions are marked Pending Review, but there is no administrator verification console. CSV storage is suitable for local demos, not concurrent production use. The prototype password hashing is not a substitute for production authentication. A public launch requires secure authentication, payment processing, campaign verification, privacy controls, audit logs, fraud prevention and legal/compliance review.

Do not commit real personal information, credentials or donor records to a public repository.

## Author
**Dibyajyoti Swain**
