# Run design to both A and B, then fold both of them with alpha-fold. See if we get something closer
def compare_designs(S, pdbID1, pdbID2):
    S1 = design_every_position(S, pdbID1)
    S2 = design_every_position(S, pdbID2)

    # Compare sequences:
    print("\nS: ", S, "\nS1: ", S1, "\nS2: ", S2)

    AF = Alphafold(S)  # Fold the natural sequence
    AF1 = Alphafold(S1)  # Fold the first one
    AF2 = Alphafold(S2)  # Fold the second one

    TM = ['TM1', 'TM2']
    SEQ = ['S', 'S1', 'S2']
    df_tm = pd.DataFrame(columns=TM, index=SEQ)
    S_true_list = [pdbID1, pdbID2]
    S_pred_list = [AF, AF1, AF2]
    for i_true in range(2):  # loop on the two true structures
        for j_pred in range(3):  # S_predicted in [AF, AF1, AF2]:  # loop on the three predicted structures
            #            df_tm[TM[i_true]][SEQ[j_pred]] = TMScore(S_true_list[i_true], S_pred_list[j_pred])  # Compute TMScore similarity
            alignment = tmscoring.TMscoring(S_true_list[i_true], S_pred_list[j_pred])  # 'structure1.pdb', 'structure2.pdb')  # from installed tmscoring
            df_tm[TM[i_true]][SEQ[j_pred]] = alignment.tmscore(**alignment.get_current_values())

    print(df_tm)
    return df_tm, S, S1, S2, AF, AF1, AF2  # Return all sequences, structures and their similarity


def dihedral_wrapper(traj):
    """Featurize an MD trajectory into a vector space via calculation
    of dihedral (torsion) angles of alpha carbon backbone

    Lifted from MSMBuilder, RT McGibbon

    Parameters
    ----------
    traj : mdtraj.Trajectory
        A molecular dynamics trajectory to featurize.

    Returns
    -------
    features : np.ndarray, dtype=float, shape=(n_samples, n_features)
        A featurized trajectory is a 2D array of shape
        `(length_of_trajectory x n_features)` where each `features[i]`
        vector is computed by applying the featurization function
        to the `i`th snapshot of the input trajectory.

    """
    ca = [a.index for a in traj.top.atoms if a.name == 'CA']
    if len(ca) < 4:
        return np.zeros((len(traj), 0), dtype=np.float32)

    alpha_indices = np.array(
        [(ca[i - 1], ca[i], ca[i + 1], ca[i + 2]) for i in range(1, len(ca) - 2)])
    result = md.compute_dihedrals(traj, alpha_indices)

    return result[0]


def download_read_pdb(pdbcode, datadir, keepfile=True):
    """
    Downloads a PDB file from the Internet and saves it in a data directory.
    Then it reads and returns the structure inside.
    :param pdbcode: The standard PDB ID e.g. '3ICB'
    :param datadir: The directory where the downloaded file will be saved
    :param keepfile: if False, then the downloaded file will be deleted (default: keep the downloaded file)
    :return: a Bio.PDB Structure object or None if something went wrong
    """
    pdbfilenm = download_pdb(pdbcode, datadir)
    if pdbfilenm is None:
        return None
    struct = read_pdb(pdbcode, pdbfilenm)
    if not keepfile:
        os.remove(pdbfilenm)
    return struct


def download_pdb(pdb_id):
    url = f"https://files.rcsb.org/download/{pdb_id}.pdb"
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        filename = f"./pdb_files/{pdb_id}.pdb"
        with open(filename, 'w') as file:
            file.write(response.text)
        print(f"Downloaded {filename}")
    else:
        print(f"Failed to download PDB file for ID {pdb_id}. Status code: {response.status_code}")


# Functions below are from András Aszódi:
# https://stackoverflow.com/questions/10324674/parsing-a-pdb-file-in-python
def download_pdb(pdbcode, datadir, downloadurl="http://files.rcsb.org/download/"):
    """
    Downloads a PDB file from the Internet and saves it in a data directory.
    :param pdbcode: The standard PDB ID e.g. '3ICB' or '3icb'
    :param datadir: The directory where the downloaded file will be saved
    :param downloadurl: The base PDB download URL, cf.
        `https://www.rcsb.org/pages/download/http#structures` for details
        Note that the unencrypted HTTP protocol is used by default
        to avoid spurious OpenSSL errors...
    :return: the full path to the downloaded PDB file or None if something went wrong
    """
    pdbfn = pdbcode + ".pdb"
    url = downloadurl + pdbfn
    outfnm = os.path.join(datadir, pdbfn)
    try:
        urllib.request.urlretrieve(url, outfnm)
        return outfnm
    except Exception as err:
        # all sorts of things could have gone wrong...
        print(str(err), file=sys.stderr)
        return None



