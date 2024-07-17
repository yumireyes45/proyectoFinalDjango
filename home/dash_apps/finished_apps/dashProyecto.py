from django_plotly_dash import DjangoDash
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import plotly.figure_factory as ff
import requests
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from tracker.models import Project, Task
from django.contrib.auth.models import User


def graph_empty(text=''):
    layout = dict(
        autosize=True,
        annotations=[dict(text=text, showarrow=False)],
        #paper_bgcolor="#1c2022",
        #plot_bgcolor="#1c2022",
        #font_color="#A3AAB7",
        font=dict(color="FFFF", size=20),
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
    )
    return {"data": [], "layout": layout}

def cardGraph(id = "",figure = graph_empty(text='')):
        return html.Div([
            dmc.LoadingOverlay(
                loaderProps={"variant": "bars", "color": "#01414b", "size": "xl"},
                loader=dmc.Image(src="https://i.imgur.com/KIj15up.gif", alt="", caption="", width=70,height=70),
                children=[
                    dmc.Card(
                        children=[
                            dmc.ActionIcon(
                                DashIconify(icon=f"feather:{"maximize"}"), 
                                color="blue", 
                                variant="default",
                                id=f"maxi{id}",
                                n_clicks=0,
                                mb=10,
                                style={'position': 'absolute','top': '4px','right': '4px','z-index': '99'},
                            ),
                            dcc.Graph(id=id, figure= figure)# figure=graph_empty
                        ],
                        withBorder=True,
                        shadow="sm",
                        radius="md",
                        p=0
                    ),
                ]
            ),

        ])



