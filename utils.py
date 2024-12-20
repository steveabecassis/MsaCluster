from Bio.PDB import PDBParser
from Bio.SeqUtils import seq1
import mdtraj as md
import numpy as np
import matplotlib.pyplot as plt
from argparse import  ArgumentParser
from Bio.PDB import PDBParser, PDBIO, Select
from Bio import SeqIO
import mdtraj as md
from contact_map import ContactFrequency, ContactDifference
import numpy as np
import mdtraj as md

pdf_files_path = f'/Users/steveabecassis/Desktop/pdb_file'
pdb_file = f'{pdf_files_path}/1jfk.pdb'

class ChainSelect(Select):
    def __init__(self, chain_letter):
        self.chain_letter = chain_letter

    def accept_chain(self, chain):
        return chain.id == self.chain_letter

def create_chain_pdb_files(fold_1,fold_2,pdb_file_path,chain_pdb_file_path):
    chain_fold_1 = fold_1[-1]
    chain_fold_2 = fold_2[-1]
    # Load the original PDB file
    parser = PDBParser()
    structure_fold1 = parser.get_structure('PDB_structure' , f'{pdb_file_path}/{fold_1[:-1]}.pdb')
    structure_fold2 = parser.get_structure('PDB_structure' , f'{pdb_file_path}/{fold_2[:-1]}.pdb')
    io = PDBIO()
    # Set the structure for saving and use ChainSelect to filter the chain
    io.set_structure(structure_fold1)
    io.save(f'./{chain_pdb_file_path}/{fold_1}.pdb', ChainSelect(chain_fold_1))
    io.set_structure(structure_fold2)
    io.save(f'./{chain_pdb_file_path}/{fold_2}.pdb', ChainSelect(chain_fold_2))


def get_fasta_chain_seq(pdb_file,fold_name,output_dir):
    # Create a PDB parser
    parser = PDBParser()
    # Parse the structure
    structure = parser.get_structure('PDB_structure', pdb_file)
    # Extract the sequence
    for model in structure:
        for chain in model:
                sequence = ""
                for residue in chain:
                    if residue.id[0] == ' ':
                        sequence += seq1(residue.resname)

    with open(f"./{output_dir}/fasta_chain_files/{fold_name}.fasta", "w") as output_handle:
        output_handle.write('>'+'\n'+sequence)

# pdb_file = '/Users/steveabecassis/Desktop/1eboE.pdb'
# with open(f"/Users/steveabecassis/Desktop/test.fasta", "w") as output_handle:
#     output_handle.write('>'+'\n>'+sequence)

def save_org_cmaps(chain_pdb_file_path,fold):
    traj = md.load(filename_or_filenames=f'{chain_pdb_file_path}/{fold}.pdb')
    frame_contacts = ContactFrequency(traj[0])
    np.save(f'./Pipeline/org_cmaps/{fold}.npy',frame_contacts)

