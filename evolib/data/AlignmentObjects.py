from evolib.stats.StatObjects import IOstats

from evolib.lib.DataObjects import BinaryTable, SeqTable
from evolib.lib.DNAmethods import binarizeDNA

class DnaPopulationData(IOstats):
    """
    Class representation of DNA sequences from multiple 
    samples. 
    """
    def __init__(self, seqs, ids = None):
        
        if isinstance(seqs, list) is False:
            raise TypeError, 'List expected.'
        
        n = len(seqs)
        
        if isinstance(ids, list) is False:
            if ids is None:
                ids = self._create_ids(n)
            else:
                raise TypeError, 'List expected.'
            
        self._from_sequence(self, seqs, ids)
        self.pop_nsam = None


    def _create_ids(self, nseqs):
        """
        Creates a list of sequence ids equal to the number 
        of sequences as shown in the examples below:
           ['seq1', 'seq2', 'seq3']
           ['seq01', 'seq02', ...'seq24']
        """
        ids = []
        for i in range(nseqs):
            seqnum = i + 1
            num_zeros = len(str(nseqs)) - len(str(seqnum))
            zeros = '0' * num_zeros
            id1 = 'seq' + zeros + str(seqnum)
            ids.append(id1)
            
        return ids
    
    
    def _from_sequence(self, seqs, ids):
        
        self.seqs = seqs
        self.ids = ids
        
        self.DNAdata = SeqTable(seqs)
        self.IOdata = self._get_IOdata(self.DNAdata)
    
    
    def _get_IOdata(self, seqs):
        
        self.validSites = 0
        IO = BinaryTable()
        self.sites = []
        for site in seqs.seqsBySite():
            self.sites.append(site)
            if site.hasMissingData():
                pass
            elif site.numberOfAlleles() > 2:
                pass
            elif site.numberOfAlleles() == 1:
                self.validSites += 1
            else:
                self.validSites += 1
                siteIO = binarizeDNA(site.alleles())
                IO.append(siteIO)
                
        return IO

