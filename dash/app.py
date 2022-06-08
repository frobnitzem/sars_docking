#!/usr/bin/env python3

import os

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from dash.development.base_component import Component

import dash_bio as dashbio

from helpers import make_dash_table, LigViewer
from scatterplot3d import scatter_plot_3d

targets = {
        'MPro 5R84': '5r84',
        'MPro 6WQF': '6wqf',
        'PLPro 7JIR': '7jir',
        'Spike 6M0J': '6m0j',
        'NSP15 6WLC': '6wlc',
        'RDRP': 'rdrp',
}

app = dash.Dash('drug-discovery')
dataset = LigViewer('5r84')

FIGURE = scatter_plot_3d(dataset)

@app.callback(
    Output('dashbio-molecule3d', 'modelData'),
    Output('dashbio-molecule3d', 'styles'),
    Input('target-selector', 'value'),
    Input('clickable-graph', 'clickData')
)
def plot_molecule(target, molname):
    global dataset
    if target != dataset.target:
        dataset = LigViewer(target)
    name = dfNameFromHover(molname)
    atoms, styles = dataset.show_lig(name)
    return atoms, styles

# Show information on selected atoms
@app.callback(
    #Output('molecule3d-output', 'children'),
    Output('dashbio-molecule3d', 'zoomTo'),
    Input('dashbio-molecule3d', 'selectedAtomIds')
)
def show_selected_atoms(atom_ids):
    if atom_ids is None or len(atom_ids) == 0:
        return {},
        #'No atom has been selected. Click somewhere on the molecular \
        #structure to select an atom.', {}

    #names = [html.Div([
    #    html.Div('{name} {residue_name}{residue_index} {chain}'.format(
    #                **dataset.data['atoms'][atm])),
    #    html.Br()
    #]) for atm in atom_ids]

    last_atom = dataset.data['atoms'][atom_ids[-1]]
    zoomTo = {'animationDuration': 300,
              'sel': {'chain': last_atom['chain'],
                      'resi': last_atom['residue_index']}
             }
    return zoomTo

@app.callback(
    Output('clickable-graph', 'figure'),
    Input('target-selector', 'value'),
    Input('charts_radio', 'value'))
def highlight_molecule(target, plot_type):
    global FIGURE
    global dataset
    if target != dataset.target:
        dataset = LigViewer(target)
    FIGURE = scatter_plot_3d(dataset, plot_type = plot_type)
    return FIGURE

def dfNameFromHover( hoverData ):
    ''' Returns index name for hover point '''
    if hoverData is not None:
        if 'points' in hoverData:
            firstPoint = hoverData['points'][0]
            if 'pointNumber' in firstPoint:
                point_number = firstPoint['pointNumber']
                molecule_name = str(FIGURE['data'][0]['text'][point_number]).strip()
                return molecule_name
    return None

def dfRowFromHover( hoverData ):
    ''' Returns row for hover point as a Pandas Series '''
    name = dfNameFromHover(hoverData)
    if name is None:
        return None
    try:
        return dataset.df.loc[name]
    except KeyError:
        return None

# TODO: check original app callbacks from hoverData
# -> accessing element children, etc.

empty_info = make_dash_table(
                header=['name', 'atoms', 'tors'],
                cells = [['']]*3
               )
@app.callback(
    Output('chem_info', 'children'),
    [Input('clickable-graph', 'hoverData')])
def chem_info(hoverData=None):
    row = dfRowFromHover(hoverData)
    if row is None:
        return empty_info
    return make_dash_table(
                header=['name', 'atoms', 'tors'],
                cells =[[row.name], [row['atoms']], [row['tors']]],
           )
@app.callback(
    Output('draw_info', 'children'),
    [Input('clickable-graph', 'clickData')])
def draw_info(hoverData=None):
    row = dfRowFromHover(hoverData)
    if row is None:
        return empty_info
    return make_dash_table(
                header=['name', 'atoms', 'tors'],
                cells =[[row.name], [row['atoms']], [row['tors']]],
           )