def get_calphas(struct):
    """
    Extracts the C-alpha atoms from a PDB structure.
    :param struct: A Bio.PDB.Structure object.
    :return: A list of Bio.PDB.Atom objects representing the C-alpha atoms in `struct`.
    """
    calphas = [atom for atom in struct.get_atoms() if atom.get_fullname() == " CA "]
    return calphas

# Read fasta file
def get_sequence_from_fasta(fasta_file_path):
    sequence = None
    for record in SeqIO.parse(fasta_file_path, "fasta"):
        sequence = str(record.seq)
        break
    return sequence


# Taken from here:
# https://stackoverflow.com/questions/76682974/similarity-score-sequence-alignment
def lev_distance_matrix(seqs):
    """Calculate Levenshtein distance and ratio metrics
       on input pair of strings.
    """
    seqs = sorted(seqs)

    return {
        seqs[0]: {
            seqs[1]: {
                "distance": pylev.distance(*seqs),
                "ratio": pylev.ratio(*seqs),
            }
        }
    }


class PlotTool:

    def plot_single_fold(self,pdb,label=''):
        viewer = py3Dmol.view(width=400, height=300)
        viewer.addModel(pdb, 'pdb')
        viewer.setStyle({'model': 0}, {'stick': {}})
        viewer.setStyle({'model': 0}, {'cartoon': {'color': 'blue'}})
        viewer.addLabel(label, {'fontOpacity': 0.3}, {'resi': 158})
        viewer.zoomTo()
        viewer.zoom(1.2)
        viewer.setBackgroundColor('white')
        viewer.show()

    def plot_fold_alignement(self):
        # Select CA atoms for alignment
        ca_atoms1 = self.structure1.select('name CA')
        ca_atoms2 = self.structure2.select('name CA')

        common_residues = set(ca_atoms1.getResnums()).intersection(ca_atoms2.getResnums())
        matched_ca1 = ca_atoms1.select('resnum ' + ' '.join(map(str, common_residues)))
        matched_ca2 = ca_atoms2.select('resnum ' + ' '.join(map(str, common_residues)))

        transformation = pr.calcTransformation(matched_ca2, matched_ca1)
        structure2_aligned = transformation.apply(self.structure2)

        # Write the aligned structure2 to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdb') as temp_file:
            pr.writePDB(temp_file.name, structure2_aligned)
            aligned_pdb2_path = temp_file.name
        # Read the aligned PDB files
        pdb1 = self.read_pdb_file(f'{self.folder}/{self.fold_pair}/chain_pdb_files/{self.fold1}.pdb')
        pdb2 = self.read_pdb_file(aligned_pdb2_path)
        # Create a py3Dmol viewer
        viewer = py3Dmol.view(width=800, height=600)
        # Add the first structure with cartoon style
        viewer.addModel(pdb1, 'pdb')
        viewer.setStyle({'model': 0}, {'cartoon': {'color': 'blue'}})
        # Add the aligned second structure with cartoon style
        viewer.addModel(pdb2, 'pdb')
        viewer.setStyle({'model': 1}, {'cartoon': {'color': 'red'}})

        # Align the second model to the first
        viewer.zoomTo()
        viewer.zoom(1.2)
        viewer.setBackgroundColor('white')
        viewer.show()
        os.remove(aligned_pdb2_path)


    # Why another function with almost the same name???
    def plot_fold_alignement_(self,path_pdb1,path_pdb2):
        # Select CA atoms for alignment
        structure1 = pr.parsePDB(path_pdb1)
        structure2 = pr.parsePDB(path_pdb2)
        ca_atoms1 = structure1.select('name CA')
        ca_atoms2 = structure2.select('name CA')

        common_residues = set(ca_atoms1.getResnums()).intersection(ca_atoms2.getResnums())
        matched_ca1 = ca_atoms1.select('resnum ' + ' '.join(map(str, common_residues)))
        matched_ca2 = ca_atoms2.select('resnum ' + ' '.join(map(str, common_residues)))

        transformation = pr.calcTransformation(matched_ca2, matched_ca1)
        structure2_aligned = transformation.apply(self.structure2)

        pref = path_pdb2.split('/')[-1][:-4] + '_TEMP'
        print(pref)
        # Write the aligned structure2 to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdb',prefix= pref) as temp_file:
            pr.writePDB(temp_file.name, structure2_aligned)
            aligned_pdb2_path = temp_file.name
        # Read the aligned PDB files
        pdb1 = self.read_pdb_file(path_pdb1)
        pdb2 = self.read_pdb_file(aligned_pdb2_path)
        # Create a py3Dmol viewer
        viewer = py3Dmol.view(width=800, height=600)
        # Add the first structure with cartoon style
        viewer.addModel(pdb1, 'pdb')
        # viewer.addLabel(f"{path_pdb1.split('/')[-1][:-4]}", {'fontOpacity': 0.3}, {'resi': 158})
        print(f"Blue:{path_pdb1.split('/')[-1][:-4]}")
        viewer.setStyle({'model': 0}, {'cartoon': {'color': 'blue'}})
        # Add the aligned second structure with cartoon style
        viewer.addModel(pdb2, 'pdb')
        print(f"Red:{path_pdb2.split('/')[-1][:-4]}")
        # viewer.addLabel(f"{path_pdb2.split('/')[-1][:-4]}", {'fontOpacity': 0.3}, {'resi': 158})
        viewer.setStyle({'model': 1}, {'cartoon': {'color': 'red'}})

        # Align the second model to the first
        viewer.zoomTo()
        viewer.zoom(1.2)
        viewer.setBackgroundColor('white')
        viewer.show()



    def plot_fold_alignment_1(self, path_pdb1, path_pdb2):
            try:
                # Select CA atoms for alignment
                structure1 = pr.parsePDB(path_pdb1)
                structure2 = pr.parsePDB(path_pdb2)
                ca_atoms1 = structure1.select('name CA')
                ca_atoms2 = structure2.select('name CA')

                # Ensure CA atoms are found
                if ca_atoms1 is None or ca_atoms2 is None:
                    raise ValueError("CA atoms not found in one or both structures")

                # Get common residues
                common_residues = set(ca_atoms1.getResnums()).intersection(ca_atoms2.getResnums())
                if not common_residues:
                    raise ValueError("No common residues found for alignment")

                matched_ca1 = ca_atoms1.select('resnum ' + ' '.join(map(str, common_residues)))
                matched_ca2 = ca_atoms2.select('resnum ' + ' '.join(map(str, common_residues)))

                # Ensure matched CA atoms are found
                if matched_ca1 is None or matched_ca2 is None:
                    raise ValueError("Matched CA atoms not found in one or both structures")

                # Calculate transformation and apply to structure2
                transformation = pr.calcTransformation(matched_ca2, matched_ca1)
                structure2_aligned = transformation.apply(structure2)

                pref = path_pdb2.split('/')[-1][:-4] + '_TEMP'
                print(pref)
                # Write the aligned structure2 to a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdb', prefix=pref) as temp_file:
                    pr.writePDB(temp_file.name, structure2_aligned)
                    aligned_pdb2_path = temp_file.name

                # Read the aligned PDB files
                pdb1 = self.read_pdb_file(path_pdb1)
                pdb2 = self.read_pdb_file(aligned_pdb2_path)

                # Create a py3Dmol viewer
                viewer = py3Dmol.view(width=800, height=600)

                # Add the first structure with cartoon style
                viewer.addModel(pdb1, 'pdb')
                print(f"Blue: {path_pdb1.split('/')[-1][:-4]}")
                viewer.setStyle({'model': 0}, {'cartoon': {'color': 'blue'}})

                # Add the aligned second structure with cartoon style
                viewer.addModel(pdb2, 'pdb')
                print(f"Red: {path_pdb2.split('/')[-1][:-4]}")
                viewer.setStyle({'model': 1}, {'cartoon': {'color': 'red'}})

                # Align the second model to the first
                viewer.zoomTo()
                viewer.zoom(1.2)
                viewer.setBackgroundColor('white')
                viewer.show()

                # Delete the temporary file
                os.remove(aligned_pdb2_path)
            except Exception as e:
                print(f"An error occurred: {e}")


