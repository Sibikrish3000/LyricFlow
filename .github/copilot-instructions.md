### **Project Title Suggestion: `LyricFlow`**

A modular Python toolkit for the automated processing and embedding of song lyrics, featuring a powerful CLI and a scalable FastAPI web service.

### **Core Philosophy**

*   **Modularity:** Each component (audio handling, fetching, romanization, ASR) should be independently usable and easily replaceable.
*   **Efficiency:** Prioritize existing data first (embedded tags -> local files -> online APIs) before resorting to computationally expensive operations like ASR.
*   **Developer-Friendliness:** A clean, well-documented, and testable codebase is paramount. Use modern Python practices and tooling.
*   **User-Friendliness:** Both the CLI and API should provide clear feedback, progress indicators, and robust error handling.

### **Suggested Project Structure**

```
lyricflow/
├── lyricflow/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── endpoints.py
│   │   └── models.py
│   ├── cli/
│   │   ├── __init__.py
│   │   └── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── audio_handler.py
│   │   ├── lyrics_fetcher.py   # New
│   │   ├── lyrics_sync.py
│   │   ├── romanizer.py
│   │   ├── translator.py
│   │   └── whisper_gen.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── logging.py
│   └── py.typed             # For PEP 561 compliance
├── tests/
│   ├── ...
├── docs/
│   ├── ...
├── .env.example
├── config.yaml.example
├── pyproject.toml
└── README.md
```

---

### **I. Functional Specifications**

#### **Core Modules**

1.  **`audio_handler`**
    *   **Library:** Use `mutagen` for broad format support (ID3 tags for MP3/M4A, Vorbis comments for FLAC/OGG, etc.).
    *   **Metadata Extraction:** Read standard tags (Title, Artist, Album) to aid in lyric searches.
    *   **Lyric Tag Detection:** Detect existing synced (SYLT, USLT) and unsynced (ULT) lyric tags. Provide a clear hierarchy for which tag to prioritize.
    *   **Embedding:** Embed new and updated tags, specifically `Lyrics`, `Romanized_Lyrics`, and a synced format like SYLT. Ensure existing unrelated tags are preserved.

2.  **`lyrics_fetcher` (New Module)**
    *   **Purpose:** Before resorting to ASR, attempt to fetch lyrics from online databases.
    *   **Strategy:** Use audio metadata (Title, Artist) to query sources.
    *   **Sources:** Support for pluggable sources like Musixmatch, Genius, or other LRC providers.
    *   **Output:** Return either plain text lyrics or, ideally, a time-synced `.lrc` string.

3.  **`lyrics_sync`**
    *   **Refined Workflow:**
        1.  Check for existing synced and romanized lyrics in tags. If present, the task is complete unless `--overwrite` is used.
        2.  If not, check for any existing synced lyrics (e.g., SYLT). If found, extract, romanize, and embed them back.
        3.  If no embedded lyrics, search the local directory for a matching `.lrc` file (e.g., `{basename}.lrc`).
        4.  If found, romanize its content, create `{basename}_romaji.lrc`, and embed it.
        5.  **New Step:** If no local file, trigger the `lyrics_fetcher` module. If successful, process and embed the fetched lyrics.
        6.  If all else fails, flag the file for ASR generation.
    *   **Output:** Embeds romanized synced lyrics and sets the `Romanized_Lyrics` tag.

4.  **`romanizer`**
    *   **AI-Based:**
        *   Support for Gemini and OpenAI APIs via a unified interface.
        *   Allow custom base URLs for compatibility with local LLMs or proxy servers.
        *   Implement **caching** (e.g., using `diskcache`) for API requests to avoid redundant calls and costs.
    *   **Local Fallback:**
        *   Provide deterministic local romanization for Japanese (`pykakasi`, `fugashi`) and other languages where applicable.
        *   The system should automatically fall back to local methods if API keys are missing or API calls fail.
    *   **Language Detection:** Optionally use a library like `langdetect` to identify the source language before processing.

5.  **`translator`**
    *   **Functionality:** Optional translation of original or romanized lyrics via Gemini/OpenAI API.
    *   **Output Format:** Generate a combined, multi-line text file or embed in a custom tag, showing parallel lyrics. Example:
        ```
        [00:15.50]ありがとう (arigatou) [Thank you]
        ```

6.  **`whisper_lyric_gen`**
    *   **Model Selection:** Allow users to specify the Whisper model size (`tiny`, `base`, `small`, `medium`, `large`) in the config to balance speed and accuracy.
    *   **Preprocessing:** Implement **Voice Activity Detection (VAD)** before transcription to remove silent segments and improve ASR accuracy.
    *   **Timestamp Accuracy:** Use advanced features of Whisper implementations (like `whisper-timestamped` or Stable-TSS) for more precise word-level timestamps.
    *   **Process Feedback:** The module should be able to report progress (e.g., percentage complete) to the calling interface (CLI/API).

### **II. CLI Tool (using `click`)**

