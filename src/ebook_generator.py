import os
import json
import requests
from uuid import uuid4
from datetime import datetime
from src.openai_generator import OpenAIGenerator
from src.constants import ROOT_DIR

class EbookGenerator:
    """
    Class for generating and publishing ebooks with AI-generated content and cover images.
    Supports multiple formats including PDF, EPUB, and MOBI.
    """
    def __init__(self):
        """
        Initialize the EbookGenerator.
        """
        self.openai_generator = OpenAIGenerator()
        self.ebooks = []
        
    def generate_ebook(self, topic, format="epub", length="medium", chapters=5):
        """
        Generate a complete ebook with title, chapters, cover image, and metadata.
        
        Args:
            topic (str): The main topic for the ebook
            format (str): Output format (pdf, epub, mobi)
            length (str): Length of the ebook (short, medium, long)
            chapters (int): Number of chapters to generate
            
        Returns:
            dict: Ebook data including title, content, chapters, and file paths
        """
        # Determine word count based on length
        word_counts = {
            "short": 5000,
            "medium": 15000,
            "long": 30000
        }
        target_words = word_counts.get(length, 15000)
        words_per_chapter = target_words // chapters
        
        # Generate ebook title
        title = self._generate_ebook_title(topic)
        
        # Generate table of contents and chapter outlines
        toc_and_outlines = self._generate_toc_and_outlines(topic, title, chapters)
        
        # Generate chapters
        chapter_contents = []
        for i, chapter_outline in enumerate(toc_and_outlines["chapter_outlines"]):
            chapter_title = toc_and_outlines["chapter_titles"][i]
            chapter_content = self._generate_chapter_content(
                topic, 
                title, 
                chapter_title, 
                chapter_outline, 
                words_per_chapter
            )
            chapter_contents.append({
                "title": chapter_title,
                "content": chapter_content,
                "word_count": len(chapter_content.split())
            })
        
        # Generate cover image
        cover_prompt = self._generate_cover_prompt(topic, title)
        cover_path = self.openai_generator.generate_image(cover_prompt, size="1024x1024")
        
        # Create ebook object
        ebook = {
            "title": title,
            "topic": topic,
            "format": format,
            "chapters": chapter_contents,
            "toc": toc_and_outlines["chapter_titles"],
            "cover_path": cover_path,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "word_count": sum(chapter["word_count"] for chapter in chapter_contents),
            "description": toc_and_outlines["description"]
        }
        
        self.ebooks.append(ebook)
        return ebook
    
    def _generate_ebook_title(self, topic):
        """
        Generate an engaging ebook title.
        
        Args:
            topic (str): The topic to generate a title for
            
        Returns:
            str: Generated ebook title
        """
        system_message = "You are a professional book title creator who crafts compelling, marketable titles."
        
        prompt = f"""
        Create an engaging, professional ebook title about:
        
        {topic}
        
        The title should:
        - Be attention-grabbing and compelling
        - Appeal to readers interested in this topic
        - Be between 30-60 characters
        - Be suitable for a non-fiction ebook
        - Not use clickbait tactics
        
        Just provide the title text with no additional explanation or formatting.
        """
        
        title = self.openai_generator.generate_content(prompt, system_message, max_tokens=100)
        return title.strip() if title else f"The Complete Guide to {topic}"
    
    def _generate_toc_and_outlines(self, topic, title, num_chapters):
        """
        Generate table of contents and chapter outlines.
        
        Args:
            topic (str): The main topic
            title (str): The ebook title
            num_chapters (int): Number of chapters to generate
            
        Returns:
            dict: Table of contents and chapter outlines
        """
        system_message = "You are a professional book editor who creates well-structured book outlines."
        
        output_structure = {
            "description": "A compelling book description (150-200 words)",
            "chapter_titles": f"List of {num_chapters} chapter titles",
            "chapter_outlines": f"List of {num_chapters} chapter outlines, each with 3-5 bullet points"
        }
        
        prompt = f"""
        Create a detailed outline for an ebook with the title:
        
        "{title}"
        
        About the topic:
        
        {topic}
        
        Please provide:
        1. A compelling book description (150-200 words)
        2. A list of {num_chapters} chapter titles
        3. For each chapter, provide a brief outline with 3-5 bullet points of what should be covered
        
        The ebook should have a logical flow from beginning to end, with each chapter building on the previous one.
        """
        
        result = self.openai_generator.generate_structured_content(
            prompt, 
            system_message, 
            max_tokens=2000,
            output_structure=output_structure
        )
        
        # Fallback if structured generation fails
        if not result:
            result = {
                "description": f"A comprehensive guide to {topic}.",
                "chapter_titles": [f"Chapter {i+1}: Understanding {topic}" for i in range(num_chapters)],
                "chapter_outlines": [["Introduction", "Main concepts", "Practical applications"] for _ in range(num_chapters)]
            }
            
        return result
    
    def _generate_chapter_content(self, topic, book_title, chapter_title, chapter_outline, target_words):
        """
        Generate comprehensive content for a single chapter.
        
        Args:
            topic (str): The main topic
            book_title (str): The ebook title
            chapter_title (str): The chapter title
            chapter_outline (list): Outline points for the chapter
            target_words (int): Target word count for the chapter
            
        Returns:
            str: Generated chapter content in HTML format
        """
        system_message = f"""
        You are a professional book author who creates engaging, informative content.
        Write in a clear, authoritative tone that's accessible to readers.
        Use proper HTML formatting with h2, h3, p, ul, ol, and other appropriate tags.
        Target approximately {target_words} words for this chapter.
        """
        
        outline_text = "\n".join([f"- {point}" for point in chapter_outline])
        
        prompt = f"""
        Write a comprehensive chapter for an ebook with the title:
        
        Book: "{book_title}"
        Chapter: "{chapter_title}"
        
        About the topic:
        {topic}
        
        Chapter outline:
        {outline_text}
        
        The chapter should:
        - Start with an engaging introduction to the chapter topic
        - Cover all points in the outline thoroughly
        - Include relevant examples, case studies, or anecdotes where appropriate
        - Use subheadings to organize content
        - End with a conclusion that summarizes key points and transitions to the next chapter
        - Be formatted in proper HTML
        - Be approximately {target_words} words
        
        Format the entire chapter in HTML, using appropriate tags (h2, h3, p, ul, ol, blockquote, etc.).
        Do not include the chapter title at the beginning as it will be added separately.
        """
        
        content = self.openai_generator.generate_content(prompt, system_message, max_tokens=4000)
        
        # Ensure content has proper HTML structure
        if content and not content.strip().startswith("<"):
            content = f"<p>{content.replace('\\n\\n', '</p><p>').replace('\\n', '<br>')}</p>"
            
        return content
    
    def _generate_cover_prompt(self, topic, title):
        """
        Generate an optimized prompt for ebook cover image.
        
        Args:
            topic (str): The main topic
            title (str): The ebook title
            
        Returns:
            str: Optimized image generation prompt
        """
        system_message = "You are a professional book cover designer who creates detailed specifications for compelling covers."
        
        prompt = f"""
        Create a detailed, descriptive prompt for DALL-E to generate a high-quality ebook cover for:
        
        Book title: {title}
        Topic: {topic}
        
        The prompt should:
        - Be detailed and specific about visual elements
        - Include style guidance (photorealistic, illustration, etc.)
        - Mention color scheme, lighting, and mood
        - Describe a professional, commercial-quality book cover
        - Be between 50-100 words
        - NOT include any text overlays or words to appear in the image (title will be added separately)
        
        Just provide the prompt text with no additional explanation or formatting.
        """
        
        cover_prompt = self.openai_generator.generate_content(prompt, system_message, max_tokens=200)
        return cover_prompt.strip() if cover_prompt else f"A professional book cover representing {topic}, with modern design and appealing colors"
    
    def compile_ebook(self, ebook, output_dir=None, add_cover=True, add_toc=True):
        """
        Compile the ebook content into the specified format.
        
        Args:
            ebook (dict): The ebook data
            output_dir (str): Directory to save the compiled ebook
            add_cover (bool): Whether to include the cover image
            add_toc (bool): Whether to include table of contents
            
        Returns:
            dict: Paths to the compiled ebook files
        """
        if not output_dir:
            output_dir = os.path.join(ROOT_DIR, ".mp", "ebooks")
            
        # Ensure directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Create a safe filename from the title
        safe_title = ebook["title"].lower().replace(' ', '_').replace('?', '').replace('!', '').replace(',', '').replace('.', '')
        
        # First, create HTML version which will be used as source for other formats
        html_path = os.path.join(output_dir, f"{safe_title}.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(f"<!DOCTYPE html>\n<html>\n<head>\n<title>{ebook['title']}</title>\n")
            f.write("<meta charset=\"utf-8\">\n")
            f.write("<style>body{margin:5%; font-family:serif; font-size:medium;} h1{text-align:center;} h2{margin-top:2em;} .cover{text-align:center; margin:2em;} .cover img{max-width:100%; max-height:800px;}</style>\n")
            f.write("</head>\n<body>\n")
            
            # Add cover image if available
            if add_cover and ebook.get("cover_path"):
                image_filename = os.path.basename(ebook["cover_path"])
                f.write(f'<div class="cover"><img src="{image_filename}" alt="{ebook["title"]}"></div>\n')
            
            # Add title page
            f.write(f'<h1>{ebook["title"]}</h1>\n')
            f.write(f'<p style="text-align:center;">Generated on {ebook["date"]}</p>\n')
            
            # Add description
            if ebook.get("description"):
                f.write(f'<div class="description"><p>{ebook["description"]}</p></div>\n')
            
            # Add table of contents if requested
            if add_toc and ebook.get("toc"):
                f.write('<h2>Table of Contents</h2>\n<ul>\n')
                for i, chapter_title in enumerate(ebook["toc"]):
                    f.write(f'<li><a href="#chapter{i+1}">{chapter_title}</a></li>\n')
                f.write('</ul>\n')
            
            # Add chapters
            for i, chapter in enumerate(ebook["chapters"]):
                f.write(f'<h2 id="chapter{i+1}">{chapter["title"]}</h2>\n')
                f.write(chapter["content"])
                f.write('\n')
            
            f.write("\n</body>\n</html>")
        
        # Copy cover image if available
        cover_path = None
        if ebook.get("cover_path") and os.path.exists(ebook["cover_path"]):
            import shutil
            image_filename = os.path.basename(ebook["cover_path"])
            cover_path = os.path.join(output_dir, image_filename)
            shutil.copy(ebook["cover_path"], cover_path)
        
        # Compile to requested format
        output_files = {"html": html_path, "cover": cover_path}
        
        if ebook["format"].lower() == "pdf":
            pdf_path = self._convert_to_pdf(html_path, output_dir, safe_title)
            output_files["pdf"] = pdf_path
        
        elif ebook["format"].lower() == "epub":
            epub_path = self._convert_to_epub(html_path, output_dir, safe_title, ebook)
            output_files["epub"] = epub_path
        
        elif ebook["format"].lower() == "mobi":
            mobi_path = self._convert_to_mobi(html_path, output_dir, safe_title, ebook)
            output_files["mobi"] = mobi_path
        
        # Save metadata
        meta_path = os.path.join(output_dir, f"{safe_title}_meta.json")
        meta_data = {
            "title": ebook["title"],
            "topic": ebook["topic"],
            "date": ebook["date"],
            "word_count": ebook["word_count"],
            "chapters": len(ebook["chapters"]),
            "format": ebook["format"],
            "html_file": os.path.basename(html_path),
            "cover_file": os.path.basename(cover_path) if cover_path else None,
            "output_files": {k: os.path.basename(v) for k, v in output_files.items() if v}
        }
        
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta_data, f, indent=2)
        
        output_files["meta"] = meta_path
        return output_files
    
    def _convert_to_pdf(self, html_path, output_dir, filename):
        """
        Convert HTML to PDF format.
        
        Args:
            html_path (str): Path to HTML file
            output_dir (str): Output directory
            filename (str): Base filename
            
        Returns:
            str: Path to generated PDF file
        """
        pdf_path = os.path.join(output_dir, f"{filename}.pdf")
        
        try:
            # Try using wkhtmltopdf if available
            import subprocess
            subprocess.run(["wkhtmltopdf", html_path, pdf_path], check=True)
            return pdf_path
        except:
            # Fallback to weasyprint if available
            try:
                from weasyprint import HTML
                HTML(html_path).write_pdf(pdf_path)
                return pdf_path
            except:
                # If conversion fails, note this in a text file
                note_path = os.path.join(output_dir, f"{filename}_pdf_note.txt")
                with open(note_path, "w") as f:
                    f.write("PDF conversion requires wkhtmltopdf or weasyprint to be installed.\n")
                    f.write("Please install one of these tools and try again.\n")
                return note_path
    
    def _convert_to_epub(self, html_path, output_dir, filename, ebook):
        """
        Convert HTML to EPUB format.
        
        Args:
            html_path (str): Path to HTML file
            output_dir (str): Output directory
            filename (str): Base filename
            ebook (dict): Ebook data
            
        Returns:
            str: Path to generated EPUB file
        """
        epub_path = os.path.join(output_dir, f"{filename}.epub")
        
        try:
            # Try using pandoc if available
            import subprocess
            cmd = ["pandoc", html_path, "-o", epub_path]
            
            # Add metadata if available
            if ebook.get("title"):
                cmd.extend(["--metadata", f"title={ebook['title']}"])
            
            # Add cover if available
            if ebook.get("cover_path"):
                cmd.extend(["--epub-cover-image", ebook["cover_path"]])
                
            subprocess.run(cmd, check=True)
            return epub_path
        except:
            # If conversion fails, note this in a text file
            note_path = os.path.join(output_dir, f"{filename}_epub_note.txt")
            with open(note_path, "w") as f:
                f.write("EPUB conversion requires pandoc to be installed.\n")
                f.write("Please install pandoc and try again.\n")
            return note_path
    
    def _convert_to_mobi(self, html_path, output_dir, filename, ebook):
        """
        Convert HTML to MOBI format.
        
        Args:
            html_path (str): Path to HTML file
            output_dir (str): Output directory
            filename (str): Base filename
            ebook (dict): Ebook data
            
        Returns:
            str: Path to generated MOBI file
        """
        mobi_path = os.path.join(output_dir, f"{filename}.mobi")
        
        try:
            # First convert to EPUB
            epub_path = self._convert_to_epub(html_path, output_dir, filename, ebook)
            
            # Then convert EPUB to MOBI using calibre's ebook-convert if available
            import subprocess
            subprocess.run(["ebook-convert", epub_path, mobi_path], check=True)
            return mobi_path
        except:
            # If conversion fails, note this in a text file
            note_path = os.path.join(output_dir, f"{filename}_mobi_note.txt")
            with open(note_path, "w") as f:
                f.write("MOBI conversion requires pandoc and calibre's ebook-convert to be installed.\n")
                f.write("Please install these tools and try again.\n")
            return note_path
    
    def publish_ebook(self, ebook, platform="amazon"):
        """
        Simulate publishing the ebook to various platforms.
        
        Args:
            ebook (dict): The ebook data
            platform (str): The platform to publish to (amazon, kobo, etc.)
            
        Returns:
            dict: Response data including URL and platform details
        """
        # This is a placeholder for actual publishing functionality
        # In a real implementation, this would use the KDP API or other publishing platform APIs
        
        print(f"Publishing ebook '{ebook['title']}' to {platform}")
        print(f"Content length: {ebook['word_count']} words, {len(ebook['chapters'])} chapters")
        print(f"Cover image: {ebook['cover_path']}")
        
        # Simulate publishing to platform
        platform_url = f"https://example.com/ebook/{ebook['title'].lower().replace(' ', '-')}"
        
        return {
            "success": True,
            "url": platform_url,
            "platform": platform,
            "ebook_id": str(uuid4()),
            "date_published": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
