import requests
from utils import setup_logger

logger = setup_logger()

class Translator:
    def __init__(self, api_key):
        self.api_key = api_key
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def translate_word(self, word):
        """Translate a word and get its English explanation using DeepSeek API"""
        try:
            prompt = f"""Translate the word "{word}" to Chinese and provide a simple English explanation.
Please respond in the following format only:
Chinese: [Chinese translation]
English: [Simple explanation in English (maximum 10 words)]"""

            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "model": "deepseek-chat"
                }
            )

            if response.status_code == 200:
                result = response.json()
                response_text = result['choices'][0]['message']['content']

                # Parse the response
                lines = response_text.strip().split('\n')
                translations = {}
                for line in lines:
                    if line.startswith('Chinese:'):
                        translations['chinese'] = line.replace('Chinese:', '').strip()
                    elif line.startswith('English:'):
                        translations['english'] = line.replace('English:', '').strip()

                return translations
            else:
                logger.error(f"Translation API error: {response.text}")
                raise Exception(f"Translation API returned status code: {response.status_code}")

        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            raise