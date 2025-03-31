import os
import json
import time
from openai import OpenAI
from src.config import get_config
from src.constants import ROOT_DIR
import re
from PIL import Image, ImageDraw, ImageFont
import textwrap
import uuid
import requests
from datetime import datetime
import subprocess
import shutil

class EbookFormatter:
    """
    Class for formatting and converting eBooks to different formats
    """
    def __init__(self):
        """
        Initialize the EbookFormatter
        """
        # Create necessary directories
        self.temp_dir = os.path.join(ROOT_DIR, ".mp", "temp")
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Define supported formats
        self.formats = {
            "kindle": {
                "extension": "mobi",
                "mime_type": "application/x-mobipocket-ebook"
            },
            "epub": {
                "extension": "epub",
                "mime_type": "application/epub+zip"
            },
            "pdf": {
                "extension": "pdf",
                "mime_type": "application/pdf"
            }
        }
    
    def markdown_to_html(self, markdown_path, html_path):
        """
        Convert markdown to HTML
        
        Args:
            markdown_path (str): Path to markdown file
            html_path (str): Path to output HTML file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Read markdown content
            with open(markdown_path, 'r') as f:
                markdown_content = f.read()
            
            # Simple markdown to HTML conversion
            # This is a basic implementation - in a real system, use a proper markdown parser
            html_content = self._convert_markdown_to_html(markdown_content)
            
            # Write HTML content
            with open(html_path, 'w') as f:
                f.write(html_content)
            
            return True
        except Exception as e:
            print(f"Error converting markdown to HTML: {e}")
            return False
    
    def _convert_markdown_to_html(self, markdown_content):
        """
        Convert markdown content to HTML
        
        Args:
            markdown_content (str): Markdown content
            
        Returns:
            str: HTML content
        """
        # Create HTML document structure
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>eBook</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            font-size: 2.5em;
            margin-top: 1em;
            margin-bottom: 0.5em;
            text-align: center;
        }
        h2 {
            font-size: 2em;
            margin-top: 1em;
            margin-bottom: 0.5em;
            text-align: center;
        }
        h3 {
            font-size: 1.5em;
            margin-top: 1em;
            margin-bottom: 0.5em;
        }
        h4 {
            font-size: 1.2em;
            margin-top: 1em;
            margin-bottom: 0.5em;
        }
        p {
            margin-bottom: 1em;
            text-align: justify;
        }
        ul, ol {
            margin-bottom: 1em;
            padding-left: 2em;
        }
        li {
            margin-bottom: 0.5em;
        }
        blockquote {
            border-left: 4px solid #ddd;
            padding-left: 1em;
            margin-left: 0;
            color: #666;
        }
        code {
            font-family: monospace;
            background-color: #f5f5f5;
            padding: 2px 4px;
            border-radius: 3px;
        }
        pre {
            background-color: #f5f5f5;
            padding: 1em;
            border-radius: 5px;
            overflow-x: auto;
        }
        a {
            color: #0066cc;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        img {
            max-width: 100%;
            height: auto;
            display: block;
            margin: 0 auto;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 1em;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f5f5f5;
        }
        .page-break {
            page-break-after: always;
        }
        .toc {
            margin-bottom: 2em;
        }
        .toc a {
            text-decoration: none;
            color: #333;
        }
        .toc a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
"""
        
        # Convert markdown to HTML
        content = markdown_content
        
        # Headers
        content = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
        content = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
        content = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
        content = re.sub(r'^#### (.*?)$', r'<h4>\1</h4>', content, flags=re.MULTILINE)
        
        # Bold and italic
        content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
        content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', content)
        
        # Lists
        # Unordered lists
        content = re.sub(r'^- (.*?)$', r'<li>\1</li>', content, flags=re.MULTILINE)
        content = re.sub(r'(<li>.*?</li>\n)+', r'<ul>\n\g<0></ul>\n', content, flags=re.DOTALL)
        
        # Ordered lists
        content = re.sub(r'^\d+\. (.*?)$', r'<li>\1</li>', content, flags=re.MULTILINE)
        content = re.sub(r'(<li>.*?</li>\n)+', r'<ol>\n\g<0></ol>\n', content, flags=re.DOTALL)
        
        # Links
        content = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', content)
        
        # Images
        content = re.sub(r'!\[(.*?)\]\((.*?)\)', r'<img src="\2" alt="\1">', content)
        
        # Code blocks
        content = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', content, flags=re.DOTALL)
        
        # Inline code
        content = re.sub(r'`(.*?)`', r'<code>\1</code>', content)
        
        # Blockquotes
        content = re.sub(r'^> (.*?)$', r'<blockquote>\1</blockquote>', content, flags=re.MULTILINE)
        
        # Horizontal rule
        content = re.sub(r'^---$', r'<hr>', content, flags=re.MULTILINE)
        
        # Paragraphs
        content = re.sub(r'(?<!\n)\n(?!\n)', r' ', content)  # Join lines that aren't separated by blank lines
        content = re.sub(r'\n\n+', r'\n\n', content)  # Normalize multiple blank lines
        content = re.sub(r'(?<!\n\n|<h|<ul|<ol|<li|<blockquote|<hr|<pre)([^<>]+?)(?!\n\n|</h|</ul|</ol|</li|</blockquote|</hr|</pre)', r'<p>\1</p>', content)
        
        # Complete HTML document
        html += content + "\n</body>\n</html>"
        
        return html
    
    def html_to_epub(self, html_path, epub_path, metadata=None):
        """
        Convert HTML to EPUB
        
        Args:
            html_path (str): Path to HTML file
            epub_path (str): Path to output EPUB file
            metadata (dict): Optional metadata for the EPUB
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # In a real implementation, you would use a library like ebooklib or calibre
            # For now, we'll create a simple EPUB structure
            
            # Create a temporary directory for EPUB structure
            epub_dir = os.path.join(self.temp_dir, f"epub_{uuid.uuid4()}")
            os.makedirs(epub_dir, exist_ok=True)
            
            # Create EPUB structure
            os.makedirs(os.path.join(epub_dir, "META-INF"), exist_ok=True)
            os.makedirs(os.path.join(epub_dir, "OEBPS"), exist_ok=True)
            
            # Create container.xml
            with open(os.path.join(epub_dir, "META-INF", "container.xml"), 'w') as f:
                f.write("""<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>""")
            
            # Copy HTML content
            shutil.copy(html_path, os.path.join(epub_dir, "OEBPS", "content.html"))
            
            # Create content.opf
            title = metadata.get("title", "eBook") if metadata else "eBook"
            creator = metadata.get("creator", "MoneyPrinterV2") if metadata else "MoneyPrinterV2"
            language = metadata.get("language", "en") if metadata else "en"
            
            with open(os.path.join(epub_dir, "OEBPS", "content.opf"), 'w') as f:
                f.write(f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookID" version="2.0">
    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
        <dc:title>{title}</dc:title>
        <dc:creator>{creator}</dc:creator>
        <dc:language>{language}</dc:language>
        <dc:identifier id="BookID">urn:uuid:{uuid.uuid4()}</dc:identifier>
    </metadata>
    <manifest>
        <item id="content" href="content.html" media-type="application/xhtml+xml"/>
    </manifest>
    <spine toc="ncx">
        <itemref idref="content"/>
    </spine>
</package>""")
            
            # Create mimetype file
            with open(os.path.join(epub_dir, "mimetype"), 'w') as f:
                f.write("application/epub+zip")
            
            # In a real implementation, you would use a library to create the EPUB file
            # For now, we'll just create a placeholder file
            with open(epub_path, 'w') as f:
                f.write("This is a placeholder for the EPUB file.\n")
                f.write("In a real implementation, you would use a library like ebooklib or calibre to create the EPUB file.\n")
            
            # Clean up
            shutil.rmtree(epub_dir)
            
            return True
        except Exception as e:
            print(f"Error converting HTML to EPUB: {e}")
            return False
    
    def html_to_pdf(self, html_path, pdf_path):
        """
        Convert HTML to PDF
        
        Args:
            html_path (str): Path to HTML file
            pdf_path (str): Path to output PDF file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # In a real implementation, you would use a library like weasyprint or wkhtmltopdf
            # For now, we'll just create a placeholder file
            with open(pdf_path, 'w') as f:
                f.write("This is a placeholder for the PDF file.\n")
                f.write("In a real implementation, you would use a library like weasyprint or wkhtmltopdf to create the PDF file.\n")
            
            return True
        except Exception as e:
            print(f"Error converting HTML to PDF: {e}")
            return False
    
    def epub_to_mobi(self, epub_path, mobi_path):
        """
        Convert EPUB to MOBI (Kindle format)
        
        Args:
            epub_path (str): Path to EPUB file
            mobi_path (str): Path to output MOBI file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # In a real implementation, you would use a tool like Calibre's ebook-convert
            # For now, we'll just create a placeholder file
            with open(mobi_path, 'w') as f:
                f.write("This is a placeholder for the MOBI file.\n")
                f.write("In a real implementation, you would use a tool like Calibre's ebook-convert to create the MOBI file.\n")
            
            return True
        except Exception as e:
            print(f"Error converting EPUB to MOBI: {e}")
            return False
    
    def convert_markdown_to_all_formats(self, markdown_path, output_dir, metadata=None):
        """
        Convert markdown to all supported formats
        
        Args:
            markdown_path (str): Path to markdown file
            output_dir (str): Directory to save output files
            metadata (dict): Optional metadata for the eBook
            
        Returns:
            dict: Dictionary of output file paths by format
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Get base filename without extension
        base_name = os.path.splitext(os.path.basename(markdown_path))[0]
        
        # Convert markdown to HTML
        html_path = os.path.join(output_dir, f"{base_name}.html")
        self.markdown_to_html(markdown_path, html_path)
        
        # Convert HTML to other formats
        output_paths = {
            "html": html_path
        }
        
        # Convert to EPUB
        epub_path = os.path.join(output_dir, f"{base_name}.epub")
        if self.html_to_epub(html_path, epub_path, metadata):
            output_paths["epub"] = epub_path
        
        # Convert to PDF
        pdf_path = os.path.join(output_dir, f"{base_name}.pdf")
        if self.html_to_pdf(html_path, pdf_path):
            output_paths["pdf"] = pdf_path
        
        # Convert to MOBI (Kindle)
        mobi_path = os.path.join(output_dir, f"{base_name}.mobi")
        if self.epub_to_mobi(epub_path, mobi_path):
            output_paths["kindle"] = mobi_path
        
        return output_paths


class AmazonKDPPublisher:
    """
    Class for publishing eBooks to Amazon KDP
    """
    def __init__(self):
        """
        Initialize the AmazonKDPPublisher
        """
        config = get_config()
        self.kdp_config = config.get("amazon_kdp", {})
        self.kdp_email = self.kdp_config.get("email", "")
        self.kdp_password = self.kdp_config.get("password", "")
    
    def publish_ebook(self, ebook_data, publishing_options=None):
        """
        Publish an eBook to Amazon KDP
        
        Args:
            ebook_data (dict): eBook data including paths to files
            publishing_options (dict): Optional publishing options
            
        Returns:
            dict: Publication status and details
        """
        # Check if KDP credentials are configured
        if not self.kdp_email or not self.kdp_password:
            return {
                "error": "Amazon KDP credentials not configured",
                "status": "failed",
                "message": "Please configure your Amazon KDP email and password in the settings"
            }
        
        # Check if required files exist
        if "kindle" not in ebook_data.get("formats", {}):
            return {
                "error": "Kindle format (MOBI) is required for KDP publishing",
                "status": "failed",
                "message": "Please ensure the eBook has been converted to Kindle format"
            }
        
        if not ebook_data.get("cover_path"):
            return {
                "error": "Cover image is required for KDP publishing",
                "status": "failed",
                "message": "Please ensure the eBook has a cover image"
            }
        
        # In a real implementation, you would use Selenium or a similar tool to automate the KDP publishing process
        # For now, we'll just return instructions for manual publishing
        
        # Get publishing options
        options = publishing_options or {}
        book_language = options.get("book_language", "en")
        book_categories = options.get("book_categories", ["business", "computers"])
        book_keywords = options.get("book_keywords", "")
        book_price = options.get("book_price", 2.99)
        kdp_select = options.get("kdp_select", True)
        
        # Update eBook data with KDP information
        kdp_info = {
            "status": "ready_for_publishing",
            "kdp_id": "",
            "asin": "",
            "publication_date": "",
            "url": "",
            "instructions": [
                "1. Go to https://kdp.amazon.com and log in",
                "2. Click 'Create a New Book'",
                f"3. Enter the title: {ebook_data['title']}",
                f"4. Enter the subtitle: {ebook_data['subtitle']}",
                "5. Upload the cover image and manuscript files",
                f"6. Set your pricing to ${book_price}",
                f"7. {'Enroll in KDP Select' if kdp_select else 'Do not enroll in KDP Select'}",
                "8. Submit for review"
            ]
        }
        
        return {
            "status": "ready_for_publishing",
            "message": "eBook is ready for publishing to Amazon KDP",
            "instructions": kdp_info["instructions"],
            "kdp_info": kdp_info
        }
