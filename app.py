from flask import Flask, request, jsonify
import os
from config import load_config
from notion_handler import NotionHandler
from translator import Translator
from utils import setup_logger
import json

app = Flask(__name__)
logger = setup_logger()

# Load configuration
config = load_config()
notion_handler = NotionHandler(config['NOTION_TOKEN'])
translator = Translator(config['DEEPSEEK_API_KEY'])

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    try:
        payload = request.json

        # Handle Notion's URL verification
        if payload.get('type') == 'url_verification':
            return jsonify({'challenge': payload['challenge']})

        # Process page updates
        if payload.get('type') == 'page_updated':
            page_id = payload['page']['id']

            # Get page content
            page_content = notion_handler.get_page_content(page_id)

            # Translate new content
            translated_content = translator.translate_content(
                page_content,
                target_language='spanish'  # You can make this configurable if needed
            )

            # Update Notion page with translations
            notion_handler.update_page_content(page_id, translated_content)

            logger.info(f"Successfully processed page update for {page_id}")
            return jsonify({'status': 'success'}), 200

        return jsonify({'status': 'ignored'}), 200

    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # ALWAYS serve the app on port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)