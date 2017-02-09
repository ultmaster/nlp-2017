import nltk
from nltk.draw.tree import TreeView

groucho_grammar = nltk.CFG.fromstring("""
S -> NP VP
PP -> P NP
NP -> Det Nom
Nom -> N | Adj Nom
VP -> V NP | VP PP
Det -> 'the'
Adj -> 'little' | 'fine' | 'fat'
N -> 'brook' | 'trout' | 'bear'
V -> 'saw'
P -> 'in'
""")


sent = 'the little bear saw the fine fat trout in the brook'.split(' ')
parser = nltk.ChartParser(groucho_grammar)
for tree in parser.parse(sent):
    TreeView(tree)._cframe.print_to_file('grammar.ps')