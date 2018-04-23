

INF='inf'
COMPL='compl'
CECOMPL='ce-compl'




class component:
    '''
    represents a lexical component:
    - a word
    - a lemma
    - part-of-speech
    - other features
    '''

    def __init__(self):
        self.word = None
        self.lemma = None
        self.pos = None
        self.feats = dict()

    def set_word(self,word):
        self.word = word

    def set_pos(self,pos):
        self.pos = pos

    def add_feat(self,att,val):
        self.feats[att] = val

    def __str__(self):
        w = self.word
        if w is None:
            w = '_'
        p = self.pos
        if p is None:
            p = '??'
        l = ''
        if self.lemma is not None:
            l = self.lemma
        r = ''
        for a in self.feats:
               r += ', '+ a + "=" + self.feats[a]

        return '('+w+','+ l+', '+p+r+')'



class compoalts:
    '''
    a set of alternative components at a given position
    '''

    def __init__(self):
        self.compset = []


    def length(self):
        return len(self.compset)


    def add_component(self,feats):
        c = component()
        for f in feats:
            val = feats[f]
            if f == 'word':
                c.word = val
            elif f == 'lemma':
                c.lemma = val
            elif f == 'pos':
                c.pos = val
            else:
                c.feats[f] = val
        self.compset.append(c)
        return c


    def get_compset(self):
        return self.compset


    def __str__(self):

        res = ''
        for c in self.compset:
            res += '|' + str(c)
        if len(res) > 0:
            return res[1:]
        return ''



class realization:
    '''
      a realization is a feature set
      ex1: cat=compl;mood=subj
      ex2: cat=NP;hum=true
    '''

    def __init__(self):
        self.fs = dict()

    def add(self,att,val):
        self.fs[att] = val


    def __str__(self):
        return str(self.fs)

class constituent:
    '''
    Represents a constituent including
    - type: NP, completive[subjonctive/indicative], infinitive
    - a function (subj, obj, ...)?
    - semantic properties (hum,nothum)
    - lexical sequence
    - a set of possible realisations (NP, INF, COMPL)
    - a set of syntactic dependents (of type constituent)
    '''

    def __init__(self,id):
        self.id = id
        self.type = None
        self.func = None
        self.realizations = []
        self.properties = dict()
        self.seq = []
        self.text = None
        self.deps = []


    def has_realizations(self):
        return len(self.realizations) != 0

    def add_property(self,att,val):
        self.properties[att] = val

    def add_realization(self,att,value):
        if att == 'Nnr':
            if value:
                rea = realization()
                rea.add('cat',INF)
                self.realizations.append(rea)
                rea = realization()
                rea.add('cat',COMPL)
                self.realizations.append(rea)
        elif att == 'Nhum':
            if value:
              rea = realization()
              rea.add('cat','NP')
              rea.add('hum',value)
              self.realizations.append(rea)
        elif att == 'N-hum':
            if value:
                rea = realization()
                rea.add('cat', 'NP')
                rea.add('nothum', value)
                self.realizations.append(rea)
        elif att == 'ce Qu Pind':
            if value:
                rea = realization()
                rea.add('cat',CECOMPL)
                rea.add('mood','ind')
                self.realizations.append(rea)
        elif att == 'ce Qu Psubj':
            if value:
                rea = realization()
                rea.add('cat',CECOMPL)
                rea.add('mood','subj')
                self.realizations.append(rea)
        elif att[0] == 'V' and att[2:6] =='-inf':
            if value:
                rea = realization()
                rea.add('cat',INF)
                rea.add('ref',att[1])
                self.realizations.append(rea)


    def add_component(self,feats):
        cs = compoalts()
        c = cs.add_component(feats)
        self.seq.append(cs)
        #print("---",self.seq[0])

    def add_component_in_componentset(self,cs):
        cs.add_component()



    def __str__(self):
        indent = ' '*5
        indent2 = indent*2
        indent3 = indent*3

        s = indent+'(VERB\n'
        if self.id >= 0:
           s = indent+'('+str(self.id)+'\n'

        if len(self.properties) != 0:
            s += indent2 + 'Properties:\n'
        for att in self.properties:
            s += indent3 + str(att) + '=' + str(self.properties[att]) + '\n'

        if len(self.realizations) != 0:
            s += indent2+'Realizations:\n'
        for r in self.realizations:
            s += indent3 + str(r)+'\n'

        if len(self.seq) != 0:
            s += indent2+'Lexical items:\n'
        s += indent3
        for c in self.seq:
            s += str(c)+' '
        s += '\n'+indent + ')'

        return s
        #return str([str(s) for s in self.seq])+'\n'+str(self.properties)+'\n'+str([str(r) for r in self.realizations])





class frame:
    '''
       Represents a syntactic frame with possible lexicalized constituents:
       - head (lexicalized labeled constituent)
       - arguments
    '''

    def __init__(self):
        self.head = None # syntactic lexical head
        self.args = [] # syntactic arguments (constituents)
        self.families = [] #corresponding family names in xmg grammar

    def get_arg(self, index):
        if len(self.args) <= index:
            self.args =self.args + [None]*(index + 1)
        if self.args[index] is None:
            self.args[index] = constituent(index)
        return self.args[index]

    def get_head(self):
        if self.head is None:
            self.head = constituent(-1)
        return self.head

    def __str__(self):
        s = 'FRAME:\n'
        s += str(self.head)+'\n'
        for c in self.args:
            if c is not None:
               s += str(c)+'\n'
        return s



class entry:
    '''
    Represents a lexical entry with:
    - an id
    - an history of changes
    - some properties
    - a syntactic frame (main construction)
    - a set of syntactic alternatives (frames)
    - set of defining criteria (CRAN, ID, LEX, ...)
    '''

    def __init__(self,table:str):
        self.id = table
        self.changes = []
        self.properties = dict()
        self.criteria = dict()
        self.frame = frame()
        self.alternatives = []


    def load_entry(self, properties, properties2, raw_entry):
        '''
        load entry in an entry instance from the squence of properties and the raw entry from LG table

        :param properties: sequence of LGProperty to be applied on raw_entry from LG table
        :param properties2: second sequence of LGProperty to be applied on raw_entry from LG table
        :param raw_entry: sequence of feature values
        :return: None
        '''

        i = 0
        for p in properties:
            if p is not None:
               p.apply(self,raw_entry[i].strip())
            i += 1
        i = 0
        for p in properties2:
            if p is not None:
                p.apply(self, raw_entry[i].strip())
            i += 1



    def __str__(self):
        return str(self.id)+'\nProperties: '+str(self.properties)+'\n=='+str(self.frame)


