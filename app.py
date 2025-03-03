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

@app.route('/')
def health_check():
    """Health check endpoint"""
    logger.info("Health check request received")
    return jsonify({
        'status': 'healthy',
        'service': 'notion-translator',
        'endpoints': [
            {'path': '/', 'methods': ['GET'], 'description': 'Health check'},
            {'path': '/webhook', 'methods': ['GET', 'POST'], 'description': 'Notion webhook endpoint'}
        ]
    })

@app.route('/webhook', methods=['GET', 'POST'])
def handle_webhook():
    """Handle Notion webhook requests"""
    try:
        if request.method == 'GET':
            # Handle Notion's URL verification
            challenge = request.args.get('challenge')
            if challenge:
                return jsonify({'challenge': challenge})
            return jsonify({'status': 'ok'})

        payload = request.json
        logger.info(f"Received webhook payload: {json.dumps(payload)}")

        # Validate payload structure
        if not payload.get('data'):
            logger.error("Invalid payload: Missing 'data' field")
            return jsonify({'error': 'Invalid payload structure: Missing data field'}), 400

        # Extract word from the payload
        try:
            properties = payload['data'].get('properties', {})
            word_property = properties.get('Word', {})
            title = word_property.get('title', [])

            if not title or not isinstance(title, list):
                raise KeyError("Invalid or missing title array")

            word = title[0]['text']['content']
            page_id = payload['data']['id']

            logger.info(f"Processing word: '{word}' for page: {page_id}")

        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Error extracting data from webhook: {str(e)}")
            logger.debug(f"Received payload structure: {json.dumps(payload)}")
            return jsonify({
                'error': 'Invalid payload structure', 
                'details': f'Could not extract word or page ID: {str(e)}'
            }), 400

        # Get translations
        try:
            translations = translator.translate_word(word)
            logger.info(f"Got translations for '{word}': {translations}")

            if not translations.get('chinese') or not translations.get('english'):
                raise ValueError("Translation response missing required fields")

        except Exception as e:
            logger.error(f"Translation error for word '{word}': {str(e)}")
            return jsonify({
                'error': 'Translation failed',
                'details': str(e)
            }), 500

        # Update Notion page with translations
        try:
            notion_handler.update_translations(page_id, translations)
            logger.info(f"Successfully updated translations for word: '{word}' in page: {page_id}")

        except Exception as e:
            logger.error(f"Failed to update Notion page {page_id}: {str(e)}")
            return jsonify({
                'error': 'Failed to update Notion page',
                'details': str(e)
            }), 500

        return jsonify({
            'status': 'success',
            'word': word,
            'translations': translations
        }), 200

    except Exception as e:
        logger.error(f"Unexpected error processing webhook: {str(e)}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

if __name__ == '__main__':
    # ALWAYS serve the app on port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)