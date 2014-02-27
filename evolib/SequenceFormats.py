from VCFrow import ROW_BASECLASS, ROW_BASECLASS_OLD
from VCFcolumns import CHROM, POS, ID, REF, ALT, QUAL, FILTER, INFO, FORMAT, SAMPLE


class VariantCallFormat():
    """
    
    Usage:
    
    VariantCallFormat(filename)
    
    Returns a VCF class. Each row is represented by a <ROWCLASS>, 
    with each column represented by a <COLCLASS>.
    
    Example:
    
        >>> from SequenceFormats import VariantCallFormat
        >>> myVCF = VariantCallFormat("data.vcf")
        >>> for bp in myVCF:
        >>>     print bp['CHROM'], bp['POS'], bp['REF'], bp.genotypes(), bp.heterozygosity()
    """
    
    def __init__(self, file_name):
        
        self.file_name = file_name
        self.header = self.get_header(file_name)
        
        nsamples = len(self.header) - 9
        self.col_classes = [CHROM, POS, ID, REF, ALT, QUAL, FILTER, INFO, FORMAT] + [SAMPLE] * nsamples
        
        self.chromosome_info = dict(self.chr_info())
        
        
    def __iter__(self):
        for row in self.row_iter():
            yield row
            
    
    def row_iter(self):
        
        file = open(self.file_name, 'r')
        
        for line in file:
            
            if line.startswith('#') is False:
                
                value_list = line.rstrip().split('\t')
                v_col_row = ROW_BASECLASS(value_list, self.col_classes, self.header)
                
                yield v_col_row
                
                
    def chr_info(self):
        
        chromosomes = []
        past_chrom = None
        reverse = None
        
        file = open(self.file_name, 'r')
        
        for row in file:
            
            if row.startswith('#') is False:
                
                value_list = row.rstrip().split('\t')
                chrom = value_list[0]
                
                if chrom != past_chrom:
                    past_chrom = chrom
                    past_pos = int(value_list[1])
                    reverse = None
                    add_info = (chrom, )
                    
                elif reverse is None:
                    
                    if past_pos < int(value_list[1]):
                        reverse = False
                        add_info += (reverse, )
                        chromosomes.append(add_info)
                        
                    elif past_pos > int(value_list[1]):
                        reverse = True
                        add_info += (reverse, )
                        chromosomes.append(add_info)
                    
        return chromosomes
    
    
    def get_header(self, file_name):
        
        file = open(file_name, 'r')
        
        for line in file:
            if line.startswith('#') is False:
                break
            elif line.startswith('##') is True:
                pass
            else:
                header = line[1:].rstrip().split('\t')
                
        file.close()
        
        return header

####################
    
"""
    def get_columns(self, value_list, col_classes, header):
        
        column_list = []
        
        for index in range(8):
            ColClass = col_classes[index](value_list[index])
            column_list.append(ColClass)
        
        if len(header) > 8:
            FormatColClass = col_classes[8](value_list[8])
            column_list.append(FormatColClass)
            for index in range(9, len(header)):
                ColClass = col_classes[index](value_list[index], FormatColClass.value)
                ColClass.col_name = header[index]
                column_list.append(ColClass)
        
        return column_list
"""

class IOPolyTable(list):
    
    def __init__(self, seqs):
        
        self.IOseqs = None
        
        self.DNA = ['A', 'T', 'C', 'G']
        other_chrs = ['N', '-']
        unique_chrs = set(''.join(seqs).upper())
        
        if unique_chrs <= set(['1', '0']):
            nsam, s = len(seqs), len(seqs[0])
            self.IOseqs = [[] for l in range(s)]
            for base in range(s):
                for ind in range(nsam):
                    self.IOseqs[base].append(int(seqs[ind][base]))

        elif unique_chrs <= set(self.DNA + other_chrs):
            self.IOseqs = self.DNA_to_IO(seqs)
        else:
            raise TypeError, 'Unusual characters in sequences.'

    def __getitem__(self, index):
        return self.IOseqs[index]

    def __len__(self):
        return len(self.IOseqs)
        
    def DNA_to_IO(self, dna):

        length = len(dna[0])
        samples = len(dna)
        
        IO = []
        for base in range(length):
            base_seqs = ''
            baseIO = []
            for sam in range(samples):
                base_seqs += dna[sam][base]
                
            if len(set(base_seqs)) == 2 and set(base_seqs) <= set(self.DNA):
                minor, major = self.minor_major_allele(base_seqs)
                for i in base_seqs:
                    if i == major:
                        baseIO.append(0)
                    elif i == minor:
                        baseIO.append(1)
                IO.append(baseIO)

        return IO

    def minor_major_allele(self, seq):
        
        useq = list(set(seq))
        counts = [(seq.count(i), i) for i in useq]
        counts.sort()
        minor = counts[0][1]
        major = counts[1][1]
        
        return minor, major

