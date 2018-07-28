
FIXED='fixed'
LVC='lvc'

EPSILON='<E>'
DET = 'Det'

def get_value(value):
    if value == '+':
        return True
    elif value == '-':
        return False
    elif value == '<E>':
        return None
    return value


def tokenize(seq):
    seq.replace("'","' ")
    return seq.split(" ")


def get_property_value(default_value,value):
    if default_value is not None:
        return default_value
    return value


class LGProperty:
    def __init__(self, name,table=None,value=None):
        self.name = name
        self.table = table #optional
        self.value = value #optional: if constant property over the current table


    def apply(self, entry, value):
        '''
        apply on current lexical entry the property with the value value

        :param entry: the current lexical entry
        :param value: the value of the property
        :return: None
        '''
        return self.name + '=>' + value

    @staticmethod
    def isOfType(name,table=None):
        '''

        :param name: name of the property to be tested
        :param table: table (optional)
        :return: boolean whether the property name (in table table optionaly) is of the current property type
        '''
        pass


class FreeConstituentDistribution(LGProperty):
    def __init__(self, name,value=None):
        LGProperty.__init__(self,name,table=None, value=value)
        if(not FreeConstituentDistribution.isOfType(self.name,table=None)):
            raise RuntimeError('Is not a Free constituent distribution property')
        self.index = self.getIndex() # if N0 =: Nhum then 0
        self.rea = self.getRea()  # if N0 =: Nhum then Nhum


    def getIndex(self):
        return self.name[1]

    def getRea(self):
        return self.name.split('=: ')[1]

    def __str__(self):
        return str(self.index) + '--' + self.rea




    @staticmethod
    def isOfType(name, table=None):
        '''
        test whether the name of th property is of the form Ni =: X
        :param name: name of the property to be tested
        :param table: table (optional)
        :return: boolean whether the property name (in table table optionaly) is of the current property type
        '''
        if len(name) == 0:
            return False
        if name[0] != 'N':
            return False
        if name[1] not in '01234':
            return False
        prefix = name[0:2] + ' =: '
        if not name.startswith(prefix):
            return False
        tab = name.split('=:')
        if len(tab) != 2:
            return False
        return True


    def apply(self, entry, value):
        '''
        apply on current lexical entry the property with the value value

        :param entry: the current lexical entry
        :param value: the value of the property
        :return: None
        '''

        value = get_property_value(self.value,value)
        const = entry.frame.get_arg(self.index)
        value = get_value(value)
        if value is not None and value:
           const.add_realization(self.rea, value)


FreeN1Tables=['C_anp2']

class IDProperty(LGProperty):

    #used for general properties true for the whole table
    def __init__(self,table,mwetype,value=None):
        LGProperty.__init__(self, '', table=table, value = value)
        self.mwetype = mwetype

    def apply(self, entry, value):
        '''
        apply on current lexical entry the property with the value value

        :param entry: the current lexical entry
        :param value: the value of the property
        :return: None
        '''
        value = get_property_value(self.value,value)
        entry.id += '_'+value
        entry.properties["mwetype"] = self.mwetype
        for const in entry.frame.args:
            if self.mwetype == FIXED and const is not None and not const.has_realizations():
               const.add_property("fixed",True)



    @staticmethod
    def isOfType(name,table=None):
        '''

        :param name: name of the property to be tested
        :param table: table (optional)
        :return: boolean whether the property name (in table table optionaly) is of the current property type
        '''
        return name == '<ID>'


class EntryProperty(LGProperty):

    def __init__(self, name,value=None):
        LGProperty.__init__(self,name,table=None, value=value)
        if(not EntryProperty.isOfType(self.name,table=None)):
            raise RuntimeError('Is not a ENT<> property')
        self.pos = self.getPos() # if <ENT>Det1 then Det # if <ENT><faire> then V
        self.index = self.getIndex()  # if <ENT>Det1 then '1' # if <ENT><faire> then None
        #is_lexicalized_verb: rule=<ENT><.*>
        #or is component of a constituent i: two possible forms <ENT>.*i or <ENT>


    def getIndex(self):
        if self.name[-1] == '>' and self.name[5] == '<':
            return None
        if self.name[-1] in '0123456789cv':
            return self.name[-1]
        return 'n'

    def getPos(self):
        if self.name[-1] == '>' and self.name[5] == '<':
            return 'V'
        if self.name[-1] in '0123456789cv':
            return self.name[5:-1]
        return self.name[5:]


    def __str__(self):
        ind = 'HEAD'
        if self.index is not None:
            ind = self.index
        return str(self.pos) + '--' + ind


    def apply(self, entry, value):
        '''
        apply on current lexical entry the property with the value value

        :param entry: the current lexical entry
        :param value: the value of the property
        :return: None
        '''
        if self.index != None:
            #if self.index == 'c':
            #    self.index = '1'
            const = entry.frame.get_arg(self.index)
        else:
            const = entry.frame.get_head()
        value = get_property_value(self.value, value)
        value = get_value(value)
        if value is not None and isinstance(value,str):
            items = tokenize(value)
            entry.id += '_'+'_'.join(items)
            if len(items) == 1:
               const.add_component({'word':value, 'pos':self.pos})
            else: #case of badly tokenized values in LG tables
                i = 0
                for it in items:
                    if i == 0 or self.index is not None:
                      const.add_component({'word':it})
                    i += 1




    @staticmethod
    def isOfType(name, table=None):
        '''
        test whether the name of th property is of the form <ENT>X
        :param name: name of the property to be tested
        :param table: table (optional)
        :return: boolean whether the property name (in table table optionaly) is of the current property type
        '''

        # Handle Ppv in an other type of prperty
        if not name.startswith('<ENT>') or name == '<ENT>Ppv':
            return False
        return True