def dashboard(user_id):

    # Iniciar la aplicación Dash
    app = DjangoDash('dashProyecto')

    # Obtener el usuario por user_id
    user = User.objects.get(id=user_id)
    username = user.username  # Obtener el username del usuario
    
    # Obtener proyectos del usuario logeado
    projects = Project.objects.filter(owner=user_id)

    # Preparar los datos para un componente Dropdown en Dash
    projects_data = [
        {'label': project.name, 'value': project.id} for project in projects
    ]

    # Seleccionar el primer proyecto por defecto para simplificar
    selected_project_id = projects.first().id if projects else None
    print(selected_project_id)


    tasks = Task.objects.filter(project=selected_project_id)
    df_tasks = pd.DataFrame.from_records(tasks.values('name', 'completed', 'project', 'start_date', 'end_date', 'description', 'assigned_to'))

    # Obteniendo los nombres de los usuarios a partir de los IDs
    user_ids = df_tasks['assigned_to'].unique()
    users = User.objects.filter(id__in=user_ids)
    user_map = {user.id: user.username for user in users}
    df_tasks['assigned_to'] = df_tasks['assigned_to'].map(user_map)

    user_options = [{'label': username, 'value': username} for userid, username in user_map.items()]
    
    # Renombrar las columnas del DataFrame
    df_grant = df_tasks.rename(columns={
    'name': 'Task',         # Cambiar 'name' a 'Task'
    'start_date': 'Start',  # Cambiar 'start_date' a 'Start'
    'end_date': 'Finish',    # Cambiar 'end_date' a 'Finish'
    'completed': 'Resource', # Cambiar 'descriçion' a 'resource'
    })

    #df_grant['Resource']=df_grant['Resource'].astype(str)

    df_grant['Resource'] = df_grant['Resource'].map({True: 'Completo', False: 'Incompleto'})
    
    def cambioNum(num):
         if num=='False':
              return 'Incompleto'
         else:
              return 'Completo'
         
    #df_grant['Resource']=df_grant.apply(lambda x: cambioNum(x['Resource']), axis=1)

    
    print("-------------------------")
    print(df_grant)
    print("-------------------------")
    print(df_tasks)
    print("-------------------------")
    


    df_tasks['completed_numeric'] = df_tasks['completed'].astype(int)

    project_completion = df_tasks.groupby(['project', 'name'])[['completed_numeric']].mean().reset_index()
    project_completion['completed_percent'] = project_completion['completed_numeric'] * 100


    # Gráfico de porcentaje de tareas completadas y no completadas
    completion_counts = df_tasks['completed'].value_counts()
    completion_counts.index = ['Completadas' if x else 'No Completadas' for x in completion_counts.index]
    completion_fig = px.pie(
        values=completion_counts.values,
        names=completion_counts.index,
        color= completion_counts.index,
        color_discrete_map= {"No Completadas": "red",
                             "Completadas": "blue"},
        title='Porcentaje de Tareas Completadas vs No Completadas'
    )

    #Grafico grant de completas e incompletas
    colors = {
          'Incompleto': 'rgb(255, 0, 0)',
          'Completo': 'rgb(13, 13, 238)'}
    
    
    
    grant_fig = ff.create_gantt(df_grant, colors=colors, index_col='Resource', show_colorbar=True,
                      group_tasks=True, title='Tareas Completas y No Completas con Fechas')
    
    # Crear gráficos de tareas completadas y no completadas
    histograma_fig = px.histogram(
        df_tasks, 
        x='assigned_to', 
        color='completed', 
        barmode='group',
        title='Tareas Completadas y No Completadas por Usuario'
    )
    
    fig_not_completed = px.bar(
        df_tasks[df_tasks['completed'] == False],
        x='assigned_to',
        y='completed',
        color='assigned_to',
        title='Tareas No Completadas por Usuario'
    )
    
    app.layout = dmc.Container([
    
    dmc.Grid([
        dmc.Col([],span=3),
        dmc.Col([dmc.Title(f"Tareas Completadas por Proyecto de {username}",align="center"),],span=6),
        dmc.Col([],span=3),
        dmc.Col([
            
            dmc.Card(
                children=[
                    dcc.Graph(figure=completion_fig),
                ],
                withBorder=True,
                shadow="sm",
                radius="md",
                p=0,
                h=600
            )
            
            
            
            ],span=6),
        dmc.Col([
            
            dmc.Card(
                children=[
                    dcc.Graph(figure=grant_fig),
                ],
                withBorder=True,
                shadow="sm",
                radius="md",
                p=0,
            )
            
            
            
            ],span=6),
        dmc.Col([],span=3),
        dmc.Col([dmc.Title("Tareas Completadas por Usuario",align="center"),],span=6),
        dmc.Col([],span=3),
        dmc.Col([],span=3),
        dmc.Col([
            dcc.Dropdown(
            id='user-dropdown',
            options=user_options,
            value=user_options[0]['value'] if user_options else None,
            clearable=False,
        )
        ],span=6),
        dmc.Col([],span=3),
        dmc.Col([
            
            dmc.Card(
                children=[
                    dcc.Graph(id='tasks-histograma'),
                ],
                withBorder=True,
                shadow="sm",
                radius="md",
                p=0,
            )
            
            
            
            ],span=12),
    ],gutter="xl")
    

],fluid=True)
    
    @app.callback(
        Output('tasks-histograma', 'figure'),
        Input('user-dropdown', 'value')
    )

    def update_graphs(selected_user):
        #grafico tareas completadas
        filtered_tasks = df_tasks[df_tasks['assigned_to'] == selected_user]
        df_test=filtered_tasks.groupby('completed')[['name']].count().reset_index()

        fig = px.bar(df_test, x="completed",
             y='name',
             height=400)
        
        fig.update_layout(
            bargap=0.7, # gap between bars of adjacent location coordinates.
            bargroupgap=0.1 # gap between bars of the same location coordinate.
        )

        completed_fig = px.histogram(
            filtered_tasks[filtered_tasks['completed'] == True],
            x='name',
            title='Tareas Completadas'
        )

        completed_fig.update_layout(
            bargap=0.7, # gap between bars of adjacent location coordinates.
            bargroupgap=0.1 # gap between bars of the same location coordinate.
        )

        #grafico tareas no completadas
        not_completed_fig = px.histogram(
            filtered_tasks[filtered_tasks['completed'] == False],
            x='name',
            title='Tareas No Completadas'
        )

        not_completed_fig.update_layout(
            bargap=0.7, # gap between bars of adjacent location coordinates.
            bargroupgap=0.1 # gap between bars of the same location coordinate.
        )

        return fig




