import io

import pandas as pd
import parmed as pmd

from dash import html
try:
    from dash_bio.utils import PdbParser, create_mol3d_style
except ImportError:
    from dash_bio_utils import PdbParser, create_mol3d_style
try:
    from dash_bio.utils.mol3dviewer_styles_creator import ATOM_COLORS
except ImportError:
    ATOM_COLORS = None

def make_dash_table(header, cells):
    """ Return a dash defintion of an HTML table from column-formatted data.
        header contains one string per column, and
        cells contains one list per column.
    """

    hdr = html.Tr([ html.Th(h) for h in header ])
    body = [ html.Tr(
                      [ html.Td(c[i]) for c in cells ]
             ) for i in range(len(cells[0]))
           ]

    return [html.Thead(hdr), html.Tbody(body)]

# example link:
# html.A(href=row["PAGE"], children="Datasheet", target="_blank")

class PDBStringParser(PdbParser):
    def __init__(self, s : str):
        # prevent confusion of parmed's PDBFile parser
        # by truncating each line to xyz-only
        s = '\n'.join([l[:54] for l in s.split('\n') \
                              if l[:6] in ['ATOM  ', 'HETATM']])

        self.structure = pmd.formats.PDBFile.parse(io.StringIO(s))
        self.atoms = self.structure.atoms
        self.bonds = self.structure.bonds

def style_protein(atoms):
    styles = []
    for a in atoms:
        styles.append({
            'visualization_type': 'cartoon',
            # stick, cartoon, sphere
            #'color': '#ABABAB' # metallic gray
            'color': '#64D052' # forest green
        })
    return styles

def style_ligand(atoms, c_color=None):
    styles = []
    for a in atoms:
        if ATOM_COLORS is not None:
            color = ATOM_COLORS.get(a['elem'], '#AB3340')
        color = '#AB3340'
        if c_color is not None and a['elem'] == 'C':
            color = c_color
        styles.append({
            'visualization_type': 'stick',
            # stick, cartoon, sphere
            'color': color
        })
    return styles

def renumber_atoms(atoms, off, res):
    for a in atoms:
        a['serial'] += off
        a['chain'] = 'L'
        a['residue_index'] = res
    return atoms
def renumber_bonds(bonds, off):
    for b in bonds:
        b['atom1_index'] += off
        b['atom2_index'] += off
    return bonds

def join_data(x, y, res=0):
    offset = x['atoms'][-1]['serial']+1
    return {'atoms': x['atoms']+renumber_atoms(y['atoms'], offset, res),
            'bonds': x['bonds']+renumber_bonds(y['bonds'], offset)
           }

# Example output of pdbparser.mol3d_data()
#pdbdata = dict(atoms=[
#  {'serial': 0, 'name': 'N', 'elem': 'N', 'positions': [-34.168, 48.168, -15.656], 'mass_magnitude': 14.0067, 'residue_index': 0, 'residue_name': 'MET', 'chain': 'A'}, {'serial': 1, 'name': 'CA', 'elem': 'C', 'positions': [-33.665, 46.809, -15.848], 'mass_magnitude': 12.0107, 'residue_index': 0, 'residue_name': 'MET', 'chain': 'A'}],
#  bonds=[
#  {'atom1_index': 3512, 'atom2_index': 3625, 'bond_order': 1.0}, {'atom1_index': 4163, 'atom2_index': 4187, 'bond_order': 1.0}]
# )

# Carbon colors for each of 3 ligand poses
palette = ["#c8c8c8", "#fefec8", "#feb7af"]
class LigViewer:
    def __init__(self, name):
        with open(f'data/{name}.pdbqt') as f:
            pdbparser = PDBStringParser(f.read())

        self.target = name
        self.pdbdata = pdbparser.mol3d_data()
        self.pdbstyles = style_protein( self.pdbdata['atoms'])
        self.df = pd.read_parquet(f'data/{name}.sample.pq')
        self.data = self.pdbdata

    # show ligand by name
    def show_lig(self, name=None):
        data = self.pdbdata
        styles = self.pdbstyles

        self.data = data
        if name is None:
            return data, styles

        try:
            row = self.df.loc[name]
        except KeyError:
            return data, styles
        for i,col in enumerate(['conf', 'conf2', 'conf3']):
            lig = row[col]
            ligdata = PDBStringParser(lig).mol3d_data()
            ligstyles = style_ligand(ligdata['atoms'], palette[i])

            data = join_data(data, ligdata, 1000+i)
            styles = styles + ligstyles

        self.data = data
        return data, styles

def main(argv):
    data, styles, df = load_target(argv[1])
    print(f"Loaded {len(data['atoms'])} atoms and {len(data['bonds'])} bonds.")
    print(data['atoms'][-5:])
    print(data['bonds'][-5:])
    print(styles[-5:])
    print(df)

if __name__=="__main__":
    import sys
    main(sys.argv)