empty_scores = make_dash_table(
                header = ['AutoDockGPU', 'RF3', 'VS-DUD-E v2'],
                cells  = [['']*3]*3
               )
@app.callback(
    Output('chem_scores', 'children'),
    [Input('clickable-graph', 'hoverData')])
def chem_scores(hoverData):
    row = dfRowFromHover(hoverData)
    if row is None:
        return empty_scores
    p2 = lambda x: f"%.2f"%float(row[x])
    ext3 = lambda name: [p2(name), p2(f"{name}2"), p2(f"{name}3")]
    return make_dash_table(
                header=['AutoDockGPU', 'RF3', 'VS-DUD-E v2'],
                cells =[ext3('score'), ext3('rf3'), ext3('vs_dude_v2')]
           )
@app.callback(
    Output('draw_scores', 'children'),
    [Input('clickable-graph', 'clickData')])
def chem_scores(hoverData):
    row = dfRowFromHover(hoverData)
    if row is None:
        return empty_scores
    p2 = lambda x: f"%.2f"%float(row[x])
    ext3 = lambda name: [p2(name), p2(f"{name}2"), p2(f"{name}3")]
    return make_dash_table(
                header=['AutoDockGPU', 'RF3', 'VS-DUD-E v2'],
                cells =[ext3('score'), ext3('rf3'), ext3('vs_dude_v2')]
           )

app.layout = html.Div([
    # Row 2: Hover Panel and Graph
    html.Div([
        html.Div(children=[
            html.H3(children='SARS-CoV2 Molecular Docking'),
            dcc.Dropdown(
                options=[{'label':k, 'value':v} for k,v in targets.items()],
                value=dataset.target,
                searchable=False,
                clearable=False,
                id='target-selector'
            ),
            dashbio.Molecule3dViewer(
                id='dashbio-molecule3d',
                modelData={'atoms':[], 'bonds':[]},
                selectionType='Residue',
                styles=[],
                #labels=[
                #    {'text': 'Residue Chain: A', 'position': {'x': 15.407, 'y': -8.432, 'z': 6.573}}
                #],
            ),
            #html.Div(id = 'molecule3d-output'),
            html.Br(),
            html.Div([ html.Table(
                           empty_info,
                           id="draw_info",
                           className="table__container",
                        )
                    ], className="container bg-white p-0",
            ),
            html.Br(),
            html.Div([ html.Table(
                           empty_scores,
                           id="draw_scores",
                           className="table__container",
                        )
                    ], className="container bg-white p-0",
            ),
        ], style=dict(padding=10, flex=2) ),

        html.Div(children=[
            html.Div([
                html.P('HOVER over a point in the graph to see its scores below.'),
                html.P('CLICK a point to the right to see its structure to the left.')
            ], style={'margin-left': '10px'}),
            dcc.RadioItems(
                id = 'charts_radio',
                options=[
                    dict( label='3D Scatter', value='scatter3d' ),
                    dict( label='2D Scatter', value='scatter' ),
                    dict( label='2D Histogram', value='histogram2d' ),
                ],
                labelStyle = dict(display='inline'),
                value='scatter'
            ),
            dcc.Graph(id='clickable-graph',
                      style=dict(width='500px'),
                      figure=FIGURE ),
            html.Br(),
            html.Div([ html.Table(
                           empty_info,
                           id="chem_info",
                           className="table__container",
                        )
                    ], className="container bg-white p-0",
            ),
            html.Br(),
            html.Div([ html.Table(
                           empty_scores,
                           id="chem_scores",
                           className="table__container",
                        )
                    ], className="container bg-white p-0",
            ),
        ], style=dict(textAlign='center', padding=10, flex=3)),
    ], style={'display': 'flex', 'flex-direction': 'row'}),
    html.Br(),
    html.Div(children='''
        (CC-BY-SA) 2021 Oak Ridge National Laboratory, OLCF On Demand Project
''')
], className='container')



if __name__ == '__main__':
    app.run_server(debug=True)
