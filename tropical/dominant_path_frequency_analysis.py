import numpy as np
import networkx as nx
from pysb.bng import generate_equations
import re
import pandas as pd
from math import log10
import sympy
from tropical.discretize_path import find_numbers
import tropical.util as hf
from tropical.util import parse_name
from collections import defaultdict, OrderedDict
from anytree import Node, findall
from anytree.exporter import DictExporter
from anytree.importer import DictImporter
from collections import ChainMap
import time

def get_path_descendants(path):
    """ Get the set of descendants for a tree like path dict.
    """

    importer = DictImporter()
    root = importer.import_(path)
    descendants = set([descendant_node.name for descendant_node in root.descendants])
    return descendants


def relative_species_frequency_signatures(paths, path_signatures, model, accessible_species=None):
    """Compute the relative frequencies of species.

    This function computes the relative frequencies of species amongst the
    dominant paths across all simulatations and timepoints.

    Parameters
    ----------
    paths: dict
        Nested tree structure dict of paths as returned from
            DomPath.get_path_signatures()
    path_signatures: pandas.DataFrame
        The dominant path signatures for each simulation (across all
            timepoints).
    model: pysb.Model
        The model that is being used.

    Returns
    -------
        A list of tuples with the species codename
        (i.e. 's' + str( model.species_index)) and the fraction of dominant
        paths that species was in.

    """
    def convert_names(list_o_tuple):
        new_list_o_tuple = []
        for i, item in enumerate(list_o_tuple):
            sname = item[0]
            node_idx = list(find_numbers(sname))[0]
            node_sp = model.species[node_idx]
            node_name = parse_name(node_sp)
            new_list_o_tuple.append((node_name, item[1]))

        return new_list_o_tuple
    generate_equations(model)
    if accessible_species is None:
        species_all = model.species
        #print(species_all)
        n_species_all = len(species_all)
        spec_dict = dict()
        spec_counts = np.array([0.0] * n_species_all)
        #species_all_snames = []
        for i, species in enumerate(species_all):
            sname = "s{}".format(i)
            spec_dict[sname] = {'name': species, 'index': i}
    else:
        species_all = model.species
        #print(species_all)
        n_species_all = len(accessible_species)
        spec_dict = dict()
        spec_counts = np.array([0.0] * n_species_all)
        #species_all_snames = []
        for i, species in enumerate(accessible_species):
            spec_dict[species] = {'name': species, 'index': i}

    path_species = dict()
    for i, key in enumerate(paths.keys()):
        path = paths[key]
        descendants = get_path_descendants(path)
        #add the root node to the set of species for the path
        descendants.add(path['name'])
        #print(descendants)
        path_species[i] = descendants
    path_signatures_np = path_signatures.values
    n_sims = path_signatures_np.shape[0]
    n_tp = path_signatures_np.shape[1]
    #print(n_sims, n_tp)
    #quit()
    n_tot = 0.0
    for i in range(n_sims):
        for j in range(n_tp):
            n_tot += 1.0
            dom_path_id = path_signatures_np[i][j]
            #print(dom_path_id)
            for descendant in path_species[dom_path_id]:
            #    print(descendant)
                d_id = spec_dict[descendant]['index']
                spec_counts[d_id] += 1.0
    #print(n_tot)
    spec_fracs = spec_counts / n_tot
    #quit()
    spec_frac_dict = dict()
    for spec in spec_dict.keys():
        spec_frac_dict[spec] = spec_fracs[spec_dict[spec]['index']]
    sorted_by_value = sorted(spec_frac_dict.items(), key=lambda kv: -kv[1])

    return convert_names(sorted_by_value)


def relative_species_frequency_paths(paths, model, accessible_species=None):
    """Compute the relative fequencies of species.

    Computes the relative fequencies of species in the dominant paths.

    Parameters
    ----------
    paths: dict
        Nested tree structure dict of paths as returned from
            DomPath.get_path_signatures()
    model: pysb.Model
        The model that is being used.

    Returns
    -------
    A list of tuples with the species codename
        (i.e. 's' + str( model.species_index)) and the fraction of dominant
        paths that species was in.

    """
    def convert_names(list_o_tuple):
        new_list_o_tuple = []
        for i, item in enumerate(list_o_tuple):
            sname = item[0]
            node_idx = list(find_numbers(sname))[0]
            node_sp = model.species[node_idx]
            node_name = parse_name(node_sp)
            new_list_o_tuple.append((node_name, item[1]))

        return new_list_o_tuple
    generate_equations(model)
    if accessible_species is None:
        species_all = model.species
        #print(species_all)
        n_species_all = len(species_all)
        spec_dict = dict()
        spec_counts = np.array([0.0] * n_species_all)
        #species_all_snames = []
        for i, species in enumerate(species_all):
            sname = "s{}".format(i)
            spec_dict[sname] = {'name': species, 'index': i}
    else:
        species_all = model.species
        #print(species_all)
        n_species_all = len(accessible_species)
        spec_dict = dict()
        spec_counts = np.array([0.0] * n_species_all)
        #species_all_snames = []
        for i, species in enumerate(accessible_species):
            spec_dict[species] = {'name': species, 'index': i}

    path_species = dict()
    for i, key in enumerate(paths.keys()):
        path = paths[key]
        descendants = get_path_descendants(path)
        #add the root node to the set of species for the path
        descendants.add(path['name'])
        #print(descendants)
        path_species[i] = descendants

    #print(n_sims, n_tp)
    #quit()
    n_tot = 0.0
    for i, key in enumerate(path_species.keys()):
        n_tot += 1.0
        for descendant in path_species[key]:
        #    print(descendant)
            d_id = spec_dict[descendant]['index']
            spec_counts[d_id] += 1.0
    #print(n_tot)
    spec_fracs = spec_counts / n_tot
    #quit()
    spec_frac_dict = dict()
    for spec in spec_dict.keys():
        spec_frac_dict[spec] = spec_fracs[spec_dict[spec]['index']]
    sorted_by_value = sorted(spec_frac_dict.items(), key=lambda kv: -kv[1])

    return convert_names(sorted_by_value)
