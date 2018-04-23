# Generate lexicon

from lex.lg import FreeConstituentDistribution,EntryProperty,IDProperty, AdjPermutProperty, PpvProperty, DetPlurielProperty,DetDistribProperty,PassiveProperty
from lex.lexicon import entry
from lex.utils import post_processing
from xml.dom.minidom import Document
from lex.generatexml import entry2xmlelement


import argparse
import os

if __name__ == "__main__":

   parser = argparse.ArgumentParser()
   parser.add_argument("table", help="the table filepath to be transformed and outputed")
   parser.add_argument("out", help="output dir")
   args = parser.parse_args()

   name = os.path.basename(args.table)
   #print(name[:-8])
   doc = Document()
   root = doc.createElement('lex')
   doc.appendChild(root)

   f = open(args.table)
   fout = open(args.out+'/'+name[:-8]+'.xml','w')
   fout2 = open(args.out+'/'+name[:-8]+'.txt','w')
   titles=[]
   i=0
   for l in f:
      tab = [s[1:-1] for s in l[:-1].split(';')]
      if len(tab) == 1:
         break
      #print(tab)
      #print(titles)
      if i == 0: #this is the title line
         titles = tab
         properties = []
         properties2 = [] # properties to apply once all others are applied
         for prop in titles:
           if FreeConstituentDistribution.isOfType(prop):
               properties.append(FreeConstituentDistribution(prop))
               properties2.append(None)
           elif EntryProperty.isOfType(prop):
               properties.append(EntryProperty(prop))
               properties2.append(None)
           elif IDProperty.isOfType(prop):
               properties.append(None)
               properties2.append(IDProperty(prop))
           elif AdjPermutProperty.isOfType(prop):
               properties.append(None)
               properties2.append(AdjPermutProperty(prop))
           elif PpvProperty.isOfType(prop):
               properties.append(PpvProperty(prop))
               properties2.append(None)
           elif DetPlurielProperty.isOfType(prop):
               properties.append(None)
               properties2.append(DetPlurielProperty(prop))
           elif DetDistribProperty.isOfType(prop):
               properties.append(None)
               properties2.append(DetDistribProperty(prop))
           elif PassiveProperty.isOfType(prop):
               properties.append(PassiveProperty(prop))
               properties2.append(None)
           else:
                properties.append(None)
                properties2.append(None)
      else:
         e = entry(name[:-8])
         e.load_entry(properties, properties2, tab)
         post_processing(e)
         fout2.write(str(e))

         root.appendChild(entry2xmlelement(e, doc))


      i+=1

   doc.writexml(fout, indent="   ", addindent="   ", newl='\n')
   f.close()
   fout.close()
   fout2.close()


