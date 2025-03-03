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
