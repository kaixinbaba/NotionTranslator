import requests
from utils import setup_logger

logger = setup_logger()

class Translator:
    def __init__(self, api_key):
        self.api_key = api_key
        self.api_url = "https://api.deepseek.com/v1/chat/completions"  # Replace with actual DeepSeek endpoint
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def translate_text(self, text, target_language):
        """Translate a single text string using DeepSeek API"""
        try:
            # Construct the prompt for translation
            prompt = f"Translate the following text to {target_language}:\n{text}"

            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "model": "deepseek-chat"  # Replace with actual model name
                }
            )

            if response.status_code == 200:
                result = response.json()
                translated_text = result['choices'][0]['message']['content']
                return translated_text.strip()
            else:
                logger.error(f"Translation API error: {response.text}")
                raise Exception(f"Translation API returned status code: {response.status_code}")

        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            raise

    def translate_content(self, page_content, target_language):
        """Translate Notion page content"""
        translated_content = {
            'properties': {},
            'blocks': []
        }

        # Translate properties
        for prop_name, prop_data in page_content['properties'].items():
            if prop_data['type'] == 'rich_text':
                original_text = prop_data['rich_text'][0]['text']['content']
                translated_text = self.translate_text(original_text, target_language)
                prop_data['rich_text'][0]['text']['content'] = translated_text
                translated_content['properties'][prop_name] = prop_data

        # Translate blocks
        for block in page_content['blocks']:
            if block['type'] in ['paragraph', 'heading_1', 'heading_2', 'heading_3']:
                original_text = block[block['type']]['rich_text'][0]['text']['content']
                translated_text = self.translate_text(original_text, target_language)

                translated_block = {
                    'id': block['id'],
                    'content': {
                        'type': block['type'],
                        block['type']: {
                            'rich_text': [{
                                'type': 'text',
                                'text': {
                                    'content': translated_text
                                }
                            }]
                        }
                    }
                }
                translated_content['blocks'].append(translated_block)

        return translated_content