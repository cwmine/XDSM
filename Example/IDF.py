#!/usr/bin/env python2
#-*- coding:utf-8 -*-
# speicify XDSM code path
import sys
sys.path.append('../XDSM')

from XDSM import XDSM


def make_IDF_XDSM():

    dsm = XDSM()
    ad = lambda *args, **kargs: dsm.addComp(*args, **kargs)
    co = lambda *args, **kargs: dsm.addDep(*args, **kargs)

    # add diagnol (Component) in order from up to down

    ad('EMPTY', 'Analysis', '')
    #all 'EMPTY' heading name component is used for Input and output,
    # the component will not be shown,
    # here used for upper input and left output
    ad('opt', 'Optimization', r'$0,3\to 1$:\\Optimization')
    ad('ana', 'Analysis, stack', r'$1$\\Analysis $i$')
    ad('fun', 'Function', r'$2$\\Functions')

    #add dependency variables, here order free
    co('opt', 'EMPTY', 'DataInter',
       r'$\mathbf{x}^{(0)}, \hat{\mathbf{y}}^{(0)}$')
    co('EMPTY', 'opt', 'DataInter',
       r'$x^*$')
    co('ana', 'opt', 'DataInter',
       r'$1:\mathbf{x}_0, \mathbf{x}_i, \hat{\mathbf{y}}_{j\neq i}$')
    co('EMPTY', 'ana', 'DataInter,stack',
       r'$\mathbf{y}_i^*$')
    co('fun', 'opt', 'DataInter',
       r'$2:\mathbf{x}, \hat{\mathbf{y}}$')
    co('fun', 'ana', 'DataInter, stack',
       r'$2:\mathbf{y}_i$')
    co('opt', 'fun', 'DataInter',
       '$3:f_0,\mathbf{c}, \mathbf{c}^c$')

    # component name from start to the end in turn
    dsm.addChain([
        'opt-EMPTY', 'opt', 'ana', 'fun', 'opt', 'EMPTY-opt'])
    #the dependency node using "downstream_component-upstream_component"

    # output tex file and compile it
    dsm.write(r'IDF.pdf', compilepdf=True)

if __name__ == '__main__':
    make_IDF_XDSM()



