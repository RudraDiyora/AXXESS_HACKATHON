"""
Post-processing — jargon replacement, word count check, HTML rendering.

Source: Patient_Summary_Generator branch (src/services/post_processor.py)
"""

import re

from data.jargon_list import medical_jargon


def _replace_jargon(text: str) -> str:
    """Replace medical jargon with plain-English equivalents."""
    cleaned = text
    for entry in medical_jargon:
        pattern = re.compile(rf"\b{re.escape(entry['term'])}\b", re.IGNORECASE)
        cleaned = pattern.sub(entry["plain"], cleaned)
    return cleaned


def _check_word_count(summary_obj: dict) -> dict:
    full_text = " ".join(str(v) for v in summary_obj.values())
    word_count = len(full_text.split())
    return {"word_count": word_count, "too_long": word_count > 400}


def _build_rendered_html(summary_obj: dict, patient_name: str) -> str:
    return f"""<div class="patient-summary">
  <p class="greeting">{summary_obj.get('greeting', '')}</p>
  <h3>What We Found Today</h3>
  <p>{summary_obj.get('what_we_found', '')}</p>
  <h3>Your Vital Signs</h3>
  <p>{summary_obj.get('your_vitals', '')}</p>
  <h3>Your Medications</h3>
  <p>{summary_obj.get('your_medications', '')}</p>
  <h3>Things To Watch For</h3>
  <p>{summary_obj.get('watch_for', '')}</p>
  <h3>Your Next Steps</h3>
  <p>{summary_obj.get('next_steps', '')}</p>
  <p class="closing">{summary_obj.get('closing', '')}</p>
</div>""".strip()


def post_process(summary_obj: dict, patient_name: str) -> dict:
    """
    Clean up an LLM-generated summary: replace jargon, check length,
    and render HTML.
    """
    cleaned = {key: _replace_jargon(str(val)) for key, val in summary_obj.items()}

    wc = _check_word_count(cleaned)
    html = _build_rendered_html(cleaned, patient_name)

    return {
        "summary": cleaned,
        "html": html,
        "meta": {
            "word_count": wc["word_count"],
            "too_long": wc["too_long"],
            "flagged": (
                ["Summary exceeds recommended length"] if wc["too_long"] else []
            ),
        },
    }
