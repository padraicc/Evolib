from evolib.tools.GeneralMethods import create_ids

from evolib.stats.StatObjects import IOstats
from evolib.generic.AlignmentSite import Site

from evolib.data.DataObjects import SeqTable, IOtable
from evolib.tools.DNAmethods import booleanDNA, booleanIO
from evolib.generic.GeneticSequence import DNAsequence

class DnaPopulationData(IOstats):
    """
    Class representation of DNA sequences from multiple 
    samples. 
    """
    def __init__(self, *args):

        if len(args) == 1:
            seqs, ids = self._from_sequence(args[0])
        elif len(args) == 2:
            seqs, ids = self._from_sequence(args[0], args[1])
        else:
            raise TypeError, "Wrong number of arguments"
        
        self._attach_data(seqs, ids)


    def _from_sequence(self, seqs, ids = None):
    
        if isinstance(seqs, list) is False:
            raise TypeError, 'List expected.'
        
        n = len(seqs)
        
        if isinstance(ids, list) is False:
            if ids is None:
                ids = create_ids(n, "seq")
            else:
                raise TypeError, 'List expected.'

        return seqs, ids
        

    def _attach_data(self, sequences, ids):
        
        self.DNAdata = SeqTable(sequences, ids)
        self.IOdata = self._get_IOdata(self.DNAdata)

    ######
        
    def __len__(self):
        return len(self.DNAdata)
        
    ######
    
    def _get_IOdata(self, seqs):

        self.validSites = 0
        io = []
        
        for site in seqs.iter_sites():

            SiteClass = Site(site)
            
            if SiteClass.hasMissingData():
                pass
            elif SiteClass.numberOfAlleles() > 2:
                pass
            elif SiteClass.numberOfAlleles() == 1:
                self.validSites += 1
            else:
                self.validSites += 1
                siteIO = booleanDNA(SiteClass.alleles())
                io.append(siteIO)

        IO = IOtable(io)
                
        return IO

        ######
            
    def ids(self):
        return self.DNAdata.ids


    def nsamples(self):
        return self.__len__()


    def sequences(self):
        return self.DNAdata.sequences

    
    def length(self):
        return self.validSites

    ######

    def index(self, key):
        return self.DNAdata.index(key)

    def pop(self, index = None):
        seq, seqid = self.DNAdata.pop(index)
        self.IOdata = self._get_IOdata(self.DNAdata)
        
        return DNAsequence(seq, seqid)

    ######

    def coding(self, refseq):

        dna = ['A', 'T', 'G', 'C', 'a', 't', 'g', 'c']
        nsam = self.nsamples()
        
        inc = (i for i in xrange(len(refseq)) if refseq[i] in dna)
        cds_seqs = ['' for j in xrange(nsam)]

        for site in inc:
            for ind in xrange(nsam):
                cds_seqs[ind] += self.DNAdata.sequences[ind][site]
            
        return type(self)(cds_seqs, self.DNAdata.ids)

    

###### ######

class IOPopulationData(IOstats):

    def __init__(self, seqs):

        self.IOdata = self._get_IOdata(seqs)


    def _get_IOdata(self, seqs):
        
        io = []
        if seqs != []:
            for s in range(len(seqs[0])):
                site = ''.join([f[s] for f in seqs[:]])
                bio = booleanIO(site)
                io.append(bio)
                
        IO = IOtable(io)
        
        return IO