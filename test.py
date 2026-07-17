from tokenizer import TokenizerHandler

def test():

    tokenizerHandler = TokenizerHandler("/Users/punitsobti/Desktop/wiki/bpe_tokenizer.json")
    tokenizerHandler1 = TokenizerHandler("/Users/punitsobti/Desktop/wiki/vocab.json")
    print(tokenizerHandler.encode_ids("https://hi.wikipedia.org/wiki/भारत#cite_ref-1"))
    print(tokenizerHandler.decode(tokenizerHandler.encode_ids("https://hi.wikipedia.org/wiki/भारत#cite_ref-1")))
    print(tokenizerHandler.decode(tokenizerHandler.encode_ids("India's population is 1,423,676,878")))
    print(tokenizerHandler.encode_ids("India is great country123#.I am qweee"))
    print(tokenizerHandler.encode_ids("India_india i am"))
    print(tokenizerHandler.encode_ids("https://"))
    print(tokenizerHandler.decode(tokenizerHandler.encode_ids("India india i am")))
    print("------------------------------------------------------------------")

    print(tokenizerHandler1.encode_ids("https://hi.wikipedia.org/wiki/भारत#cite_ref-1"))
    print(tokenizerHandler1.decode(tokenizerHandler1.encode_ids("https://hi.wikipedia.org/wiki/भारत#cite_ref-1")))
    print(tokenizerHandler1.decode(tokenizerHandler1.encode_ids("India's population is 1,423,676,878")))
    print(tokenizerHandler1.encode_ids("India is great country123#.I am qweee"))
    print(tokenizerHandler1.encode_ids("India_india i am"))
    print(tokenizerHandler.encode_ids("https://"))
    print(tokenizerHandler1.decode(tokenizerHandler1.encode_ids("India india i am#population election")))

if __name__ == "__main__":
    test()
      


       
