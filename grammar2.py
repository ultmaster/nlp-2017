import nltk
from nltk.corpus import brown
from nltk.grammar import CFG, Nonterminal

tbank_productions = set(production for sent in brown.tagged_sents()
                        for production in sent.productions())
tbank_grammar = CFG(Nonterminal('S'), list(tbank_productions))
parser = nltk.ChartParser(tbank_grammar)
print(tbank_grammar)
sent = 'the little bear saw the fine fat trout in the brook'.split(' ')
for tree in parser.parse(sent):
    print(tree)