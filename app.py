import streamlit as st
import pandas as pd
import pyreadstat
import plotly.graph_objects as go

# Load the questionnaire data
df, meta = pyreadstat.read_sav('afrobarometer_release-dataset_ang_r9_pt_2023-03-01.sav')

# Load the question descriptions
question_descriptions = {}
with open('question_descriptions.txt', 'r') as f:
    for line in f:
        category, var_name, description = line.strip().split(': ')
        if category not in question_descriptions:
            question_descriptions[category] = {}
        question_descriptions[category][var_name] = description

# Group questions into categories
categories = list(question_descriptions.keys())

# Create the Streamlit app
st.sidebar.title('Selecione uma categoria')
category = st.sidebar.radio('', categories)

# Display all answer charts for questions inside the selected category
st.header(category)
for question_var, question_description in question_descriptions[category].items():
    answer_counts = df[question_var].value_counts()
    answer_labels = meta.variable_value_labels[question_var]
    answer_counts.index = [answer_labels[i] for i in answer_counts.index]
    st.subheader(question_description)
    # st.bar_chart(answer_counts, x_label="Total de Respostas", y_label="Respostas", stack=False, horizontal=True)
    # Create a Plotly bar chart
    fig = go.Figure(data=[go.Bar(
        x=answer_counts.values,
        y=answer_counts.index,
        orientation='h'  # Horizontal bars
    )])

    # Add labels to the top of each bar
    for i in range(len(answer_counts)):
        fig.add_annotation(
            x=answer_counts.values[i],
            y=answer_counts.index[i],
            text=str(answer_counts.values[i]),
            showarrow=False,
            font=dict(size=10, color='black', weight='bold'),  # Black and bold text
            yshift=0,  # Center the label on the bar
            xanchor='center',  # Center the label horizontally
            bgcolor='yellow',  # Yellow background
            opacity=0.8  # Adjust background transparency
        )

    fig.update_layout(
#        title=question_description,
        xaxis_title="Total de Respostas",
        yaxis_title="Respostas"
    )
    st.plotly_chart(fig)