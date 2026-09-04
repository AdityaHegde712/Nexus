# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-api-python-client>=2.100.0",
#     "google-auth-oauthlib>=1.2.0",
#     "google-auth-httplib2>=0.2.0",
# ]
# ///
"""Google Docs-Inator: Converts Markdown files to styled Google Docs and publishes to Google Drive."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Dict, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
]

SKILL_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = SKILL_DIR / "config.json"
LOOKUP_PATH = SKILL_DIR / "id_lookup.json"
DEFAULT_CREDS_PATH = SKILL_DIR / "credentials.json"
DEFAULT_TOKEN_PATH = SKILL_DIR / "token.json"


def extract_title_from_markdown(content: str, fallback: str) -> str:
    """Extract first H1 header from markdown, or fall back to provided name."""
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("# ") and not line.startswith("##"):
            title = line[2:].strip()
            if title:
                return title
    return fallback


def load_json_config(path: Path) -> Dict[str, Any]:
    """Load JSON config if exists, returning empty dict on failure."""
    if not path.is_file():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def resolve_destination(
    folder_arg: Optional[str],
    folder_id_arg: Optional[str],
    drive_id_arg: Optional[str],
    lookup_map: Dict[str, Any],
    config_map: Dict[str, Any],
) -> Optional[str]:
    """Resolve target folder ID from CLI arguments, lookup map, or config defaults."""
    # 1. Explicit --folder-id
    if folder_id_arg and folder_id_arg.strip():
        return folder_id_arg.strip()

    # 2. --folder alias or explicit ID
    if folder_arg and folder_arg.strip():
        val = folder_arg.strip()
        if val in lookup_map and lookup_map[val]:
            return str(lookup_map[val]).strip()
        # Case-insensitive check
        for k, v in lookup_map.items():
            if k.lower() == val.lower() and v:
                return str(v).strip()
        return val

    # 3. Explicit --drive-id
    if drive_id_arg and drive_id_arg.strip():
        return drive_id_arg.strip()

    # 4. Fallback to config.json defaults
    default_folder = config_map.get("default_folder_id", "").strip()
    if default_folder:
        return default_folder

    default_drive = config_map.get("default_drive_id", "").strip()
    if default_drive:
        return default_drive

    return None


def convert_markdown_to_docx(md_path: Path, output_docx_path: Path) -> None:
    """Invoke pandoc to convert markdown to docx."""
    pandoc_bin = shutil.which("pandoc") or os.environ.get("PANDOC_PATH")
    if not pandoc_bin:
        raise RuntimeError(
            "Pandoc executable not found on PATH. Ensure Pandoc is installed and on system PATH."
        )

    cmd = [
        pandoc_bin,
        str(md_path),
        "-f",
        "markdown",
        "-t",
        "docx",
        "-s",
        "-o",
        str(output_docx_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if result.returncode != 0:
        raise RuntimeError(f"Pandoc conversion failed: {result.stderr.strip()}")


def get_authenticated_service(creds_path: Path, token_path: Path) -> Any:
    """Obtain authenticated Google Drive API v3 service using cached token or OAuth flow."""
    creds = None
    if token_path.is_file():
        try:
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        except Exception:
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not creds_path.is_file():
                raise FileNotFoundError(
                    f"Credentials file not found at: {creds_path}\n"
                    f"Please place your Google OAuth client ID credentials JSON at {creds_path}."
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
            creds = flow.run_local_server(port=0)

        # Cache refreshed or new token
        token_path.parent.mkdir(parents=True, exist_ok=True)
        with open(token_path, "w", encoding="utf-8") as token_file:
            token_file.write(creds.to_json())

    return build("drive", "v3", credentials=creds)


def upload_docx_as_google_doc(
    service: Any,
    docx_path: Path,
    title: str,
    target_folder_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Upload docx file to Google Drive and convert to native Google Doc."""
    file_metadata: Dict[str, Any] = {
        "name": title,
        "mimeType": "application/vnd.google-apps.document",
    }

    if target_folder_id:
        file_metadata["parents"] = [target_folder_id]

    media = MediaFileUpload(
        str(docx_path),
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        resumable=True,
    )

    file_item = (
        service.files()
        .create(
            body=file_metadata,
            media_body=media,
            supportsAllDrives=True,
            fields="id, name, webViewLink, parents",
        )
        .execute()
    )

    return file_item


def parse_arguments() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Convert Markdown to Google Doc and publish to Google Drive."
    )
    parser.add_argument(
        "-f",
        "--file",
        required=True,
        type=Path,
        help="Path to source Markdown (.md) file",
    )
    parser.add_argument(
        "-t",
        "--title",
        type=str,
        default=None,
        help="Title for the Google Doc (defaults to Markdown H1 or filename)",
    )
    parser.add_argument(
        "-d",
        "--folder",
        type=str,
        default=None,
        help="Folder alias from id_lookup.json (e.g. 'docs') or direct Folder ID",
    )
    parser.add_argument(
        "--folder-id",
        type=str,
        default=None,
        help="Direct Google Drive / Shared Drive folder ID",
    )
    parser.add_argument(
        "--drive-id",
        type=str,
        default=None,
        help="Google Shared Drive ID (root upload)",
    )
    parser.add_argument(
        "-c",
        "--credentials",
        type=Path,
        default=DEFAULT_CREDS_PATH,
        help=f"Path to credentials.json (default: {DEFAULT_CREDS_PATH})",
    )
    parser.add_argument(
        "-k",
        "--token",
        type=Path,
        default=DEFAULT_TOKEN_PATH,
        help=f"Path to token.json cache (default: {DEFAULT_TOKEN_PATH})",
    )
    return parser.parse_args()


def main() -> int:
    """Main execution routine."""
    args = parse_arguments()

    md_file = args.file.resolve()
    if not md_file.is_file():
        print(
            json.dumps({"status": "error", "message": f"File not found: {md_file}"}),
            file=sys.stderr,
        )
        return 1

    try:
        md_content = md_file.read_text(encoding="utf-8")
    except Exception as e:
        print(
            json.dumps({"status": "error", "message": f"Failed reading file: {e}"}),
            file=sys.stderr,
        )
        return 1

    doc_title = args.title or extract_title_from_markdown(md_content, fallback=md_file.stem)

    config_map = load_json_config(CONFIG_PATH)
    lookup_map = load_json_config(LOOKUP_PATH)

    target_dest = resolve_destination(
        folder_arg=args.folder,
        folder_id_arg=args.folder_id,
        drive_id_arg=args.drive_id,
        lookup_map=lookup_map,
        config_map=config_map,
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_docx = Path(temp_dir) / f"{md_file.stem}.docx"

        try:
            convert_markdown_to_docx(md_file, temp_docx)
        except Exception as e:
            print(
                json.dumps({"status": "error", "message": f"Conversion error: {e}"}),
                file=sys.stderr,
            )
            return 1

        try:
            service = get_authenticated_service(args.credentials, args.token)
            result = upload_docx_as_google_doc(
                service=service,
                docx_path=temp_docx,
                title=doc_title,
                target_folder_id=target_dest,
            )
        except Exception as e:
            print(
                json.dumps({"status": "error", "message": f"Google Drive API error: {e}"}),
                file=sys.stderr,
            )
            return 1

    output = {
        "status": "success",
        "document_id": result.get("id"),
        "title": result.get("name", doc_title),
        "url": result.get("webViewLink", f"https://docs.google.com/document/d/{result.get('id')}/edit"),
        "target_folder_id": target_dest,
    }
    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
