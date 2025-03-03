from notion_client import Client
import json
from utils import setup_logger

logger = setup_logger()

class NotionHandler:
    def __init__(self, token):
        self.client = Client(auth=token)

    def get_page_content(self, page_id):
        """Retrieve content from a Notion page"""
        try:
            # Get page properties
            page = self.client.pages.retrieve(page_id)

            # Get page blocks (content)
            blocks = self.client.blocks.children.list(page_id)

            content = {
                'properties': page.get('properties', {}),
                'blocks': blocks.get('results', [])
            }

            return content

        except Exception as e:
            logger.error(f"Error getting page content: {str(e)}")
            raise

    def update_page_content(self, page_id, translated_content):
        """Update Notion page with translated content"""
        try:
            # Update properties if needed
            if translated_content.get('properties'):
                self.client.pages.update(
                    page_id,
                    properties=translated_content['properties']
                )

            # Update blocks
            if translated_content.get('blocks'):
                for block in translated_content['blocks']:
                    if block.get('id'):
                        self.client.blocks.update(
                            block_id=block['id'],
                            **block['content']
                        )

            logger.info(f"Successfully updated page {page_id}")

        except Exception as e:
            logger.error(f"Error updating page content: {str(e)}")
            raise

    def update_translations(self, page_id, translations):
        """Update translation fields in the Notion database"""
        try:
            # Log the update attempt
            logger.info(f"Attempting to update page {page_id} with translations: {json.dumps(translations)}")

            # First check if the page exists and is accessible
            try:
                page = self.client.pages.retrieve(page_id)
                logger.info(f"Successfully retrieved page {page_id}")

                # Check if page is archived
                if page.get('archived', False):
                    error_msg = f"Page {page_id} is archived. Please unarchive it before updating."
                    logger.error(error_msg)
                    raise Exception(error_msg)

            except Exception as e:
                logger.error(f"Failed to retrieve page {page_id}: {str(e)}")
                raise Exception(f"Page retrieval failed: {str(e)}")

            # Prepare the properties update
            properties = {
                "Translation": {
                    "rich_text": [{
                        "text": {
                            "content": translations['chinese']
                        }
                    }]
                },
                "Translation En": {
                    "rich_text": [{
                        "text": {
                            "content": translations['english']
                        }
                    }]
                }
            }

            # Update only page properties, not blocks
            update_response = self.client.pages.update(
                page_id,
                properties=properties
            )

            logger.info(f"Successfully updated translations for page {page_id}")
            return update_response

        except Exception as e:
            logger.error(f"Error updating translations: {str(e)}")
            if hasattr(e, 'response'):
                logger.error(f"Notion API response: {e.response.text if hasattr(e.response, 'text') else str(e.response)}")
            raise