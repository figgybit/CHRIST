"""
Unit tests for consciousness parsers.
"""

import pytest
import tempfile
import json
from pathlib import Path
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from consciousness.parsers import EmailParser, TextFileParser, ChatParser


class TestEmailParser:
    """Test email parsing functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = EmailParser()

    def test_parse_simple_email(self, tmp_path):
        """Test parsing a simple email file."""
        # Create a test email
        email_content = """From: sender@example.com
To: recipient@example.com
Subject: Test Email
Date: Mon, 20 Jan 2025 10:30:00 +0000

This is a test email body.
"""
        email_file = tmp_path / "test.eml"
        email_file.write_text(email_content)

        # Parse the email
        result = self.parser.parse_eml_file(str(email_file))

        # Assertions
        assert result['type'] == 'email'
        assert result['headers']['from'] == 'sender@example.com'
        assert result['headers']['to'] == 'recipient@example.com'
        assert result['headers']['subject'] == 'Test Email'
        assert 'test email body' in result['content']['plain'].lower()

    def test_parse_email_with_attachments(self, tmp_path):
        """Test parsing email with attachments."""
        # Create multipart email
        email_content = """From: sender@example.com
To: recipient@example.com
Subject: Email with Attachment
Date: Mon, 20 Jan 2025 10:30:00 +0000
Content-Type: multipart/mixed; boundary="boundary123"

--boundary123
Content-Type: text/plain

Email body text

--boundary123
Content-Type: application/pdf
Content-Disposition: attachment; filename="document.pdf"

[PDF content here]
--boundary123--
"""
        email_file = tmp_path / "test_attachment.eml"
        email_file.write_text(email_content)

        result = self.parser.parse_eml_file(str(email_file))

        assert result['type'] == 'email'
        assert len(result['attachments']) > 0
        assert result['metadata']['has_attachments'] is True

    def test_extract_message_data_handles_errors(self):
        """Test that message extraction handles errors gracefully."""
        import email
        msg = email.message_from_string("Invalid: email")
        result = self.parser._extract_message_data(msg)
        assert result['type'] == 'email'
        assert 'id' in result


class TestTextFileParser:
    """Test text file parsing functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = TextFileParser()

    def test_parse_text_file(self, tmp_path):
        """Test parsing a simple text file."""
        # Create test file
        content = "This is a test file.\nIt has multiple lines.\nLine 3."
        text_file = tmp_path / "test.txt"
        text_file.write_text(content)

        # Parse file
        result = self.parser.parse_file(str(text_file))

        # Assertions
        assert result['type'] == 'text_file'
        assert result['content']['text'] == content
        assert result['content']['format'] == '.txt'
        assert result['metadata']['line_count'] == 3
        assert result['metadata']['word_count'] == 11

    def test_parse_markdown_file(self, tmp_path):
        """Test parsing a markdown file."""
        content = "# Title\n\nSome **bold** text."
        md_file = tmp_path / "test.md"
        md_file.write_text(content)

        result = self.parser.parse_file(str(md_file))

        assert result['type'] == 'text_file'
        assert result['content']['format'] == '.md'
        assert '# Title' in result['content']['text']

    def test_parse_nonexistent_file(self):
        """Test parsing a file that doesn't exist."""
        with pytest.raises(FileNotFoundError):
            self.parser.parse_file('/nonexistent/file.txt')

    def test_detect_encoding(self, tmp_path):
        """Test encoding detection."""
        # Create file with UTF-8 encoding
        text_file = tmp_path / "utf8.txt"
        text_file.write_text("UTF-8 text with émoji 🎉", encoding='utf-8')

        encoding = self.parser._detect_encoding(str(text_file))
        assert encoding.lower() in ['utf-8', 'ascii']


class TestChatParser:
    """Test chat export parsing functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = ChatParser()

    def test_parse_whatsapp_export(self, tmp_path):
        """Test parsing WhatsApp chat export."""
        chat_content = """1/20/25, 10:30 AM - John: Hello there!
1/20/25, 10:31 AM - Jane: Hi John!
1/20/25, 10:32 AM - John: How are you?"""

        chat_file = tmp_path / "whatsapp_chat.txt"
        chat_file.write_text(chat_content)

        results = self.parser.parse_whatsapp_export(str(chat_file))

        assert len(results) == 3
        assert results[0]['platform'] == 'whatsapp'
        assert results[0]['sender'] == 'John'
        assert 'Hello there!' in results[0]['content']['text']

    def test_parse_discord_export(self, tmp_path):
        """Test parsing Discord chat export."""
        discord_data = {
            "channel": {"name": "general"},
            "guild": {"name": "Test Server"},
            "messages": [
                {
                    "id": "123",
                    "timestamp": "2025-01-20T10:30:00Z",
                    "author": {"name": "User1"},
                    "content": "Test message",
                    "attachments": [],
                    "reactions": []
                }
            ]
        }

        discord_file = tmp_path / "discord_export.json"
        discord_file.write_text(json.dumps(discord_data))

        results = self.parser.parse_discord_export(str(discord_file))

        assert len(results) == 1
        assert results[0]['platform'] == 'discord'
        assert results[0]['sender'] == 'User1'
        assert results[0]['content']['text'] == 'Test message'


class TestUniversalParser:
    """Test universal parser delegation."""

    def test_parse_email(self, tmp_path):
        """Test that universal parser correctly delegates email files."""
        from consciousness.parsers import UniversalParser

        email_content = """From: test@example.com
Subject: Test
Date: Mon, 20 Jan 2025 10:30:00 +0000

Body"""
        email_file = tmp_path / "test.eml"
        email_file.write_text(email_content)

        parser = UniversalParser()
        result = parser.parse(str(email_file))

        assert result['type'] == 'email'

    def test_parse_text(self, tmp_path):
        """Test that universal parser correctly delegates text files."""
        from consciousness.parsers import UniversalParser

        text_file = tmp_path / "test.txt"
        text_file.write_text("Test content")

        parser = UniversalParser()
        result = parser.parse(str(text_file))

        assert result['type'] == 'text_file'

    def test_unsupported_format(self, tmp_path):
        """Test handling of unsupported file formats."""
        from consciousness.parsers import UniversalParser

        unsupported_file = tmp_path / "test.xyz"
        unsupported_file.write_text("content")

        parser = UniversalParser()
        with pytest.raises(ValueError, match="Unsupported file format"):
            parser.parse(str(unsupported_file))


if __name__ == '__main__':
    pytest.main([__file__, '-v'])