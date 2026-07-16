# Multilingual BPE Tokenizer & Fertility Optimization Experiment

## 🎯 Objective
To build a custom Byte-Pair Encoding (BPE) tokenizer from scratch with a strict `vocab_size = 10000`, targeting a subword fertility score of ~1.2 across four specific Wikipedia pages.

## 🛠️ Experiment Setup
* **Data Sources:** Wikipedia articles for "India" across 4 languages:
  * English (`en`) - Replicated 8 times.
  * Telugu (`te`) - Replicated 8 times.
  * Hindi (`hi`) - Replicated 5 times.
  * Bhojpuri (`bh`) - Replicated 4 times.
* **Data Strategy (Word Replication):** Text extraction utilizes append (`"a"`) mode combined with sequential download loops. This intentionally duplicates the text to artificially boost the frequency of specific words. This oversampling forces the BPE trainer to prioritize memorizing long regional words within the tight 10,000 token budget.
* **Libraries Used:** Hugging Face `tokenizers`, `BeautifulSoup` (for HTML scraping), `markdownify`, `regex`, and `requests`.

---

## 🧠 Tokenizer Architecture

The tokenizer is built using the Hugging Face `tokenizers` library with the following components:

1. **Core Model:** BPE (Byte-Pair Encoding) with `[UNK]` token fallback.
2. **Normalizer:** `NFKC` for consistent Unicode representation across scripts.
3. **Pre-Tokenizer Sequence:**
   * `Whitespace()`: Splits text by spaces.
   * `Punctuation()`: Isolates punctuation marks to prevent them from fusing to alphanumeric words.
   * `Split(Regex(r"\d{1,3}"))`: Chunks digits into groups of up to 3 (e.g., hundreds/thousands).
4. **Trainer Profile:** 
   * `vocab_size=10000`.
   * `min_frequency=1` (Ensures even single-occurrence words in the duplicated dataset receive tokens).
5. **Decoder:** `Metaspace` with `prepend_scheme="always"` and `replacement=" "`[cite: 15]. 

---

## 📊 Fertility Analysis & Results

### Scoring Logic
* Fertility is calculated by dividing the total number of generated tokens by the total number of baseline words. 
* To account for the `Punctuation()` pre-tokenizer, the baseline word count uses a regex (`r'\w+|[^\w\s]'`) to ensure alphanumeric words and individual punctuation marks are scored fairly. 

### Current Metrics
Based on the current evaluation, the tokenizer achieved the following fertility scores (Tokens per Word):
* **Telugu (`te`):** 1.3643.
* **Bhojpuri (`bh`):** 1.2024.
* **Hindi (`hi`):** 1.1748.
* **English (`en`):** 1.1362.

**Global Performance:**
* **Max Fertility:** 1.3643.
* **Min Fertility:** 1.1362.
* **Final Evaluation Score:** 4384.5402.

---

## 💻 Codebase Reference

### 1. `config.py`
```python
DATA_DIR = "data"
TEST_DATA_DIR = "data_test"
REGISTRY_FILE = "wiki_registry.json"
TOKENIZER_FILE = "bpe_tokenizer.json"
FERTILITY_FILE = "fertility_results.json"

## 🚀 Getting Started / How to Use

### Prerequisites
####Assuming you have cloned the repository and the trained vocabulary file (`bpe_tokenizer.json`) is already available in your directory, you      only need to install the Hugging Face `tokenizers` library to use it:

```bash
pip install tokenizers

from tokenizer import TokenizerHandler

# 1. Initialize the handler with the pre-trained model path
tokenizer = TokenizerHandler("bpe_tokenizer.json")

# 2. Define the text you want to process
text = "India's population is 1,428,627,663"

# 3. Encode text to token IDs
token_ids = tokenizer.encode_ids(text)
print(f"Token IDs: {token_ids}")

# 4. Decode token IDs back to a human-readable string
decoded_text = tokenizer.decode(token_ids)
print(f"Decoded Text: {decoded_text}")