class VsupProperty(LGProperty):

    def __init__(self, name,value=None):
        LGProperty.__init__(self,name,table=None, value=value)
        if(not VsupProperty.isOfType(self.name,table=None)):
            raise RuntimeError(name + ' is not a Vsup property')
        self.verb = self.getVerb() # if Vsup =: faire then verb=faire



    def getVerb(self):
        return self.name[8:]


    def __str__(self):
        return 'support verb:' + self.verb


    def apply(self, entry, value):
        '''
        apply on current lexical entry the property with the value value

        :param entry: the current lexical entry
        :param value: the value of the property
        :return: None
        '''

        const = entry.frame.get_head()
        value = get_property_value(self.value, value)
        value = get_value(value)
        if value is not None and value:
               const.add_component({'word':self.verb, 'pos':'V'})




    @staticmethod
    def isOfType(name, table=None):
        '''
        test whether the name of th property is of the form <ENT>X
        :param name: name of the property to be tested
        :param table: table (optional)
        :return: boolean whether the property name (in table table optionaly) is of the current property type
        '''

        # Handle Ppv in an other type of prperty
        if not name.startswith('Vsup =: '):
            return False
        return True


class PpvProperty(LGProperty):

    def __init__(self, name,value=None):
        LGProperty.__init__(self,name,table=None,value=value)
        if(not PpvProperty.isOfType(self.name,table=None)):
            raise RuntimeError('Is not a Ppv property')
        self.ppv = self.name[7:]



    def __str__(self):
        return "TODO: Ppv Property"

    def apply(self, entry, value):
        '''
        apply on current lexical entry the property with the value value

        :param entry: the current lexical entry
        :param value: the value of the property
        :return: None
        '''

        const = entry.frame.get_head()
        value = get_property_value(self.value, value)
        value = get_value(value)
        if value is not None and value:
            if self.ppv.endswith(' figé'):
                self.ppv = 'ppv-'+self.ppv[:-5]
            const.add_property(self.ppv,value)



    @staticmethod
    def isOfType(name, table=None):
        '''
        test whether the name of th property is of the form <ENT>X
        :param name: name of the property to be tested
        :param table: table (optional)
        :return: boolean whether the property name (in table table optionaly) is of the current property type
        '''

        # Handle Ppv in an other type of prperty
        if not name.startswith('Ppv =: '):
            return False
        #print('XXXXXXXXXX')
        return True




class AdjPermutProperty(LGProperty):

    def __init__(self, name,value=None):
        LGProperty.__init__(self,name,table=None,value=value)
        if(not AdjPermutProperty.isOfType(self.name,table=None)):
            raise RuntimeError('Is not an Andj Permut property')
        #self.pos = self.getPos() # if <ENT>Det1 then Det # if <ENT><faire> then V
        self.index = self.getIndex()  # if <ENT>Det1 then '1' # if <ENT><faire> then None


    def getIndex(self):
        if self.name[3] in '0123456789c':
            return self.name[3]
        return None


    def __str__(self):
        return "Adj Permut at position "+str(self.index)


    def apply(self, entry, value):
        '''
        apply on current lexical entry the property with the value value

        :param entry: the current lexical entry
        :param value: the value of the property
        :return: None
        '''

        if self.index != None:
            #if self.index == 'c':
            #    self.index = '1'
            const = entry.frame.get_arg(self.index)
            value = get_property_value(self.value, value)
            value = get_value(value)
            if value is not None and value:
               #print("======",const.seq)
               adj = [(i,c) for i,c in enumerate(const.seq) for x in c.get_compset() if x.pos == 'Adj']
               if len(adj) <=0:
                   return
               adj = adj[0]
               #print("======", adj)
               if adj is not None:
                  noun = [(i,c) for i,c in enumerate(const.seq) for x in c.get_compset() if x.pos == 'C']
                  if len(noun) <= 0:
                      return
                  noun = noun[0]
                  if noun is not None:
                     const.seq[noun[0]] = adj[1]
                     const.seq[adj[0]] = noun[1]
                     # we need index of noun and adj
                     #print("I found Adj and Noun to permut: "+str(adj)+" "+str(noun))




    @staticmethod
    def isOfType(name, table=None):
        '''
        test whether the name of th property is of the form <ENT>X
        :param name: name of the property to be tested
        :param table: table (optional)
        :return: boolean whether the property name (in table table optionaly) is of the current property type
        '''

        if not name.startswith('Adj') or not name.endswith(' permut obl'):
            return False
        return True




