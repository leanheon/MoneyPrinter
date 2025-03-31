import os
import sys
import json
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import threading
import time

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import project modules
from src.openai_generator import OpenAIGenerator
from src.monetization.monetization_manager import MonetizationManager
from src.classes.YouTube import YouTube
from src.classes.Twitter import Twitter
from src.classes.Threads import Threads
from src.classes.ShortsGenerator import ShortsGenerator
from src.blog_generator import BlogGenerator
from src.google_sheets_connector import GoogleSheetsConnector
from src.content_manager import ContentManager
from src.config import get_config

app = Flask(__name__, template_folder='web/templates', static_folder='web/static')
app.secret_key = os.urandom(24)

# Initialize components
openai_generator = None
monetization_manager = None
youtube = None
twitter = None
threads = None
blog_generator = None
sheets_connector = None
content_manager = None

# Store generated content
generated_content = {
    "youtube": {},
    "twitter": {},
    "threads": {},
    "monetization": {},
    "shorts": {},
    "blog": {},
    "sheets": {}
}

# Status tracking
status = {
    "initialized": False,
    "initializing": False,
    "error": None
}

def initialize_components():
    """Initialize all components in a background thread"""
    global openai_generator, monetization_manager, youtube, twitter, threads, blog_generator, sheets_connector, content_manager, status
    
    try:
        status["initializing"] = True
        
        # Initialize OpenAI generator
        openai_generator = OpenAIGenerator()
        
        # Initialize monetization manager
        monetization_manager = MonetizationManager()
        
        # Initialize platform classes (without posting)
        youtube = YouTube(upload=False)
        twitter = Twitter(post=False)
        threads = Threads(post=False)
        
        # Initialize new components
        blog_generator = BlogGenerator()
        
        # Initialize Google Sheets connector
        config = get_config()
        credentials_path = config.get("google_sheets", {}).get("credentials_path", None)
        sheets_connector = GoogleSheetsConnector(credentials_path)
        
        # Initialize content manager
        content_manager = ContentManager(credentials_path)
        
        status["initialized"] = True
        status["initializing"] = False
        status["error"] = None
    except Exception as e:
        status["error"] = str(e)
        status["initializing"] = False

@app.route('/')
def index():
    """Render the main control tower dashboard"""
    config = get_config()
    has_api_key = bool(config.get("openai", {}).get("api_key", ""))
    
    return render_template('control_tower.html', 
                          initialized=status["initialized"],
                          initializing=status["initializing"],
                          error=status["error"],
                          has_api_key=has_api_key)

@app.route('/initialize', methods=['POST'])
def initialize():
    """Initialize the application components"""
    global status
    
    if not status["initialized"] and not status["initializing"]:
        # Start initialization in a background thread
        init_thread = threading.Thread(target=initialize_components)
        init_thread.daemon = True
        init_thread.start()
    
    return jsonify({"status": "initializing"})

@app.route('/status')
def get_status():
    """Get the current initialization status"""
    return jsonify({
        "initialized": status["initialized"],
        "initializing": status["initializing"],
        "error": status["error"]
    })

