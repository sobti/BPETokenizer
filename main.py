# main.py

from registry import WikiRegistry
from downloader import WikiDownloader
from cleaner import WikiCleaner
from tokenizer_trainer import BPETokenizerTrainer
from fertility_analyzer import FertilityAnalyzer

if __name__ == "__main__":
    registry = WikiRegistry()
    downloader = WikiDownloader(registry)
    cleaner = WikiCleaner()
    
    # Target pages format: (page_name, language, number_of_downloads)
    pages = [
        ("India", "en", 9),
        ("भारत", "hi", 5),  
        ("భారతదేశం", "te", 9),               
        ("भारत", "bh", 4),        
    ]
    
    # 1. Download and Clean sequentially
    for page_name, language, num_downloads in pages:
        for _ in range(num_downloads):
            # Fetch the raw HTML using the title and language
            html, count = downloader.fetch_raw_html(page_name, language)
            
            if html:
                cleaner.clean_and_save(html, page_name, language, count)
            
    # 2. Train Tokenizer with NFKC normalization
    trainer = BPETokenizerTrainer()
    trainer.train()
    
    # 3. Analyze Fertility and Compute Score
    analyzer = FertilityAnalyzer()
    analyzer.analyze_and_save()