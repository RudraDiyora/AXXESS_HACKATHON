import requests
import re

CLINICAL_TABLES_URL = "https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search"
OPENFDA_EVENT_URL = "https://api.fda.gov/drug/event.json"


def sanitize_search_term(text):
    """Remove special characters and normalize whitespace for API queries."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    return text.strip()


def search_icd10_code(disease_name):
    """Look up an ICD-10-CM code by disease name using the NLM Clinical Tables API.

    OpenFDA does not provide ICD-10 lookup, so this remains the one NIH call.
    Returns (code, name) tuple or None if no match found.
    """
    term = sanitize_search_term(disease_name)
    response = requests.get(
        CLINICAL_TABLES_URL,
        params={"sf": "code,name", "df": "code,name", "terms": term},
    )
    data = response.json()

    if data[0] > 0:
        code, name = data[3][0]
        return code, name
    return None


def fetch_top_medications(indication, top_n=10):
    """Fetch the most prescribed medications for a condition via OpenFDA.

    Searches the FDA Adverse Event Reporting System (FAERS) by drug
    indication and counts by generic drug name. Drugs prescribed more
    often generate more reports, so the count is a strong proxy for
    real-world prescribing frequency.

    This single call replaces the previous RxClass + OpenFDA ranking
    two-step approach.

    Args:
        indication: Disease/condition name (e.g. 'diabetes mellitus').
        top_n: Number of top medications to return.

    Returns a list of (name, report_count) tuples sorted by frequency.
    """
    search_query = f'patient.drug.drugindication:"{indication.upper()}"'

    response = requests.get(
        OPENFDA_EVENT_URL,
        params={
            "search": search_query,
            "count": "patient.drug.openfda.generic_name.exact",
        },
    )

    if response.status_code != 200:
        print(f"OpenFDA API error: {response.status_code}")
        return []

    data = response.json()
    results = data.get("results", [])

    # Deduplicate by base drug name — OpenFDA sometimes returns dosage-
    # specific entries like "metformin er 500 mg" alongside "metformin".
    # Keep the entry with the highest count for each base name.
    seen = {}
    for entry in results:
        name = entry["term"].lower()
        base = re.split(r"\s+\d+\s*m?g|\s+er\b|\s+xr\b|\s+hcl\b|\s+sr\b", name)[0].strip()
        if base not in seen or entry["count"] > seen[base][1]:
            seen[base] = (name, entry["count"])

    ranked = sorted(seen.values(), key=lambda x: x[1], reverse=True)
    return ranked[:top_n]


def get_medications_for_disease(disease_name, top_n=10):
    """End-to-end: disease name → ICD-10 code + top prescribed medications.

    Flow: disease name → ICD-10 lookup (NLM Clinical Tables)
          → top medications by prescribing frequency (OpenFDA FAERS).

    Args:
        disease_name: Human-readable disease name.
        top_n: Number of top medications to return.
    """
    # Step 1: ICD-10 lookup (OpenFDA doesn't offer this)
    icd_result = search_icd10_code(disease_name)
    if not icd_result:
        print("No ICD-10 match found.")
        return None, []

    icd_code, icd_name = icd_result
    print(f"ICD Code: {icd_code} — {icd_name}")

    # Step 2: Fetch top medications directly from OpenFDA
    medications = fetch_top_medications(disease_name, top_n=top_n)
    if not medications:
        # Retry with the ICD-10 display name (may differ from input)
        medications = fetch_top_medications(icd_name, top_n=top_n)

    return icd_code, medications
