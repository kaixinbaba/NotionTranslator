# Notion Translator

A robust automation script that automatically translates words and updates Notion databases with translated content and phonetic transcriptions. The application uses webhooks to detect page updates and leverages the DeepSeek API for translations.

## Prerequisites

Before running the application, you need:

1. Python 3.11 or higher
2. A Notion integration token ([Create one here](https://www.notion.so/my-integrations))
3. A DeepSeek API key
4. A Notion database with the following properties:
   - `Word` (title)
   - `Translation` (rich text)
   - `Translation En` (rich text)
   - `Transcription` (rich text)

## Command Line Installation & Setup

1. Clone the repository:
```bash
git clone <your-repository-url>
cd notion-translator
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies using pip and pyproject.toml:
```bash
pip install .
```

4. Set up environment variables by creating a `.env` file:
```bash
# Create .env file
touch .env

# Add your API keys to the .env file
echo "NOTION_TOKEN=your_notion_integration_token" >> .env
echo "DEEPSEEK_API_KEY=your_deepseek_api_key" >> .env
```

## Running the Application

1. Ensure your environment variables are set:
```bash
# Verify environment variables
python -c "import os; print('NOTION_TOKEN:', bool(os.getenv('NOTION_TOKEN'))); print('DEEPSEEK_API_KEY:', bool(os.getenv('DEEPSEEK_API_KEY')))"
```

2. Start the Flask server:
```bash
python app.py
```

The server will start on port 5000. You should see output indicating the server is running.

3. Configure your Notion webhook to point to your server's URL:
```
http://your-server:5000/webhook
```

## Testing the Application

1. Test the health check endpoint:
```bash
curl http://localhost:5000/
```

2. Test the webhook endpoint (for development):
```bash
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{"data": {"id": "your-page-id", "properties": {"Word": {"title": [{"text": {"content": "test"}}]}}}}'
```

## Error Handling

The application includes robust error handling for:
- Invalid webhook payloads
- API failures
- Archived Notion pages
- Missing or invalid translations

All errors are logged for debugging purposes.

## Development Tips

1. Enable debug mode:
```bash
export FLASK_DEBUG=1
python app.py
```

2. View logs in real-time:
```bash
# In a separate terminal
tail -f *.log
```

3. Check webhook status:
```bash
curl http://localhost:5000/webhook
```

## Architecture

The application follows a modular architecture:
- `app.py` - Main Flask application and webhook handler
- `notion_handler.py` - Notion API integration
- `translator.py` - DeepSeek API integration for translations
- `config.py` - Configuration management
- `utils.py` - Shared utilities and logging

## Troubleshooting

1. If the server fails to start, check:
   - Port 5000 is not in use
   - Environment variables are set correctly
   - Python version is 3.11 or higher

2. If translations fail, verify:
   - DeepSeek API key is valid
   - Network connection is stable
   - Word format in Notion is correct

3. If Notion updates fail, confirm:
   - Notion integration token is valid
   - Database has the correct properties
   - Page is not archived

For any other issues, check the application logs for detailed error messages.