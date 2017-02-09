import nltk

text = '''
he PRP B-NP
accepted VBD B-VP
the DT B-NP
position NN I-NP
of IN B-PP
vice NN B-NP
chairman NN I-NP
of IN B-PP
Carlyle NNP B-NP
Group NNP I-NP
, , O
a DT B-NP
merchant NN I-NP
banking NN I-NP
concern NN I-NP
. . O
'''

# For visualize only (stupid)
beauty = """(S
  (NP (PRP he))
  (VP (VBD accepted))
  (NP (DT the) (NN position))
  (PP (IN of))
  (NP (NN vice) (NN chairman))
  (PP (IN of))
  (NP (NNP Carlyle) (NNP Group))
  (, ,))
"""

tree = nltk.chunk.conllstr2tree(text)
from nltk.tree import Tree
from nltk.draw.tree import TreeView
t = Tree.fromstring(beauty)
print(t)
TreeView(t)._cframe.print_to_file('chunking.ps')
