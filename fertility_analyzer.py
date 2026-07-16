import os
import json
import glob
from config import DATA_DIR, TOKENIZER_FILE, FERTILITY_FILE, TEST_DATA_DIR
import regex as re

# Import the new encoder/decoder class
from tokenizer import TokenizerHandler

class FertilityAnalyzer:
    """Calculates global and per-language subword fertility statistics."""
    
    def __init__(self, tokenizer_path=TOKENIZER_FILE, data_dir=TEST_DATA_DIR):
        self.tokenizer_path = tokenizer_path
        self.data_dir = data_dir
        
        # Initialize the tokenizer handler
        try:
            self.tokenizer_handler = TokenizerHandler(self.tokenizer_path)
        except FileNotFoundError as e:
            print(e)
            self.tokenizer_handler = None

    def analyze_and_save(self, output_json_path=FERTILITY_FILE):
        print("\n=== Calculating Language Fertility ===")
        
        if not self.tokenizer_handler:
            return
            
        text_files = glob.glob(os.path.join(self.data_dir, "*_clean.txt"))
        
        # Gather text content aggregated by language
        lang_texts = {}
        for file_path in text_files:
            lang = os.path.basename(file_path).split("_")[0]
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            lang_texts[lang] = lang_texts.get(lang, "") + "\n" + content

        language_stats = {}
        fertility_scores = []
        
        for lang, raw_text in lang_texts.items():
            # Count alphanumeric words AND individual punctuation marks as valid baseline words
            num_words = len(re.findall(r'\w+|[^\w\s]', raw_text)) 
            
            if num_words == 0:
                continue
                
            # Use the TokenizerHandler to get the token count
            num_tokens = self.tokenizer_handler.get_token_count(raw_text)
            
            # Calculate overall fertility for this language
            fertility = num_tokens / num_words
            fertility_scores.append(fertility)
            
            language_stats[lang] = {
                "total_words": num_words,
                "total_tokens": num_tokens,
                "fertility": round(fertility, 4)
            }
            
            print(f"[{lang.upper()}] Words: {num_words} | Tokens: {num_tokens} | Fertility: {round(fertility, 4)}")

        if not fertility_scores:
            print("No valid text data found to calculate fertility.")
            return

        # Calculate Global Max, Min, and Score ACROSS languages
        max_fert = max(fertility_scores)
        min_fert = min(fertility_scores)
        diff = max_fert - min_fert
        
        # Safe division check in case max equals min (e.g., only one language was processed)
        final_score = round(1000 / diff, 4) if diff > 0 else 0.0

        global_stats = {
            "max_fertility": round(max_fert, 4),
            "min_fertility": round(min_fert, 4),
            "final_score": final_score
        }
        
        print("-" * 40)
        print(f"[GLOBAL] Max Fertility (Across Languages): {round(max_fert, 4)}")
        print(f"[GLOBAL] Min Fertility (Across Languages): {round(min_fert, 4)}")
        print(f"[GLOBAL] Final Score (1000 / (Max-Min)): {final_score}")
        print("-" * 40)

        # Structure the final JSON output
        final_results = {
            "languages": language_stats,
            "global_stats": global_stats
        }


        # Save stats to JSON
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(final_results, f, indent=4)
            
        print(f"\nFertility statistics saved to: {output_json_path}")
if __name__ == "__main__":
       analyzer = FertilityAnalyzer(TOKENIZER_FILE, TEST_DATA_DIR)
       analyzer.analyze_and_save()
       tokenizerHandler=TokenizerHandler(TOKENIZER_FILE)
       print(tokenizerHandler.encode_ids("India's population is 1,428,627,663"))