@app.route('/config', methods=['GET', 'POST'])
def config():
    """View and update configuration"""
    if request.method == 'POST':
        # Update configuration
        config_data = get_config()
        
        # Update OpenAI settings
        config_data["openai"] = {
            "api_key": request.form.get('api_key', ''),
            "model": request.form.get('model', 'gpt-4-turbo')
        }
        
        # Update monetization settings
        if "monetization" not in config_data:
            config_data["monetization"] = {}
            
        config_data["monetization"]["affiliate"] = {
            "amazon_tag": request.form.get('amazon_tag', ''),
            "clickbank_id": request.form.get('clickbank_id', '')
        }
        
        config_data["monetization"]["sponsorship"] = {
            "enabled": request.form.get('sponsorship_enabled') == 'on'
        }
        
        config_data["monetization"]["digital_products"] = {
            "enabled": request.form.get('digital_products_enabled') == 'on'
        }
        
        config_data["monetization"]["subscription"] = {
            "enabled": request.form.get('subscription_enabled') == 'on'
        }
        
        # Update Google Sheets settings
        if "google_sheets" not in config_data:
            config_data["google_sheets"] = {}
            
        config_data["google_sheets"]["credentials_path"] = request.form.get('google_credentials_path', '')
        config_data["google_sheets"]["spreadsheet_id"] = request.form.get('spreadsheet_id', '')
        config_data["google_sheets"]["spreadsheet_name"] = request.form.get('spreadsheet_name', '')
        
        # Save updated config
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
            
        # Reset initialization status
        global status
        status["initialized"] = False
        status["initializing"] = False
        status["error"] = None
        
        return redirect(url_for('config'))
    
    # GET request - show config form
    config_data = get_config()
    return render_template('config.html', config=config_data)

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    """Generate content page"""
    if request.method == 'POST':
        # Get form data
        topic = request.form.get('topic', '')
        platform = request.form.get('platform', 'youtube')
        monetization_type = request.form.get('monetization_type', '')
        
        if not topic:
            return render_template('generate.html', error="Topic is required")
            
        if not status["initialized"]:
            return render_template('generate.html', error="System not initialized")
            
        try:
            # Generate content based on platform
            if platform == 'youtube':
                script = openai_generator.generate_youtube_script(topic)
                title = openai_generator.generate_youtube_title(topic)
                
                generated_content["youtube"] = {
                    "topic": topic,
                    "title": title,
                    "script": script
                }
                
                # Generate monetized content if requested
                if monetization_type:
                    monetized = monetization_manager.generate_monetized_content(topic, platform, monetization_type)
                    generated_content["monetization"] = monetized
                
                return redirect(url_for('view_content', platform=platform))
                
            elif platform == 'twitter':
                post = openai_generator.generate_twitter_post(topic)
                
                generated_content["twitter"] = {
                    "topic": topic,
                    "post": post
                }
                
                # Generate monetized content if requested
                if monetization_type:
                    monetized = monetization_manager.generate_monetized_content(topic, platform, monetization_type)
                    generated_content["monetization"] = monetized
                
                return redirect(url_for('view_content', platform=platform))
                
            elif platform == 'threads':
                post = openai_generator.generate_threads_post(topic)
                
                generated_content["threads"] = {
                    "topic": topic,
                    "post": post
                }
                
                # Generate monetized content if requested
                if monetization_type:
                    monetized = monetization_manager.generate_monetized_content(topic, platform, monetization_type)
                    generated_content["monetization"] = monetized
                
                return redirect(url_for('view_content', platform=platform))
                
            elif platform == 'shorts':
                # Handle shorts generation
                is_knowledge = request.form.get('is_knowledge', 'false') == 'true'
                generator = ShortsGenerator(topic, is_knowledge)
                generator.generate_script()
                generator.generate_metadata()
                
                generated_content["shorts"] = {
                    "topic": topic,
                    "title": generator.title,
                    "description": generator.description,
                    "script": generator.script,
                    "is_knowledge": is_knowledge
                }
                
                return redirect(url_for('view_content', platform=platform))
                
            elif platform == 'blog':
                # Handle blog post generation
                length = request.form.get('length', 'medium')
                blog_post = blog_generator.generate_blog_post(topic, length)
                
                generated_content["blog"] = blog_post
                
                return redirect(url_for('view_content', platform=platform))
                
            else:
                return render_template('generate.html', error="Invalid platform")
                
        except Exception as e:
            return render_template('generate.html', error=str(e))
    
    # GET request - show generation form
    # Pre-fill topic if provided in query string
    topic = request.args.get('topic', '')
    platform = request.args.get('platform', 'youtube')
    monetization_type = request.args.get('monetization_type', '')
    
    return render_template('generate.html', 
                          topic=topic, 
                          platform=platform, 
                          monetization_type=monetization_type)

@app.route('/view/<platform>')
def view_content(platform):
    """View generated content"""
    if platform not in ['youtube', 'twitter', 'threads', 'shorts', 'blog']:
        return redirect(url_for('generate'))
        
    content = generated_content.get(platform, {})
    monetized = generated_content.get("monetization", {})
    
    return render_template('view_content.html', 
                          platform=platform, 
                          content=content,
                          monetized=monetized)

@app.route('/create_short', methods=['POST'])
def create_short():
    """Create a short from generated content"""
    if not status["initialized"]:
        flash("System not initialized", "error")
        return redirect(url_for('generate'))
        
    shorts_content = generated_content.get("shorts", {})
    if not shorts_content:
        flash("No shorts content generated", "error")
        return redirect(url_for('generate'))
        
    try:
        # Create ShortsGenerator instance with the generated content
        generator = ShortsGenerator(shorts_content["topic"], shorts_content.get("is_knowledge", False))
        generator.script = shorts_content["script"]
        generator.title = shorts_content["title"]
        generator.description = shorts_content["description"]
        
        # Create the short
        video_path = generator.create_short()
        
        if video_path:
            # Update generated content with video path
            generated_content["shorts"]["video_path"] = video_path
            flash("Short created successfully", "success")
        else:
            flash("Failed to create short", "error")
            
        return redirect(url_for('view_content', platform='shorts'))
        
    except Exception as e:
        flash(f"Error creating short: {str(e)}", "error")
        return redirect(url_for('view_content', platform='shorts'))

@app.route('/publish_blog', methods=['POST'])
def publish_blog():
    """Publish a blog post from generated content"""
    if not status["initialized"]:
        flash("System not initialized", "error")
        return redirect(url_for('generate'))
        
    blog_content = generated_content.get("blog", {})
    if not blog_content:
        flash("No blog content generated", "error")
        return redirect(url_for('generate'))
        
    try:
        # Save blog post files
        saved_files = blog_generator.save_blog_post(blog_content)
        
        # Simulate posting to blog
        post_result = blog_generator.post_to_blog(blog_content)
        
        if saved_files and "html_path" in saved_files:
            # Update generated content with saved files and URL
            generated_content["blog"]["saved_files"] = saved_files
            generated_content["blog"]["post_url"] = post_result.get("url") if post_result else None
            
            flash("Blog post published successfully", "success")
        else:
            flash("Failed to publish blog post", "error")
            
        return redirect(url_for('view_content', platform='blog'))
        
    except Exception as e:
        flash(f"Error publishing blog post: {str(e)}", "error")
        return redirect(url_for('view_content', platform='blog'))

