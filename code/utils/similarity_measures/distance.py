import numpy as np
import pandas as pd
import collections as co

from multiprocessing import Pool
import timeit as ti
import time

from .py.edit_distance import edit_distance as p_ed
from .cy.edit_distance import edit_distance as c_ed

from .py.edit_distance_penalty import edit_distance_penalty as p_edp

from .py.dtw import dtw as p_dtw

def py_edit_distance(hashes: dict[str, list[list[str]]]) -> pd.DataFrame:
    """
    Method for computing Edit distance similarity between hashes generated by the grid and disk LSH using python.

    Params 
    ---
    hashes : dict[str, list[list[str]]]
        A dictionary containing the trajectory hashes

    Returns
    ---
    A NxN pandas dataframe containing the pairwise similarities
    """

    sorted_hashes = co.OrderedDict(sorted(hashes.items()))
    num_hashes = len(sorted_hashes)

    M = np.zeros((num_hashes, num_hashes))
    for i, hash_i in enumerate(sorted_hashes.keys()):
        for j, hash_j in enumerate(sorted_hashes.keys()):
            X = np.array(sorted_hashes[hash_i], dtype=object)
            Y = np.array(sorted_hashes[hash_j], dtype=object)
            e_dist = p_ed(X, Y)[0]
            M[i,j] = e_dist
            if i == j:
                break

    df = pd.DataFrame(M, index=sorted_hashes.keys(), columns=sorted_hashes.keys())

    return df


def py_edit_distance_penalty(hashes: dict[str, list[list[str]]]) -> pd.DataFrame:
    """ Test method Edit distance penalty"""
    sorted_hashes = co.OrderedDict(sorted(hashes.items()))
    num_hashes = len(sorted_hashes)

    M = np.zeros((num_hashes, num_hashes))
    for i, hash_i in enumerate(sorted_hashes.keys()):
        for j, hash_j in enumerate(sorted_hashes.keys()):
            X = np.array(sorted_hashes[hash_i], dtype=object)
            Y = np.array(sorted_hashes[hash_j], dtype=object)
            e_dist = p_edp(X, Y)[0]
            M[i,j] = e_dist
            if i == j:
                break

    df = pd.DataFrame(M, index=sorted_hashes.keys(), columns=sorted_hashes.keys())

    return df


def _fun_wrapper_edpp(args):
        x,y,j = args
        e_dist = p_edp(x,y)[0]
        return e_dist, j

def py_edit_distance_penalty_parallell(hashes: dict[str, list[list[str]]]) -> pd.DataFrame:
    """Edit distance penalty for hashes computed in parallell"""
 
    sorted_hashes = co.OrderedDict(sorted(hashes.items()))
    num_hashes = len(sorted_hashes)

    M = np.zeros((num_hashes, num_hashes))
    pool = Pool(12)

    for i, hash_i in enumerate(sorted_hashes.keys()):
        elements = pool.map(_fun_wrapper_edpp, [(np.array(sorted_hashes[hash_i], dtype=object), np.array(sorted_hashes[traj_j], dtype=object), j) for j, traj_j in enumerate(sorted_hashes.keys()) if i>=j])

        for element in elements:
            M[i, element[1]] = element[0]

    df = pd.DataFrame(M, index=sorted_hashes.keys(), columns=sorted_hashes.keys())

    return df 


def py_dtw(hashes: dict[str, list[list[float]]]) -> pd.DataFrame:
    """ Coordinate dtw as hashes"""
    sorted_hashes = co.OrderedDict(sorted(hashes.items()))
    num_hashes = len(sorted_hashes)

    M = np.zeros((num_hashes, num_hashes))
    for i, hash_i in enumerate(sorted_hashes.keys()):
        for j, hash_j in enumerate(sorted_hashes.keys()):
            X = np.array(sorted_hashes[hash_i], dtype=object)
            Y = np.array(sorted_hashes[hash_j], dtype=object)
            e_dist = p_dtw(X, Y)
            M[i,j] = e_dist
            if i == j:
                break

    df = pd.DataFrame(M, index=sorted_hashes.keys(), columns=sorted_hashes.keys())

    return df


def _fun_wrapper_dtw(args):
        x,y,j = args
        e_dist = p_dtw(x,y)
        return e_dist, j

def py_dtw_parallell(hashes: dict[str, list[list[str]]]) -> pd.DataFrame:
    """Edit distance penalty for hashes computed in parallell"""
 
    sorted_hashes = co.OrderedDict(sorted(hashes.items()))
    num_hashes = len(sorted_hashes)

    M = np.zeros((num_hashes, num_hashes))
    pool = Pool(12)

    for i, hash_i in enumerate(sorted_hashes.keys()):
        elements = pool.map(_fun_wrapper_dtw, [(np.array(sorted_hashes[hash_i], dtype=object), np.array(sorted_hashes[traj_j], dtype=object), j) for j, traj_j in enumerate(sorted_hashes.keys()) if i>=j])

        for element in elements:
            M[i, element[1]] = element[0]

    df = pd.DataFrame(M, index=sorted_hashes.keys(), columns=sorted_hashes.keys())

    return df 



def cy_edit_distance(hashes: dict[str, list[list[str]]]) -> pd.DataFrame:
    sorted_hashes = co.OrderedDict(sorted(hashes.items()))
    num_hashes = len(sorted_hashes)

    M = np.zeros((num_hashes, num_hashes))
    for i, hash_i in enumerate(sorted_hashes.keys()):
        for j, hash_j in enumerate(sorted_hashes.keys()):
            X = np.array(sorted_hashes[hash_i], dtype=object)
            Y = np.array(sorted_hashes[hash_j], dtype=object)
            e_dist = c_ed(X, Y)[0]
            M[i,j] = e_dist
            if i == j:
                break

    df = pd.DataFrame(M, index=sorted_hashes.keys(), columns=sorted_hashes.keys())

    return df


def measure_py_ed(args):
    """ 
    Method for measuring time efficiency using py_ed 
    
    Params
    ---
    args : (hashes: dict[str, list[list[str]]], number: int, repeat : int) list
    """
    hashes, number, repeat = args

    measures = ti.repeat(lambda: py_edit_distance(hashes), number=number, repeat=repeat, timer=time.process_time)

    return measures

if __name__=="__main__":
    d = {"a" : [["a","b","c","d"], ["a","b","c"]], 
        "b" : [["a", "c", "d"], ["a", "b", "d"]]    }
    print(py_edit_distance(d))
    print(cy_edit_distance(d))
    t = ti.repeat(lambda: py_edit_distance(d),repeat=3,number=10000)
    t1 = ti.repeat(lambda: cy_edit_distance(d),repeat=3,number=10000)
    print(t)
    print(t1)


