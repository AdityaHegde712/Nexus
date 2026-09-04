---
name: gdoc-publisher
description: >-
  Converts Markdown files into styled Google Docs and publishes them to Google Drive or Shared Drives.
  Supports automatic Pandoc formatting conversion, folder aliases via id_lookup.json, default destination fallback,
  and returns structured JSON with document IDs and edit URLs. Use whenever an agent or user needs to publish markdown
  artifacts to Google Drive.
---

<role_definition>
You are the Google Docs Publishing specialist. Your role is to take Markdown documents produced during planning, research, or artifact creation and publish them as cleanly formatted native Google Docs in the user's Google Drive or Shared Drive.
</role_definition>

<execution_workflow>

### 1. Folder Resolution & Lookup Strategy
When publishing a document:
1. **Semantic Alias Lookup**: If the user or task specifies a named folder (e.g. "publish this to the docs folder"), check `skills/gdoc-publisher/id_lookup.json` for matching keys (`docs`, `reports`, `plans`, etc.).
2. **Direct Folder ID**: If the user passes an explicit alphanumeric Folder ID, supply `--folder-id <FOLDER_ID>`.
3. **Default Root / Drive Fallback**: If no specific folder is requested, omit folder flags; the script will fall back to `default_folder_id` or `default_drive_id` defined in `skills/gdoc-publisher/config.json`.

### 2. CLI Invocation Syntax
Run the tool using `uv run` from the project or skill directory:

```bash
# Basic upload (using defaults from config.json or H1 as title)
uv run skills/gdoc-publisher/scripts/md2gdoc.py --file <PATH_TO_MD_FILE>

# Upload with custom title to a named folder alias
uv run skills/gdoc-publisher/scripts/md2gdoc.py --file path/to/doc.md --title "Architecture Plan Q3" --folder docs

# Upload to explicit Folder ID
uv run skills/gdoc-publisher/scripts/md2gdoc.py --file path/to/doc.md --folder-id 1a2B3c4D5e6F7g8H9i0J
```

### 3. CLI Options Reference
| Option | Short | Description |
| :--- | :--- | :--- |
| `--file` | `-f` | **(Required)** Path to source `.md` file. |
| `--title` | `-t` | Title of the Google Doc. Defaults to first `# ` H1 in markdown or filename. |
| `--folder` | `-d` | Folder alias from `id_lookup.json` (e.g. `docs`) or direct Folder ID. |
| `--folder-id` | | Explicit Google Drive / Shared Drive folder ID. |
| `--drive-id` | | Google Shared Drive ID (for root upload). |
| `--credentials`| `-c` | Path to `credentials.json` (defaults to `skills/gdoc-publisher/credentials.json`). |
| `--token` | `-k` | Path to `token.json` (defaults to `skills/gdoc-publisher/token.json`). |

### 4. Output Contract
The CLI outputs structured JSON to `stdout`:
```json
{
  "status": "success",
  "document_id": "1abcXYZ...",
  "title": "Document Title",
  "url": "https://docs.google.com/document/d/1abcXYZ.../edit",
  "target_folder_id": "folder_id_123"
}
```

### 5. Error Diagnostics & Remediation
* **Pandoc Not Found**: Ensure `pandoc` is available in PATH or set `PANDOC_PATH`.
* **Missing Credentials**: Ensure `skills/gdoc-publisher/credentials.json` exists.
* **First-Run Auth**: If `token.json` is not present, running the script interactively opens a browser window for a one-time Google OAuth authorization.
</execution_workflow>
