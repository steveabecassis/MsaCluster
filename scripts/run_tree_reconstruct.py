# import itertools
# import os
# from pathlib import Path
from utils.phytree_utils import *
from glob import glob

import torch
import matplotlib as mpl
import argparse
mpl.use("agg")

torch.set_grad_enabled(False)


if __name__=='__main__':

    p = argparse.ArgumentParser(description=
    """
    Run Phylogenetic tree reconstruction from MSA.
    """)

    p.add_argument("--input_msas", nargs='*', action='store',help='Path to msas to use in prediction.')
    p.add_argument("-o", action="store", help='name of output directory to write contact maps to.')
    p.add_argument("-saveformat", action="store", help='output file format (text or pickle).')
    p.add_argument("--method", action='store', default='distance', help="Method: `distance` or ... (default is 'distance')")
    p.add_argument("--parallel", action='store_true', help='Runs in parallel using Pandarallel.')

    args = p.parse_args()
    print("Args:")
    print(args)

    print("args.o:")
    print(args.o)
    os.makedirs(args.o, exist_ok=True)
#    args.test = True
#    if args.test:
#        args.input_msas = args.input_msas[:3]

    print("Is running with GPU? " + str(torch.cuda.is_available()))
    start_time = time.time()

    # New! insert to MSA also the full alignment (calculating cmap can take long for this one)
    msa_file = args.input_msas[0]

    # Remove old cmaps in the same directory!
    print("Removing old files: " + args.o + '/*.nwk')
    print(glob(args.o + '/*.nwk'))
    for f_old in glob(args.o + '/*.nwk'):
        os.remove(f_old)

    if args.method == 'distance':
        phytree = phytree_from_msa(msa_file, output_tree_file=args.o + "/" + os.path.basename(msa_file).replace(".a3m", "_tree.nwk"))

    print(phytree.total_branch_length())
    print("Finished! Runtime for " + str(phytree.name) + " tree reconstruction = " + str(time.time()-start_time) + " seconds")