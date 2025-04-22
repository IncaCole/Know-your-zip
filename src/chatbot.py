from together import Together
import time
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Chatbot:
    def __init__(self, api_key: str):
        """
        Initialize the chatbot with Together API client.
        
        Args:
            api_key (str): Together API key
        """
        self.client = Together(api_key=api_key)
        self.model = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"
        self.max_retries = 3
        self.retry_delay = 2  # seconds

    def generate_answer(self, question: str) -> Optional[str]:
        """
        Generate an answer for the given question using the Together API.
        Includes retry logic for failed requests.
        
        Args:
            question (str): User's question
            
        Returns:
            Optional[str]: Model's response or None if all retries fail
        """
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": question}],
                    temperature=0.7,
                    max_tokens=1000
                )
                return response.choices[0].message.content
                
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    logger.error("All retry attempts failed")
                    return None

# Example usage
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    chatbot = Chatbot(api_key=os.getenv("TOGETHER_API_KEY"))
    test_question = "What is the capital of France?"
    response = chatbot.generate_answer(test_question)
    
    if response:
        print(f"Question: {test_question}")
        print(f"Response: {response}")
    else:
        print("Failed to get response after all retries")