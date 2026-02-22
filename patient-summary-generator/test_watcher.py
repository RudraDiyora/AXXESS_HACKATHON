"""Quick smoke test for the file watcher mechanism (no LLM calls).

1. Starts the watcher in a background thread.
2. Copies test_input.json → initial_file.json.
3. Waits for the assembled_patient.json to appear.
4. Validates the assembled output.
"""

import json
import os
import shutil
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(__file__))

from src.services.patient_assembler import assemble_patient_json
from src.services.validator import validate_and_normalize

PROJECT_ROOT = os.path.dirname(__file__)
DATA_DIR = os.path.join(PROJECT_ROOT, "src", "data")
TRIGGER = os.path.join(DATA_DIR, "initial_file.json")
ASSEMBLED = os.path.join(DATA_DIR, "assembled_patient.json")
TEST_SRC = os.path.join(DATA_DIR, "test_input.json")

# Clean up
for path in (TRIGGER, ASSEMBLED):
    if os.path.exists(path):
        os.remove(path)


# -- Inline mini-pipeline (assembler only, no LLM) --
def offline_pipeline(input_path):
    """Run assembler + validator only (skip LLM)."""
    with open(input_path) as fh:
        raw = json.load(fh)
    assembled = assemble_patient_json(raw)
    with open(ASSEMBLED, "w") as fh:
        json.dump(assembled, fh, indent=2)
    print(f"  ✓ Assembled JSON written to {ASSEMBLED}")


# -- Watchdog setup --
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

processing_done = threading.Event()


class TestHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self._last = 0

    def on_created(self, event):
        if not event.is_directory and os.path.basename(event.src_path) == "initial_file.json":
            now = time.time()
            if now - self._last < 2:
                return
            self._last = now
            print("  File detected by watcher!")
            offline_pipeline(event.src_path)
            processing_done.set()


handler = TestHandler()
observer = Observer()
observer.schedule(handler, DATA_DIR, recursive=False)
observer.start()

print("=== Watcher started, dropping initial_file.json… ===")
time.sleep(0.5)  # let the observer settle

# Simulate the previous stage dropping the file
shutil.copy(TEST_SRC, TRIGGER)
print(f"  Copied {TEST_SRC} → {TRIGGER}")

# Wait for processing
if processing_done.wait(timeout=30):
    print("  ✓ Watcher triggered successfully!")
else:
    print("  ✗ Timed out waiting for watcher to trigger")
    observer.stop()
    observer.join()
    sys.exit(1)

observer.stop()
observer.join()

# -- Validate assembled output --
print("\n=== Validating assembled output ===")
with open(ASSEMBLED) as fh:
    assembled = json.load(fh)

assert "patient" in assembled, "Missing patient key"
assert "clinical_data" in assembled, "Missing clinical_data key"

cd = assembled["clinical_data"]
assert len(cd.get("diagnoses", [])) > 0, "No diagnoses generated"
assert len(cd.get("medications_prescribed", [])) > 0, "No medications"

for dx in cd["diagnoses"]:
    assert "description" in dx and "icd_code" in dx and "confidence" in dx, \
        f"Diagnosis missing fields: {dx}"

result = validate_and_normalize(assembled)
assert result["valid"], f"Validation failed: {result['errors']}"

print("  ✓ All fields present and valid")
print(f"  Diagnoses: {len(cd['diagnoses'])}")
print(f"  Medications: {len(cd['medications_prescribed'])}")
print(json.dumps(assembled, indent=2))

# Cleanup
for path in (TRIGGER, ASSEMBLED):
    if os.path.exists(path):
        os.remove(path)

print("\n=== File watcher smoke test PASSED ===")
