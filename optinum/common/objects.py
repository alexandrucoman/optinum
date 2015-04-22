"""
Objects which have the ability to storage information.
"""
import random

import numpy


class Space(object):

    def __init__(self, start, stop, precision=2):
        size = (stop - start) * 10 ** precision
        self._start = start
        self._stop = stop
        self._precision = precision
        self._size = int(numpy.log2(size)) + 1

    @property
    def start(self):
        return self._start

    @property
    def stop(self):
        return self._stop

    @property
    def precision(self):
        return self._precision

    @property
    def size(self):
        return self._size


class Gene(object):

    def __init__(self, locus, allele, search_space):
        self._locus = locus
        self._allele = allele
        self._size = len(allele)
        self._space = search_space

    @property
    def locus(self):
        return self._locus

    @property
    def allele(self):
        return self._allele

    @property
    def size(self):
        return self._size

    def value(self):
        decimal = int(''.join(str(allel) for allel in self.allele), 2)
        return (numpy.float64(decimal) / pow(10, self._space.precision) +
                self._space.start)


class Chromosome(object):

    def __init__(self, gene_number, search_space):
        self._gene_number = gene_number
        self._gene_size = search_space.size
        self._space = search_space
        self._info = []

    @property
    def gene_number(self):
        return self._gene_number

    @property
    def gene_size(self):
        return self._gene_size

    def get_genes(self):
        genes = []
        for locus in range(0, self._gene_number, self._gene_size):
            allele = self._info[locus: locus + self._gene_size]
            genes.append(Gene(locus, allele, self._space))
        return genes

    def get_raw_data(self):
        return list(self._info)

    def overwrite(self, genes):
        if len(genes) != self._gene_number:
            raise ValueError("Invalid gene number for this chromosome.")
        self._info = genes

    @classmethod
    def from_raw(cls, genes, search_space):
        chromosome = cls(len(genes), search_space)
        chromosome.overwrite(genes)
        return chromosome

    @classmethod
    def random(cls, gene_number, search_space):
        template = "{0:0%(size)db}" % {"size": search_space.size}
        genetic_data = []
        for _ in range(gene_number):
            genes = random.randrange(0, 2 ** search_space.size)
            genetic_data.extend(list(template.format(genes)))

        return cls.from_raw(genetic_data, search_space)