def plot_viz_cmap(file,legend_plot):
    # Create a sample 2D numpy array (replace this with your actual data)
    visualization_map = np.load(file)
    size = 50

    # Create a custom colormap
    colors = ['grey','blue','lightblue','purple','blue','magenta']
    # values = [0, 1, 1.25, 1.5, 1.75]
    bounds = [0,0.49,0.99, 1.24, 1.49, 1.74,2]
    cmap = ListedColormap(colors)
    norm = BoundaryNorm(bounds, cmap.N)

    # Create the plot
    plt.figure(figsize=(10,8))
    im = plt.imshow(visualization_map, cmap=cmap, norm=norm, interpolation='nearest',origin='lower')

    # Create legend elements
    legend_elements = [
        Patch(facecolor='lightblue', edgecolor='black', label='Experiment contact'),
        Patch(facecolor='purple', edgecolor='black', label='Unique State Experiment contact'),
        Patch(facecolor='blue', edgecolor='black', label='Experiment contact predicted'),
        Patch(facecolor='magenta', edgecolor='black', label='Unique State Experiment contact predicted')
    ]

    # Add the legend
    plt.legend(handles=legend_elements, loc='center left', bbox_to_anchor=(1, 0.5))

    # Set title and labels
    plt.title(legend_plot)
    plt.xlabel('Residue Index')
    plt.ylabel('Residue Index')

    # Adjust layout to make room for the legend
    plt.tight_layout()

    # Show the plot
    plt.show()