*   **Progress Indicators:** Use `rich` or `tqdm` to display progress bars for directory scans and long-running tasks like Whisper generation.
*   **Commands:**
    *   `lyricflow process <path>`: Process a single audio file or recursively process a directory.
    *   `lyricflow romanize <input>`: Romanize text from stdin, a string argument, or a file.
    *   `lyricflow translate <input>`: Translate text from stdin, a string argument, or a file.
    *   `lyricflow generate <audio_file>`: Purely generate lyrics for a file without fetching or other checks.
    *   `lyricflow config`: View the current configuration.
*   **Flags:**
    *   `--api [openai|gemini|local]`: Specify the primary API for romanization/translation.
    *   `--base-url <url>`: Custom base URL for self-hosted models.
    *   `--translate-to <lang_code>`: Enable translation and specify the target language (e.g., `en`).
    *   `--no-embed`: Generate `.lrc` files but do not write tags to the audio file.
    *   `--overwrite`: Force reprocessing and overwriting of existing lyric tags.
    *   `--dry-run`: Simulate the process and print the actions that would be taken without modifying any files.
    *   `-v, --verbose`: Provide detailed logging output.

### **III. FastAPI Service**

*   **Endpoints:**
    *   `POST /process`: Upload an audio file. Immediately returns a `task_id`.
    *   `GET /status/{task_id}`: Poll this endpoint to get the status (`pending`, `processing`, `complete`, `failed`), progress percentage, and final result.
    *   `POST /romanize`: Accepts JSON with text, returns romanized text.
    *   `POST /translate`: Accepts JSON with text, returns translated text.
    *   `POST /generate`: Upload audio, returns a `task_id` for ASR generation.
*   **Async Processing:** Use `Celery` or FastAPI's `BackgroundTasks` to handle long-running audio processing without blocking the server.
*   **WebSockets:** For a more advanced client, provide a WebSocket endpoint (`WS /ws/status/{task_id}`) to push real-time progress updates.
*   **API Models:** Use Pydantic for clear request/response models and automatic validation/documentation.
    ```python
    class ProcessResponse(BaseModel):
        task_id: str
        status: str
        message: str

    class StatusResponse(BaseModel):
        status: str
        progress: float
        result: Optional[dict]
        error: Optional[str]
    ```
*   **Security:** Implement API key authentication using FastAPI's `Security` dependencies.

### **IV. Configuration**

*   **Format:** A single `config.yaml` or `.env` file in the user's home directory or the project root.
*   **Example (`config.yaml`):**
    ```yaml
    # API Configurations
    api:
      default_provider: gemini
      openai:
        api_key: "sk-..."
        base_url: "https://api.openai.com/v1"
      gemini:
        api_key: "..."

    # Processing Rules
    processing:
      language: auto # or specify default like 'ja' for Japanese
      translate_target: en
      skip_existing_lyrics: true
      on_failure: skip # or 'log_error'

    # ASR (Whisper) Settings
    whisper:
      model_path: "medium" # Path or Hugging Face model name
      device: "cuda" # or "cpu"

    # Caching
    caching:
      enabled: true
      ttl: 2592000 # 30 days in seconds
    ```

### **V. Output**

*   **Audio File:** The original file is modified in-place (or a new file is created) with the embedded `Romanized_Lyrics` and/or SYLT tags.
*   **Sidecar Files:** Optional generation of `{basename}.lrc` and `{basename}_romaji.lrc`.
*   **JSON Report (CLI/API):** A detailed JSON object summarizing the operation.
    ```json
    {
      "file": "song.flac",
      "status": "success",
      "steps_taken": [
        "Loaded metadata: 'Artist Name - Song Title'",
        "No embedded lyrics found.",
        "Local .lrc file not found.",
        "Fetched lyrics from Musixmatch.",
        "Romanized lyrics using 'Gemini API'.",
        "Embedded SYLT and 'Romanized_Lyrics' tags."
      ],
      "metadata": {
        "original": "...",
        "romanized": "...",
        "lrc_synced": "[00:12.34] Romanized line..."
      }
    }
    ```

### **VI. Testing and Documentation**

*   **Testing:**
    *   Use `pytest` for unit and integration tests.
    *   Mock API calls to external services (`requests-mock`) to test logic without network dependency.
    *   Create a sample library of audio files with and without tags for testing the `audio_handler`.
*   **Documentation:**
    *   **Code:** Use Google-style docstrings and generate documentation with `Sphinx`.
    *   **API:** FastAPI will auto-generate interactive Swagger UI and ReDoc documentation from the Pydantic models and endpoint definitions.
    *   **User Guide:** A comprehensive `README.md` explaining CLI usage, configuration, and API endpoints.

### **VII. Packaging and Dependencies**

*   **Packaging:** Use `pyproject.toml` with `astral uv` and `Hatch` for dependency management and packaging.
*   **Optional Dependencies:** Define extras for features that require heavy dependencies, allowing for a lightweight default installation.
    *   `pip install lyricflow` (core functionality)
    *   `pip install lyricflow[openai]`
    *   `pip install lyricflow[whisper]`
    *   `pip install lyricflow[all]`