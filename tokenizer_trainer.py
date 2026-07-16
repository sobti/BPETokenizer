# tokenizer_trainer.py

import os
import glob
import requests
from tokenizers import Tokenizer, models, trainers,Regex,decoders
from tokenizers.normalizers import NFKC
from tokenizers.pre_tokenizers import Whitespace, Punctuation, Sequence, Split,Metaspace
from config import DATA_DIR, TOKENIZER_FILE


class BPETokenizerTrainer:
    """Handles training a BPE tokenizer."""

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

        # BPE tokenizer
        tokenizer = Tokenizer(
            models.BPE(
                unk_token="[UNK]"
            )
        )

        # Unicode normalization for multilingual text
        tokenizer.normalizer = NFKC()

        # Simple whitespace pre-tokenization
        tokenizer.pre_tokenizer = Sequence([Metaspace(),Split(Regex(r"\d{1,3}"), behavior="isolated")])

        # Trainer
        trainer = trainers.BpeTrainer(
            vocab_size=vocab_size,
            min_frequency=1,
            special_tokens=["[UNK]"],
            show_progress=True
        )

        tokenizer.decoder  = decoders.Metaspace()

        tokenizer.train(
            files=text_files,
            trainer=trainer

        )

        tokenizer.save(self.model_path)

        print("\nTokenizer training complete")
        print(f"Vocabulary size: {tokenizer.get_vocab_size()}")
        print(f"Saved to: {self.model_path}")

    
        return True