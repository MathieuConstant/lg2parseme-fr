from lex.lg import DET
POSS='Poss'
NUM='Num'
MODIF='Modif'


from lex.lexicon import CECOMPL,COMPL


def post_processing_args(ent):
    '''
        removing args from entry that are empty (no realization nor lexical items)
    :param ent: entry to be post-processing
    :return: None
    '''

    consts = [const for const in ent.frame.args if const is not None and len(const.seq) == 0 and len(const.realizations) == 0]
    for c in consts:
        ent.frame.args.remove(c)


    #in one argument, if no prep and 'ce que P' realization => compl only
    for c in ent.frame.args:
        if c is not None:
          for r in c.realizations:
            if len(c.seq) == 0:
                cat = r.fs.get('cat')
                if cat == CECOMPL:
                    r.add('cat',COMPL)



def post_processing_lexical_items(ent):
    '''
     post-process lexical items
    :param ent: entry to be post processed
    :return: None
    '''

    for const in ent.frame.args:
        if const is not None:
           removeModif = None

           for coset in const.seq:
                  #print(coset)
                  #print('++--'+str(coset.length()))
              for comp in coset.compset:
                  ## Case Possi
                  if comp.word is not None and comp.word.startswith(POSS):
                    coref= comp.word[-1]
                    comp.word = None
                    comp.pos = DET
                    comp.add_feat('subtype',POSS)
                    comp.add_feat('agr',coref)

                  # Case Det:
                  if comp.word == DET:
                      comp.word = None
                      comp.pos = DET

                  # Case pos = Poss:
                  if comp.pos == POSS:
                      comp.word = None
                      comp.pos = DET
                      comp.add_feat('subtype', POSS)
                      comp.add_feat('agr', '0')

                  # Case Dnum
                  if comp.word == 'Dnum':
                     comp.word = None
                     comp.pos = DET
                     comp.add_feat('subtype',NUM)

                  # Case Lui-i : TODO

                  #case Modif
                  if comp.word == MODIF:
                      comp.word = None
                      const.add_property('fixed',False)
                      const.add_property('modifObl', True)
                      removeModif = comp
                  if removeModif is not None:
                      coset.compset.remove(removeModif)



def post_processing(ent):
    '''
    postprocess an entry after its loading from lg table
    :param ent: entrey to be postprocessed
    :return: None
    '''

    post_processing_lexical_items(ent)
    post_processing_args(ent)