def toggle_visibility(change):
    if change['name'] == 'value':
        if change['owner'] == toggle1:
            view.setStyle({'model': 0},
                          {'cartoon': {'color': 'red'}} if change['new'] else {'cartoon': {'hidden': True}})
        elif change['owner'] == toggle2:
            view.setStyle({'model': 1},
                          {'cartoon': {'color': 'blue'}} if change['new'] else {'cartoon': {'hidden': True}})
    view.render()



def read_sequence(filename: str) -> Tuple[str, str]:
    """ Reads the first (reference) sequences from a fasta or MSA file."""
    record = next(SeqIO.parse(filename, "fasta"))
    return record.description, str(record.seq)


# Plot structure using nglview
def plot_pdb_struct(pdb_file, output_3d_image_file = []):
#    view = nv.show_file(pdb_file)
#    view

    with open(pdb_file, "r") as f:
        pdb_data = f.read()

    # Create a 3Dmol view
    viewer = py3Dmol.view(width=400, height=400)

    # Add the protein structure data to the viewer
    viewer.addModel(pdb_data, "pdb")

    # Style the visualization (optional)
    viewer.setStyle({"cartoon": {"color": "spectrum"}})

    # Zoom to fit the structure
    viewer.zoomTo()

    output_file = f"protein_structure.png"
    with open(output_file, "wb") as f:
        f.write(viewer.toImage("png"))
    print(f"Saved {output_file}")

#    display(viewer)
#    output_file = "protein_structure.png"  # Replace with your desired output file name

#    with Display():
#        viewer.savefig(output_file)

    # Show the 3D visualization
#    viewer.show()

    if len(output_3d_image_file) == 0:
        output_3d_image_file = "Pipeline/Results/Figures/3d_struct/" + os.path.basename(pdb_file) + ".png"


#    screenshot = viewer.png()
#    with open(output_3d_image_file, 'wb') as f:
#        f.write(screenshot)

#    viewer.png(output_3d_image_file) # , width=400, height=400)

    return 0


# Function to assign colors to tree nodes (should be depending on values!)
def set_node_color(node):
    if node.is_terminal():
        color = value_to_color.get(node.name, (0.5, 0.5, 0.5))  # Default to gray
    else:
        # You can set a color for internal nodes here if needed
        color = (0.5, 0.5, 0.5)  # Default to gray
    node.color = color