@app.route('/sheets', methods=['GET', 'POST'])
def sheets():
    """Google Sheets integration page"""
    if not status["initialized"]:
        flash("System not initialized", "error")
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        action = request.form.get('action', '')
        
        if action == 'connect':
            # Connect to spreadsheet
            spreadsheet_id = request.form.get('spreadsheet_id', '')
            spreadsheet_name = request.form.get('spreadsheet_name', '')
            
            if spreadsheet_id or spreadsheet_name:
                content_manager.set_spreadsheet(spreadsheet_id, spreadsheet_name)
                flash("Connected to spreadsheet", "success")
            else:
                flash("Spreadsheet ID or name required", "error")
                
        elif action == 'create_template':
            # Create template spreadsheet
            name = request.form.get('template_name', 'MoneyPrinter Content')
            spreadsheet_id = content_manager.create_template_spreadsheet(name)
            
            if spreadsheet_id:
                flash(f"Template spreadsheet created with ID: {spreadsheet_id}", "success")
                generated_content["sheets"]["spreadsheet_id"] = spreadsheet_id
                generated_content["sheets"]["spreadsheet_name"] = name
            else:
                flash("Failed to create template spreadsheet", "error")
                
        elif action == 'add_content':
            # Add content item to spreadsheet
            topic = request.form.get('topic', '')
            content_type = request.form.get('content_type', '')
            script = request.form.get('script', '')
            
            if not topic or not content_type:
                flash("Topic and content type required", "error")
            else:
                additional_data = {}
                
                if content_type.lower() == 'shorts' or content_type.lower() == 'short':
                    additional_data["Knowledge"] = request.form.get('is_knowledge', 'false')
                elif content_type.lower() == 'blog' or content_type.lower() == 'blogpost':
                    additional_data["Length"] = request.form.get('length', 'medium')
                
                row_index = content_manager.add_content_item(topic, content_type, script, additional_data)
                
                if row_index:
                    flash(f"Content item added at row {row_index}", "success")
                else:
                    flash("Failed to add content item", "error")
                    
        elif action == 'process_pending':
            # Process pending content
            content_type = request.form.get('filter_type', None)
            results = content_manager.process_all_pending(content_type)
            
            if results:
                success_count = sum(1 for r in results if r.get("success", False))
                flash(f"Processed {len(results)} items, {success_count} successful", "success")
                generated_content["sheets"]["process_results"] = results
            else:
                flash("No pending content to process", "info")
                
        return redirect(url_for('sheets'))
    
    # GET request - show sheets page
    config = get_config()
    spreadsheet_id = config.get("google_sheets", {}).get("spreadsheet_id", "")
    spreadsheet_name = config.get("google_sheets", {}).get("spreadsheet_name", "")
    
    # Get pending content if connected
    pending_content = []
    if content_manager and (spreadsheet_id or spreadsheet_name):
        content_manager.set_spreadsheet(spreadsheet_id, spreadsheet_name)
        pending_content = content_manager.get_pending_content()
    
    return render_template('sheets.html',
                          spreadsheet_id=spreadsheet_id,
                          spreadsheet_name=spreadsheet_name,
                          pending_content=pending_content,
                          process_results=generated_content.get("sheets", {}).get("process_results", []))

@app.route('/monetization')
def monetization():
    """View monetization dashboard"""
    if not status["initialized"]:
        return redirect(url_for('index'))
        
    stats = monetization_manager.get_monetization_stats()
    revenue = monetization_manager.get_revenue_estimate()
    
    return render_template('monetization.html', 
                          stats=stats,
                          revenue=revenue)

@app.route('/generate_topic', methods=['POST'])
def generate_topic():
    """Generate a random topic using OpenAI"""
    if not status["initialized"]:
        return jsonify({"error": "System not initialized"})
        
    try:
        topic = openai_generator.generate_topic()
        return jsonify({"topic": topic})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/digital_products')
def digital_products():
    """View digital products"""
    if not status["initialized"]:
        return redirect(url_for('index'))
        
    products = monetization_manager.digital_product_manager.get_products()
    
    return render_template('digital_products.html', products=products)

@app.route('/create_product', methods=['GET', 'POST'])
def create_product():
    """Create a new digital product"""
    if not status["initialized"]:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        topic = request.form.get('topic', '')
        product_type = request.form.get('product_type', 'guide')
        
        if not topic:
            return render_template('create_product.html', error="Topic is required")
            
        try:
            product = monetization_manager.digital_product_manager.generate_digital_product(topic, product_type)
            
            if product:
                return redirect(url_for('digital_products'))
            else:
                return render_template('create_product.html', error="Failed to create product")
                
        except Exception as e:
            return render_template('create_product.html', error=str(e))
    
    # GET request - show product creation form
    return render_template('create_product.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
