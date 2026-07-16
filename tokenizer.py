import os
from tokenizers import Tokenizer

class TokenizerHandler:
    """Handles encoding and decoding operations using a pre-trained tokenizer."""
    
    def __init__(self, tokenizer_path):
        self.tokenizer_path = tokenizer_path
        if not os.path.exists(self.tokenizer_path):
            raise FileNotFoundError(f"No tokenizer model found at {self.tokenizer_path}. Train the tokenizer first.")
        
        self.tokenizer = Tokenizer.from_file(self.tokenizer_path)

    def encode(self, text):
        """Encodes raw text into a tokenizer Encoding object."""
        return self.tokenizer.encode(text)
    
    def encode_ids(self, text):
        """Encodes raw text into a tokenizer Encoding object."""
        return self.tokenizer.encode(text).ids

    def decode(self, token_ids):
        """Decodes token IDs back into a human-readable string."""
        return self.tokenizer.decode(token_ids)
        
    def get_token_count(self, text):
        """Convenience method to quickly get the total number of tokens for a given text."""
        encoded = self.encode(text)
        return len(encoded.tokens)