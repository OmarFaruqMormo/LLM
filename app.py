from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import spacy
import openai

# Load spaCy Model
nlp = spacy.load('en_core_web_sm')

# Set Up OpenAI for LLM Chat Interface
openai.api_key = "your openai api key"

# Initialize the app with suppress_callback_exceptions set to True
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

# Define common navigation layout
def navbar():
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        dbc.NavbarSimple(
                            brand="Sorcerous Dash App",
                            brand_href="/",
                            color="dark",
                            dark=True,
                            className="mb-4",
                            style={'padding': '10px 20px'}
                        ),
                        width='20',  # Auto width to fit the content
                        className="text-center"  # Center the content
                    )
                ],
                justify="center",  # Center the row
                className="mb-4"
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Nav(
                            [
                                dbc.NavItem(dbc.NavLink("Text Similarity", href="/", className="nav-link")),
                                dbc.NavItem(dbc.NavLink("Chat with LLM", href="/chat", className="nav-link"))
                            ],
                            pills=True,
                            className="justify-content-center"
                        ),
                        width=12  # Full width for the row
                    )
                ],
                justify="center",  # Center the row
                className="mb-2"
            )
        ]
    )



# Define Text Similarity Layout with Enhanced Styling
def text_similarity_layout():
    return html.Div(style={'padding': '20px'}, children=[
        html.H2("Text Similarity Calculator", style={'color': '#333', 'textAlign': 'center', 'marginBottom': '20px'}),
        
        dcc.Input(id='input_text1', type='text', placeholder='Enter first text', 
                  className='input-box'),
        
        dcc.Input(id='input_text2', type='text', placeholder='Enter second text', 
                  className='input-box'),
        
        html.Div(className='button-container', children=[
            html.Button('Calculate Similarity', id='submit_button', n_clicks=0, 
                        className='button'),
        ]),
        
        dcc.Loading(
            id="loading-1",
            type="circle",
            children=html.Div(id='similarity_output', className='output-box')
        ),
        
        dcc.Store(id='notification', storage_type='memory'),
        html.Div(id='notification_div')
    ])

# Define Chat Layout with Enhanced Styling
def chat_layout():
    return html.Div(style={'padding': '20px'}, children=[
        html.H2("Chat with LLM", style={'color': '#333', 'textAlign': 'center', 'marginBottom': '20px'}),
        
        dcc.Input(id='chat_input', type='text', placeholder='Ask a question', 
                  className='input-box'),
        
        html.Div(className='button-container', children=[
            html.Button('Send', id='chat_button', n_clicks=0, 
                        className='button'),
        ]),
        
        dcc.Loading(
            id="loading-2",
            type="circle",
            children=html.Div(id='chat_output', className='output-box')
        )
    ])


# Define the overall app layout with navigation and page content
app.layout = html.Div([
    navbar(),
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content', style={'padding': '20px'})
])

# Update page layout based on URL
@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/chat':
        return chat_layout()
    return text_similarity_layout()

# Callbacks for Text Similarity
@app.callback(
    [Output('similarity_output', 'children'), Output('notification', 'data')],
    [Input('submit_button', 'n_clicks')],
    [State('input_text1', 'value'), State('input_text2', 'value')]
)
def calculate_similarity(n_clicks, text1, text2):
    if n_clicks > 0:
        if not text1 or not text2:
            return "", "Please enter text in both fields."
        doc1 = nlp(text1)
        doc2 = nlp(text2)
        similarity_score = doc1.similarity(doc2)
        return f"Similarity Score: {similarity_score:.2f}", ""
    return "", ""

# Notification Callback
@app.callback(
    Output('notification_div', 'children'),
    Input('notification', 'data')
)
def show_notification(message):
    if message:
        return html.Div(message, style={'color': 'red', 'fontWeight': 'bold', 'marginTop': '10px'})
    return ""

# Callback for Chat Interface with LLM
from openai.error import RateLimitError

@app.callback(
    Output('chat_output', 'children'),
    [Input('chat_button', 'n_clicks')],
    [State('chat_input', 'value')]
)
def chat_with_llm(n_clicks, question):
    if n_clicks > 0 and question:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": question}]
            )
            return response['choices'][0]['message']['content'].strip()
        except RateLimitError:
            return "You have exceeded your quota. Please try again later."
    return ""



# Run the Application
if __name__ == '__main__':
    app.run_server(debug=True)