def visualize_alignement_structure(PATH_PDB1, PATH_PDB2):
    # Set up PDB parser
    parser = PDB.PDBParser()

    # Load structures
    structure1 = parser.get_structure("protein1", PATH_PDB1)
    structure2 = parser.get_structure("protein2", PATH_PDB2)

    # Get aligned atoms
    aligned_atoms1, aligned_atoms2 = get_aligned_atoms(structure1, structure2)

    # Align structures
    super_imposer = Superimposer()
    super_imposer.set_atoms(aligned_atoms1, aligned_atoms2)
    super_imposer.apply(structure2.get_atoms())

    # Save aligned structure
    io = PDB.PDBIO()
    io.set_structure(structure2)
    io.save("aligned_protein2.pdb")

    # Create py3Dmol view
    view = py3Dmol.view(width=800, height=600)

    # Add structures to the view
    with open(pdb_file2_, 'r') as f:
        view.addModel(f.read(), 'pdb')
    with open("aligned_protein2.pdb", 'r') as f:
        view.addModel(f.read(), 'pdb')

    # Set styles
    view.setStyle({'model': 0}, {'cartoon': {'color': 'red'}})
    view.setStyle({'model': 1}, {'cartoon': {'color': 'blue'}})

    # Zoom to fit
    view.zoomTo()

    # Create toggle buttons
    toggle1 = widgets.ToggleButton(description='Toggle Protein 1', value=True)
    toggle2 = widgets.ToggleButton(description='Toggle Protein 2', value=True)

    toggle1.observe(toggle_visibility)
    toggle2.observe(toggle_visibility)

    # Display the view and toggle buttons
    display(HTML(view._make_html()))
    display(widgets.HBox([toggle1, toggle2]))


def visualize_structure_alignment(pdb_file1, pdb_file2, chain1='A', chain2='A'):
    # Parse PDB files
    parser = PDBParser(QUIET=True)
    structure1 = parser.get_structure("protein1", pdb_file1)
    structure2 = parser.get_structure("protein2", pdb_file2)

    # Extract sequences
    seq1 = "".join([three_to_one(res.resname) for res in structure1[0][chain1] if res.id[0] == ' '])
    seq2 = "".join([three_to_one(res.resname) for res in structure2[0][chain2] if res.id[0] == ' '])

    # Perform sequence alignment
    aligner = Align.PairwiseAligner()
    alignments = aligner.align(seq1, seq2)
    best_alignment = next(alignments)

    # Get aligned positions
    aligned_positions = [(i, j) for i, j in zip(best_alignment.path[0], best_alignment.path[1])
                         if i != -1 and j != -1]

    # Extract aligned CA atoms
    ca_atoms1 = [atom for atom in structure1[0][chain1].get_atoms() if atom.name == 'CA']
    ca_atoms2 = [atom for atom in structure2[0][chain2].get_atoms() if atom.name == 'CA']

    aligned_atoms1 = [ca_atoms1[i] for i, _ in aligned_positions]
    aligned_atoms2 = [ca_atoms2[j] for _, j in aligned_positions]

    # Superimpose structures
    super_imposer = PDB.Superimposer()
    super_imposer.set_atoms(aligned_atoms1, aligned_atoms2)
    super_imposer.apply(structure2.get_atoms())

    # Function to get PDB string
    def get_pdb_string(structure):
        io = StringIO()
        pdb_io = PDBIO()
        pdb_io.set_structure(structure)
        pdb_io.save(io)
        return io.getvalue()

    # Create a py3Dmol view
    view = py3Dmol.view(width=800, height=600)

    # Add the first structure
    view.addModel(get_pdb_string(structure1), 'pdb')
    view.setStyle({'model': -1}, {'cartoon': {'color': 'blue'}})

    # Add the second (aligned) structure
    view.addModel(get_pdb_string(structure2), 'pdb')
    view.setStyle({'model': -1}, {'cartoon': {'color': 'red'}})

    # Zoom to fit the structures
    view.zoomTo()

    # Calculate RMSD
    rmsd = super_imposer.rms

    # Add RMSD and alignment info as labels
    view.addLabel(f"RMSD: {rmsd:.2f} Å",
                  {'position': {'x': -20, 'y': -20}, 'backgroundColor': 'white', 'fontColor': 'black'})
    view.addLabel(f"Aligned: {len(aligned_positions)} of {len(seq1)} (blue) and {len(seq2)} (red) residues",
                  {'position': {'x': -20, 'y': -40}, 'backgroundColor': 'white', 'fontColor': 'black'})

    return view
