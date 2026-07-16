from tokenizer import TokenizerHandler

def test():

    tokenizerHandler = TokenizerHandler("/Users/punitsobti/Desktop/wiki/bpe_tokenizer.json")
    print(tokenizerHandler.encode_ids("India's population is 1,428,627,663"))
    print(tokenizerHandler.decode(tokenizerHandler.encode_ids("India's population is 1,428,627,663")))
    

if __name__ == "__main__":
    test()
      
  
       
