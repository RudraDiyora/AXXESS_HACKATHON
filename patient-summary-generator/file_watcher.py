"""File watcher — auto-triggers the assembler + summary pipeline.

Monitors the project's ``src/data/`` directory for ``initial_file.json``.
When the file appears (or is modified), it:

1. Reads the partial patient JSON (no diagnoses).
2. Runs the assembler to generate diagnoses & augment medications.
3. Writes the assembled JSON to ``src/data/assembled_patient.json``.
4. Calls the summary pipeline (validator → LLM → post-processor).
5. Writes the final summary output to ``output.json`` and ``output.html``.

The watcher keeps running and will re-process whenever the file changes.
Press Ctrl-C to stop.
"""

import json
import os
import sys
import time

# Ensure project root is on the path so src.* imports work
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from src.services.patient_assembler import assemble_patient_json
from src.services.validator import validate_and_normalize
from src.services.llm_service import generate_summary
from src.services.post_processor import post_process

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
WATCH_DIR = os.path.join(PROJECT_ROOT, "src", "data")
TRIGGER_FILENAME = "initial_file.json"
TRIGGER_PATH = os.path.join(WATCH_DIR, TRIGGER_FILENAME)
ASSEMBLED_PATH = os.path.join(WATCH_DIR, "assembled_patient.json")
OUTPUT_JSON = os.path.join(PROJECT_ROOT, "output.json")
OUTPUT_HTML = os.path.join(PROJECT_ROOT, "output.html")


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------
def run_pipeline(input_path: str) -> None:
    """Full pipeline: assemble → validate → LLM summary → post-process."""

    print(f"\n{'='*60}")
    print(f"  File detected: {input_path}")
    print(f"{'='*60}\n")

    # 1. Read partial input -----------------------------------------------
    try:
        with open(input_path) as fh:
            raw = json.load(fh)
    except (json.JSONDecodeError, OSError) as exc:
        print(f"  ✗ Could not read input file: {exc}")
        return

    # 2. Assemble (generate diagnoses + meds) -----------------------------
    print("  [1/4] Assembling patient JSON (ICD-10 + medication lookup)…")
    try:
        assembled = assemble_patient_json(raw)
    except Exception as exc:
        print(f"  ✗ Assembly failed: {exc}")
        return

    with open(ASSEMBLED_PATH, "w") as fh:
        json.dump(assembled, fh, indent=2)
    print(f"  ✓ Assembled JSON saved → {ASSEMBLED_PATH}")

    # 3. Validate ---------------------------------------------------------
    print("  [2/4] Validating assembled data…")
    result = validate_and_normalize(assembled)
    if not result["valid"]:
        print(f"  ✗ Validation failed: {result['errors']}")
        return
    if result["warnings"]:
        print(f"  ⚠ Warnings: {result['warnings']}")
    print("  ✓ Validation passed")

    normalized = result["normalized"]

    # 4. LLM summary ------------------------------------------------------
    print("  [3/4] Generating patient-friendly summary via LLM…")
    try:
        raw_summary = generate_summary(normalized)
    except Exception as exc:
        print(f"  ✗ LLM call failed: {exc}")
        return
    print("  ✓ LLM response received")

    # 5. Post-process -----------------------------------------------------
    print("  [4/4] Post-processing (jargon replacement, HTML render)…")
    processed = post_process(raw_summary, normalized["patient"]["name"])

    # 6. Write outputs ----------------------------------------------------
    with open(OUTPUT_JSON, "w") as fh:
        json.dump(
            {
                "success": True,
                "warnings": result["warnings"],
                **processed,
            },
            fh,
            indent=2,
        )

    with open(OUTPUT_HTML, "w") as fh:
        fh.write(processed["html"])

    print(f"\n  ✓ Summary JSON → {OUTPUT_JSON}")
    print(f"  ✓ Summary HTML → {OUTPUT_HTML}")
    print(f"  ✓ Word count: {processed['meta']['word_count']}")
    print(f"\n{'='*60}")
    print("  Pipeline complete — waiting for next file…")
    print(f"{'='*60}\n")


# ---------------------------------------------------------------------------
# Watchdog handler
# ---------------------------------------------------------------------------
class InitialFileHandler(FileSystemEventHandler):
    """React to creation or modification of initial_file.json."""

    def __init__(self):
        super().__init__()
        self._last_run = 0  # debounce: ignore duplicate events within 2 s

    def _should_process(self, event) -> bool:
        if event.is_directory:
            return False
        # Match the trigger filename regardless of how the event path is reported
        return os.path.basename(event.src_path) == TRIGGER_FILENAME

    def on_created(self, event):
        if self._should_process(event):
            self._debounced_run(event.src_path)

    def on_modified(self, event):
        if self._should_process(event):
            self._debounced_run(event.src_path)

    def _debounced_run(self, path):
        now = time.time()
        if now - self._last_run < 2:
            return  # skip duplicate event
        self._last_run = now
        run_pipeline(path)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print(f"Watching for '{TRIGGER_FILENAME}' in {WATCH_DIR}")
    print("Drop or update the file to trigger the pipeline.  Ctrl-C to stop.\n")

    # If the file already exists, process it immediately
    if os.path.isfile(TRIGGER_PATH):
        print(f"'{TRIGGER_FILENAME}' already exists — processing now…")
        run_pipeline(TRIGGER_PATH)

    handler = InitialFileHandler()
    observer = Observer()
    observer.schedule(handler, WATCH_DIR, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping watcher…")
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
