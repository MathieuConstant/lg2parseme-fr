from lex.lexicon import entry,constituent,component,realization
from xml.dom.minidom import Document


def getnode(att:str,val:str,doc:Document):
    w = doc.createElement(att)
    wn = doc.createTextNode(str(val))
    w.appendChild(wn)
    return w

def create_node(att:str,val:str,doc:Document,parent):
    if val is not None:
        parent.appendChild(getnode(att,val,doc))


def comp2xmlelement(comp:component,doc:Document):
    ce = doc.createElement('component')
    create_node('word',comp.word,doc,ce)
    create_node('pos', comp.pos, doc, ce)
    create_node('lemma', comp.lemma, doc, ce)
    for f in comp.feats:
        create_node(f,comp.feats[f],doc,ce)

    return ce


def rea2xmlelement(rea:realization,doc:Document):
    r = doc.createElement('realization')
    for f in rea.fs:
        create_node(f,rea.fs[f],doc,r)
    return r

def const2xmlelement(const:constituent, doc:Document,ishead=False):
    name = 'constituent'
    if ishead:
       name = 'head'
    c = doc.createElement(name)
    if not ishead:
       c.setAttribute('rid',str(const.id))
    if len(const.properties) > 0:
        ps = doc.createElement('properties')
        c.appendChild(ps)
        for prop in const.properties:
            p = doc.createElement('property')
            ps.appendChild(p)
            p.setAttribute(prop,str(const.properties[prop]))

    if len(const.seq) > 0:
        items = doc.createElement('items')
        c.appendChild(items)
        for cs in const.seq:
            cse = doc.createElement('componentset')
            items.appendChild(cse)
            for comp in cs.compset:
               compe = comp2xmlelement(comp,doc)
               cse.appendChild(compe)

    if len(const.realizations) > 0:
        reas = doc.createElement('realizations')
        c.appendChild(reas)
        for rea in const.realizations:
            r = rea2xmlelement(rea,doc)
            reas.appendChild(r)

    return c


def entry2xmlelement(ent:entry, doc:Document):
    e = doc.createElement('entry')
    e.setAttribute('id',ent.id)
    frame = ent.frame
    f = doc.createElement('frame')
    e.appendChild(f)
    h = const2xmlelement(frame.head,doc,ishead=True)
    e.appendChild(h)
    for const in frame.args:
        if const is not None:
          c = const2xmlelement(const,doc)
          f.appendChild(c)

    #properties = ent.properties
    return e

