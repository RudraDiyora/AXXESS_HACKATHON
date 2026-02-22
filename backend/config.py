"""
Shared configuration — loads environment variables once.
"""

import os
from dotenv import load_dotenv

load_dotenv()

FEATHERLESS_API_KEY = os.getenv("FEATHERLESS_API_KEY", "")
FEATHERLESS_MODEL = os.getenv("FEATHERLESS_MODEL", "deepseek-ai/DeepSeek-V3-0324")
FEATHERLESS_BASE_URL = "https://api.featherless.ai/v1"

ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY", "")
ASSEMBLYAI_UPLOAD_URL = "https://api.assemblyai.com/v2/upload"
ASSEMBLYAI_TRANSCRIBE_URL = "https://api.assemblyai.com/v2/transcript"