class DetPlurielProperty(LGProperty):

    def __init__(self, name,value=None):
        LGProperty.__init__(self,name,table=None,value=value)
        if(not DetPlurielProperty.isOfType(self.name,table=None)):
            raise RuntimeError('Is not an Det plurial property')

        self.index = self.getIndex()  # if Det1 then '1'


    def getIndex(self):
        if self.name[3] in '0123456789c':
            return self.name[3]
        return None


    def __str__(self):
        return "Det Plurial at position "+str(self.index)


    def apply(self, entry, value):
        '''
        apply on current lexical entry the property with the value value; we assume that if the value is true then the constituent might vary morphologicaly (the head of contituent becomes lemma)

        :param entry: the current lexical entry
        :param value: the value of the property
        :return: None
        '''

        if self.index != None:
            #if self.index == 'c':
            #    self.index = '1'
            const = entry.frame.get_arg(self.index)
            value = get_property_value(self.value, value)
            value = get_value(value)
            if value is not None and value:
               #print([str(c) for c in const.seq])
               det = [(c,cs) for cs in const.seq for c in cs.compset if c.pos == 'Det' or c.pos is None][0]
               if det is not None:
                  det[1].compset.remove(det[0])
                  const.add_property('fixed',False)
                  nouns = [c for cs in const.seq for c in cs.compset if c.pos == 'C']

                  if len(nouns) > 0:
                      noun = nouns[0]
                      noun.lemma = noun.word
                      noun.word = None




    @staticmethod
    def isOfType(name, table=None):
        '''
        test whether the name of th property is of the form Deti pluriel
        :param name: name of the property to be tested
        :param table: table (optional)
        :return: boolean whether the property name (in table table optionaly) is of the current property type
        '''

        if not name.startswith('Det') or not name.endswith(' pluriel'):
            return False
        return True


class DetDistribProperty(LGProperty):

    def __init__(self, name,value=None):
        LGProperty.__init__(self,name,table=None,value=value)
        if(not DetDistribProperty.isOfType(self.name,table=None)):
            raise RuntimeError('Is not a Det distribution property')

        self.index = self.getIndex()  # if Det1 then '1'
        self.rea = self.getRea() #if Det1 =: Dind then 'Dind'


    def getIndex(self):
        if self.name[3] in '0123456789c':
            return self.name[3]
        return None

    def getRea(self):
        if self.name.endswith('Dind') or self.name.endswith('indéf'):
            return 'indef'
        if self.name.endswith('Def'):
            return 'def'
        return None


    def __str__(self):
        return "Det distrib at position "+str(self.index)


    def apply(self, entry, value):
        '''
        apply on current lexical entry the property with the value value; we assume that if the value is true then the constituent might vary morphologicaly (the head of contituent becomes lemma)

        :param entry: the current lexical entry
        :param value: the value of the property
        :return: None
        '''

        if self.index is not None and self.rea is not None:
            #if self.index == 'c':
            #    self.index = '1'
            const = entry.frame.get_arg(self.index)
            value = get_property_value(self.value, value)
            value = get_value(value)
            if value is not None and value:

               dets = [(c,cs) for cs in const.seq for c in cs.compset if c.pos == 'Det' or c.pos is None]
               if len(dets) > 0:
                   det = dets[0]
                   if self.rea == 'def':
                       det[1].add_component({'pos':'Det','lemma':'le'})
                   elif self.rea == 'indef':
                       det[1].add_component({'pos': 'Det', 'lemma': 'un'})




    @staticmethod
    def isOfType(name, table=None):
        '''
        test whether the name of th property is of the form Deti pluriel
        :param name: name of the property to be tested
        :param table: table (optional)
        :return: boolean whether the property name (in table table optionaly) is of the current property type
        '''

        if name.startswith('Det1 =: '):
            return True
        return False


class PassiveProperty(LGProperty):

    def __init__(self, name,value=None):
            LGProperty.__init__(self, name, table=None, value=value)
            if (not PassiveProperty.isOfType(self.name, table=None)):
                raise RuntimeError('Is not passive property')




    def __str__(self):
            return "Det distrib at position " + str(self.index)

    def apply(self, entry, value):
            '''
            apply on current lexical entry the passive property with the value value;
            :param entry: the current lexical entry
            :param value: the value of the property
            :return: None
            '''
            value = get_property_value(self.value, value)
            value = get_value(value)

            entry.properties['passive']=value


    @staticmethod
    def isOfType(name, table=None):
            '''
            test whether the name of th property is of the form Deti pluriel
            :param name: name of the property to be tested
            :param table: table (optional)
            :return: boolean whether the property name (in table table optionaly) is of the current property type
            '''

            return name == '[passif]'