fin = open("test.html", "r")
text = fin.read()
fin.close()

fout = open("test.html", "w")
fout.write(text.replace(' ', '\t'))
fout.close()