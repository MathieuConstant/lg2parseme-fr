# Generate lexicon

from lex.lg import FreeConstituentDistribution,EntryProperty,IDProperty, AdjPermutProperty, PpvProperty, DetPlurielProperty,DetDistribProperty,PassiveProperty
from lex.lexicon import entry
from lex.utils import post_processing
from xml.dom.minidom import Document
from lex.generatexml import entry2xmlelement


import argparse
import os


#property prop, list of properties to apply in first and second place
def process_titles_for_fixed(prop, properties,properties2,value=None):
    if FreeConstituentDistribution.isOfType(prop):
        properties.append(FreeConstituentDistribution(prop,value=value))
        properties2.append(None)
    elif EntryProperty.isOfType(prop):
        properties.append(EntryProperty(prop,value=value))
        properties2.append(None)
    elif IDProperty.isOfType(prop):
        properties.append(None)
        properties2.append(IDProperty(prop,value=value))
    elif AdjPermutProperty.isOfType(prop):
        properties.append(None)
        properties2.append(AdjPermutProperty(prop,value=value))
    elif PpvProperty.isOfType(prop):
        properties.append(PpvProperty(prop,value=value))
        properties2.append(None)
    elif DetPlurielProperty.isOfType(prop):
        properties.append(None)
        properties2.append(DetPlurielProperty(prop,value=value))
    elif DetDistribProperty.isOfType(prop):
        properties.append(None)
        properties2.append(DetDistribProperty(prop,value=value))
    elif PassiveProperty.isOfType(prop):
        properties.append(PassiveProperty(prop,value=value))
        properties2.append(None)
    else:
        properties.append(None)
        properties2.append(None)


def get_colomn_index(titles, table):
    tab = titles[:-1].split(';')
    #print(tab)
    for i in range(len(tab)):
       #print(tab[i][1:-1],table)
       if tab[i][1:-1] == table[:-8]:
           return i
    return None


def find_index(tab,value):
    indexes = [index for index in range(len(tab)) if tab[index] == 'à']
    if len(indexes) <= 0:
        return None
    return indexes[0]

def get_property_name_and_value(prop):
    tab = prop.split(' ')
    print(tab)

    i = find_index(tab,'à')
    if i is not None:
        n = tab[i+1]
        if len(n) == 2 and n[0] == 'N':
            return ('<ENT>Prép'+n[1],'à')
    return (None,None)
        #tab[i+1]+' =: à'

def add_properties_from_table_of_tables(filename, properties, properties2, table):
    f = open(filename)
    #print(table[:-8])
    f.readline()
    titles = f.readline()

    #print(titles[:-1])
    index = get_colomn_index(titles,table)

    i = 0
    for prop_line in f.readlines():
        prop = prop_line[:-1].split(';')
        if len(prop) <= index:
            continue
        p = prop[index]
        c = prop[0][1:-1]
        if '+' in p and c == 'C':
           print(prop[1],p)
           p = prop[1][1:-1]
           (p,v) = get_property_name_and_value(p)

           if p is not None:
               #print(p,v)
               process_titles_for_fixed(p, properties, properties2,value=v)
        i += 1
    #for prop in titles:
    #    process_titles_for_fixed(prop, properties, properties2)
    f.close()


if __name__ == "__main__":

   parser = argparse.ArgumentParser()
   parser.add_argument("table", help="the table filepath to be transformed and outputed")
   parser.add_argument("out", help="output dir")
   parser.add_argument("tot", help="the table of table filepath")
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
             process_titles_for_fixed(prop,properties,properties2)
         add_properties_from_table_of_tables(args.tot,properties,properties2, name)
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


