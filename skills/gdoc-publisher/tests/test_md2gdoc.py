"""Unit tests for md2gdoc.py publisher."""

from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

# Ensure skill directory and script are importable
SKILL_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_DIR / "scripts"))

import md2gdoc


class TestMd2Gdoc(unittest.TestCase):
    """Test suite for Markdown to Google Doc conversion and publishing logic."""

    def test_extract_title_from_markdown_h1(self):
        content = "# My Custom Report Title\n\nSome body text."
        title = md2gdoc.extract_title_from_markdown(content, fallback="default_name")
        self.assertEqual(title, "My Custom Report Title")

    def test_extract_title_from_markdown_fallback(self):
        content = "## Subheading Only\n\nNo top level header."
        title = md2gdoc.extract_title_from_markdown(content, fallback="fallback_name")
        self.assertEqual(title, "fallback_name")

    def test_resolve_destination_explicit_folder_id(self):
        dest = md2gdoc.resolve_destination(
            folder_arg="ignored_alias",
            folder_id_arg="explicit_12345",
            drive_id_arg="drive_999",
            lookup_map={"ignored_alias": "lookup_111"},
            config_map={"default_folder_id": "cfg_222"},
        )
        self.assertEqual(dest, "explicit_12345")

    def test_resolve_destination_lookup_alias(self):
        dest = md2gdoc.resolve_destination(
            folder_arg="docs",
            folder_id_arg=None,
            drive_id_arg=None,
            lookup_map={"docs": "folder_docs_id_abc"},
            config_map={"default_folder_id": "cfg_default"},
        )
        self.assertEqual(dest, "folder_docs_id_abc")

    def test_resolve_destination_lookup_case_insensitive(self):
        dest = md2gdoc.resolve_destination(
            folder_arg="DOCS",
            folder_id_arg=None,
            drive_id_arg=None,
            lookup_map={"docs": "folder_docs_id_abc"},
            config_map={},
        )
        self.assertEqual(dest, "folder_docs_id_abc")

    def test_resolve_destination_unmapped_folder_arg_as_direct_id(self):
        dest = md2gdoc.resolve_destination(
            folder_arg="random_folder_id_xyz",
            folder_id_arg=None,
            drive_id_arg=None,
            lookup_map={"docs": "folder_docs_id_abc"},
            config_map={},
        )
        self.assertEqual(dest, "random_folder_id_xyz")

    def test_resolve_destination_config_defaults(self):
        dest = md2gdoc.resolve_destination(
            folder_arg=None,
            folder_id_arg=None,
            drive_id_arg=None,
            lookup_map={"docs": "folder_docs_id_abc"},
            config_map={"default_folder_id": "cfg_folder_default_id"},
        )
        self.assertEqual(dest, "cfg_folder_default_id")

    def test_resolve_destination_drive_id_fallback(self):
        dest = md2gdoc.resolve_destination(
            folder_arg=None,
            folder_id_arg=None,
            drive_id_arg=None,
            lookup_map={},
            config_map={"default_drive_id": "cfg_drive_root_id"},
        )
        self.assertEqual(dest, "cfg_drive_root_id")

    def test_convert_markdown_to_docx_execution(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            md_file = Path(tmp_dir) / "sample.md"
            docx_file = Path(tmp_dir) / "sample.docx"
            md_file.write_text(
                "# Sample Title\n\n| Header A | Header B |\n| --- | --- |\n| 1 | 2 |\n\n```python\nprint('hello')\n```",
                encoding="utf-8",
            )
            md2gdoc.convert_markdown_to_docx(md_file, docx_file)
            self.assertTrue(docx_file.is_file())
            self.assertGreater(docx_file.stat().st_size, 0)

    @patch("md2gdoc.MediaFileUpload")
    def test_upload_docx_as_google_doc_mock(self, mock_media):
        mock_service = MagicMock()
        mock_files = MagicMock()
        mock_create = MagicMock()
        mock_service.files.return_value = mock_files
        mock_files.create.return_value = mock_create
        mock_create.execute.return_value = {
            "id": "doc_id_12345",
            "name": "Test Document",
            "webViewLink": "https://docs.google.com/document/d/doc_id_12345/edit",
        }

        result = md2gdoc.upload_docx_as_google_doc(
            service=mock_service,
            docx_path=Path("dummy.docx"),
            title="Test Document",
            target_folder_id="target_folder_789",
        )

        mock_files.create.assert_called_once()
        call_kwargs = mock_files.create.call_args[1]
        self.assertEqual(call_kwargs["body"]["name"], "Test Document")
        self.assertEqual(call_kwargs["body"]["mimeType"], "application/vnd.google-apps.document")
        self.assertEqual(call_kwargs["body"]["parents"], ["target_folder_789"])
        self.assertTrue(call_kwargs["supportsAllDrives"])
        self.assertEqual(result["id"], "doc_id_12345")


if __name__ == "__main__":
    unittest.main()
