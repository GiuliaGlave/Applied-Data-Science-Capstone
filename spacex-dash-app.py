# dash_interactivity.py
# Import required libraries
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import dash
from dash import html, dcc
from dash.dependencies import Input, Output

#read cvs file
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Calculate min and max  payload
min_payload = spacex_df['Payload Mass (kg)'].min()
max_payload = spacex_df['Payload Mass (kg)'].max()

# Create a dash application
app = dash.Dash(__name__)
                               
app.layout = html.Div(children=[ html.H1('SpaceX Launch Records Dashboard', 
                                style={'textAlign': 'center', 'color': '#503D36',
                                'font-size': 40}),
                                
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=[
                                        {'label': 'All Sites', 'value': 'ALL'},
                                        {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                        {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                        {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                        {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}
                                    ],
                                    value='ALL',
                                    placeholder="Seleziona qui un sito di lancio",
                                    searchable=True
                                ),
                                
                                # Pie Chart
                                dcc.Graph(id='success-pie-chart'),
                                
                                #Range Slider
                                html.H4("Payload Range (kg):", style={'margin-top': '20px'}),
                                
                                dcc.RangeSlider(
                                    id='payload-slider',                
                                    min=0, 
                                    max=10000, 
                                    step=1000,                 
                                    marks={0: '0',100: '100'},            
                                    value=[spacex_df['Payload Mass (kg)'].min(), spacex_df['Payload Mass (kg)'].max()]
                                ),

                                # Scatter plot
                                dcc.Graph(id='success-payload-scatter-chart')

                                ])


# Function decorator to specify function input and output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),              
    Input(component_id='site-dropdown', component_property='value')
)

def get_pie_chart(entered_site):    
    if entered_site == 'ALL':
        # Pie chart che mostra i successi totali per sito
        fig = px.pie(
            spacex_df,
            names='Launch Site',
            values='class',
            title='Totale successi per sito'
        )
        return fig
    else:
        # Filtriamo il dataframe per sito selezionato
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        # Conteggiamo successi (class=1) e fallimenti (class=0)
        site_counts = filtered_df['class'].value_counts().reset_index()
        site_counts.columns = ['class', 'counts']
        fig = px.pie(
            site_counts,
            names='class',
            values='counts',
            title=f'Success vs Fail per {entered_site}'
        )
        return fig

@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [
        Input('site-dropdown', 'value'),
        Input('payload-slider', 'value')
    ]
)
def update_scatter(selected_site, payload_range):
    low, high = payload_range
    # Filtra per payload
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) &
                            (spacex_df['Payload Mass (kg)'] <= high)]
    
    # Filtra per sito se selezionato
    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
    
    # Crea lo scatter plot
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title='Correlation between Payload and Mission Success',
        labels={'class': 'Mission Success'}
    )
    return fig

if __name__ == '__main__':
    app.run(debug=True)