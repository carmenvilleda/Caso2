#Librerias utilizadas
import dash
from dash import dcc
from dash import html
from dash import dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc

#data frame
ipc = pd.read_excel("IPC.xlsx")
cambio = pd.read_excel("cambio.xlsx")
imae = pd.read_excel("IMAE.xlsx")
df = pd.merge(ipc,cambio, on = ["Año","Mes"], how = "inner")
df = pd.merge(df,imae, on = ["Año","Mes"], how = "inner")

#construir dashboard
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server=app.server

app.title="Dashboard"

indicador=["TCR 1/", "Serie Original", "Vivienda, agua, electricidad, gas", "Salud", "Transporte","Educación"]

#Layout del app
app.layout = html.Div([
    html.Div([html.Div([
        
        #primer drop down para que elijan el mes y año
        html.Div(dcc.Dropdown(
            id = "fechas", value = ["2019","2020"], clearable =False, multi = True,
            options=[{'label':x, 'value':x} for x in sorted(df.Año.unique())]
        ),className="six columns", style={"width":"50%"},),
        
        #si van a elegir el IPC, Tipo Cambio o IMAE
        html.Div(dcc.Dropdown(
            id ="indicadores", value = "TCR 1/", clearable =False,
            options = [{'label': x, 'value':x} for x in indicador]
        ), className = "six columns"),
        ], className = "row"),],className ="custom-dropdown"),
    
    #graficas
    html.Div([dcc.Graph(id="graph", figure ={}, config ={"displayModeBar":True,"displaylogo":False,
                                                        }),],style ={'width':'1100px'}),
    
    html.Div([dcc.Graph(id="boxplot", figure={},)],style ={'width':'1100px'}),
    
    html.Div([dcc.Graph(id="scatter-plot", figure ={}, config ={"displayModeBar":True,"displaylogo":False,
                                                        }),],style ={'width':'1100px'}),
    
    #tabla
    html.Div(html.Div(id = "table-container"),style={'marginBottom':'15px','marginTop':
                                                     '10px'}),])


#callback de la funcion
@app.callback(
    [Output(component_id="graph",component_property="figure"),
    Output(component_id="boxplot",component_property="figure"),
    Output(component_id="scatter-plot",component_property="figure"),
    Output("table-container",'children')],
    [Input(component_id="fechas",component_property="value"),
    Input(component_id="indicadores",component_property="value")]
)

#funcion

def display_value(selected_date,selected_indicador):
    if len(selected_date)==0:
        df2=df[df["Año"].isin(["2019","2020"])]
    else:
        df2=df[df["Año"].isin(selected_date)]
        
    #primera grafica
    fig = px.line(df2,color="Año",x="Mes",markers=True,y = selected_indicador,
                 width=1000,height=500)
    
    fig.update_layout(title=f'{selected_indicador} de {selected_date}',
                     xaxis_title="Meses",)
    fig.update_traces(line=dict(width=2))
    
    #segunda grafica
    fig2 = px.box(df2,color="Año",x="Año", y = selected_indicador,
                 width=1000, height=500)
    fig2.update_layout(title=f'{selected_indicador} de {selected_date}',)
    
    #tercera grafica
    fig3 = px.scatter(df2, color = "Año", x = "Mes", y = selected_indicador,
                     width = 1000, height = 500)
    
    fig3.update_layout(title=f'{selected_indicador} de {selected_date}',
                      xaxis_title="Meses",)
    
    #modificacar datos para tabla
    df_reshaped = df2.pivot(index='Año', columns='Mes',values = selected_indicador)
    df_reshaped_2 = df_reshaped.reset_index()
    
    #tabla
    return(fig,fig2,fig3,
          dash_table.DataTable(columns=[{"name":i, "id":i} for i in df_reshaped_2],
                              data = df_reshaped_2.to_dict("records"),
                              export_format = "csv",
                              fill_width = True,
                              style_header = {'backgroundColor':'red',
                                             'color': 'white'},
                              ))
#192.168.0.18
#10.22.248.57
#192.168.0.18

#server y correr
if __name__=='__main__':
    app.run_server(debug=False,host="192.168.0.18",port=10000)
