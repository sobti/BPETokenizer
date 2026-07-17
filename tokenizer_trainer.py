import os
import glob
import requests
from tokenizers import Tokenizer, models, trainers, Regex, decoders
from tokenizers.normalizers import NFKC
from tokenizers.pre_tokenizers import Whitespace, Punctuation, Sequence, Split, Metaspace
from config import DATA_DIR, TOKENIZER_FILE


class BPETokenizerTrainer:
    """Handles training a BPE tokenizer with strict URL and structural boundaries."""

    def __init__(self, data_dir=DATA_DIR, model_path=TOKENIZER_FILE):
        self.data_dir = data_dir
        self.model_path = model_path

    def train(self, vocab_size=10000):
        print("\n=== Training BPE Tokenizer ===")

        text_files = glob.glob(
            os.path.join(self.data_dir, "*_clean.txt")
        )

        if not text_files:
            print("No text files found in data directory.")
            return False

        print(f"Found {len(text_files)} training files")

        # Initialize BPE tokenizer
        tokenizer = Tokenizer(
            models.BPE(
                unk_token="[UNK]"
            )
        )

        # Unicode normalization for multilingual text uniformity
        tokenizer.normalizer = NFKC()

        # --- ADVANCED PRE-TOKENIZATION SEQUENCE ---
        # Combined into a single atomic Split block to prevent rules from shredding each other.
        tokenizer.pre_tokenizer = Sequence([
            # 1. Standardize and segment text based on space occurrences
            Metaspace(),
            
            # 2. THE UNIFIED ISOLATION MATRIX
            # Order matters: Longest/most specific rules match first.
            Split(Regex(
                r"https?://|"                                # Rule A: Keeps 'http://' and 'https://' perfectly unified
                r"Link:|Reference:|"                          # Rule B: Custom structural text markers
                r"#?cite|FOOTNOTE|"                           # Rule C: Generic citation cores
                r"www\.|"                                     # Rule D: Global domain prefixes
                r"\u2581[.,!?;:।॥،()\[\]{}/\-&=\"'_]+|"       # Rule E: PREFIX PUNCTUATION GROUPER (FIXED)
                                                              # Uses \u2581 to accurately catch the Metaspace character.
                                                              # Groups ' _' together as one common token, leaving 'India' intact.
                                                              # This guarantees exactly 2 tokens for instances like '_India' or '.venv'.
                r"[.,!?;:।॥،()\[\]{}/\-&=\"'_]+[\p{L}\p{N}]+|" # Rule F: INTERNAL PUNCTUATION ATTACHMENT
                                                              # Slices internal boundaries like 'formatics_Centre' into 'formatics' and '_Centre'.
                r"[.,!?;:।॥लय()\[\]{}/\-&=\"'_]"               # Rule G: Standard loose trailing/lone punctuation marks
            ), behavior="isolated"),
            
            # 3. Isolate numeric tokens (Your original rule)
            Split(Regex(r"\d{1,3}"), behavior="isolated"),
        ])

        # Trainer settings
        trainer = trainers.BpeTrainer(
            vocab_size=vocab_size,
            min_frequency=1,
            special_tokens=["[UNK]"],
            show_progress=True
        )

        # Setup symmetric decoding
        tokenizer.decoder = decoders.Metaspace()

        # Run training pipeline
        tokenizer.train(
            files=text_files,
            trainer=trainer
        )

        tokenizer.save(self.model_path)

        print("\nTokenizer training complete")
        print(f"Vocabulary size: {tokenizer.get_vocab_size()}")
        print(f"Saved to: {self.model_path}")

        return True