class StatMethods():
    
    def seg_sites(self):
        return len(self.IOtable)
    
    def nsamples(self):
        return len(self.IOtable[0])
    
    def thetaw(self):
        
        s = self.seg_sites()
        n = self.nsamples()
        a1 = sum(1.0 / i for i in range(1, n))
        tw = s / a1

        return tw

class msFormat(StatMethods):
    
    def __init__(self, iteration):
        lines = [i for i in iteration.split('\n')[2:] if i != '']
        self.IOtable =  IOPolyTable(lines)


class FastaFormat(StatMethods):
    """
    Example usage:
    
       >>> from evolib.SequenceFormats import FastaFormat
       
       Example 1:
       >>> fileObject = open('example.fsa', 'r')
       >>> F = FastaFormat(fileObject)
       
       Example 2:
       >>> seq = 'ATCTGATGCTGAC'
       >>> F = FastaFormat(seq)
       
       Example 3:
       >>> id = 'seq1'
       >>> seq = 'ATCGATGTCGTGAC'
       >>> F = FastaFormat(seq, id)
       
       Example 4:
       >>> ids = ['seq1', 'seq2', 'seq3']
       >>> seqs = ['ATCGATGTCGTGAC', 'ATCGATGTCGTGAC', 'ATCGATGTCGTGAC']
       >>> F = FastaFormat(seqs, ids)
    """

    def __init__(self, *args):
        
        if len(args) == 1:
            arg1 = args[0]
            if isinstance(arg1, file):
                self._fromFile(arg1)
            elif isinstance(arg1, str):
                self._fromSequence(None, [arg1])
            elif isinstance(arg1, list):
                self._fromSequence(None, arg1)
            else:
                raise TypeError, 'Wrong arg type. File object or list of sequences.'
        elif len(args) == 2:
            arg1 = args[0]
            arg2 = args[1]
            if isinstance(arg1, str):
                assert isinstance(arg2, str)
                self._fromSequence([arg2], [arg1])
            elif isinstance(arg1, list):
                assert isinstance(arg2, list)
                assert len(arg1) == len(arg2)
                self._fromSequence(arg2, arg1)
            else:
                raise TypeError, 'Wrong arg type. File object or list of sequences.'
            
    def __str__(self):
        n = 70
        the_string = ''
        for s in range(len(self.sequences)):
            seq = self.sequences[s]
            the_string += '>' + self.ids[s] + '\n'
            the_string += '\n'.join([seq[i: i + n] for i in range(0, len(seq), n)]) + '\n'
            
        return the_string.rstrip()

    def _fromFile(self, fileObject):
        """
        Returns a matrix where M[i][j] refers to the jth site of the ith individual.
        """        
        step1 = ''.join(map(lambda line: line, fileObject))
        step2 = step1.split('\n>')
        seq_table = [part.partition('\n')[2].replace('\n','') for part in step2]
        seq_names = [part.partition('\n')[0].replace('>', '') for part in step2]
        
        self.sequences = seq_table
        self.ids = seq_names
        self.IOtable = IOPolyTable(seq_table)

    def _fromSequence(self, ids, seqs):
        
        if ids is None:
            nseqs = len(seqs)
            ids = self._create_ids(nseqs)
        
        self.ids = ids
        self.sequences = seqs

    def _create_ids(self, nseqs):
        """
        Creates a list of sequence ids equal to the number 
        of sequences as shown in the examples below:
           ['seq1', 'seq2', 'seq3']
           ['seq01', 'seq02', ...'seq32']
        """
        ids = []
        for i in range(nseqs):
            seqnum = i + 1
            num_zeros = len(str(nseqs)) - len(str(seqnum))
            zeros = '0' * num_zeros
            id1 = 'seq' + zeros + str(seqnum)
            ids.append(id1)
            
        return ids
