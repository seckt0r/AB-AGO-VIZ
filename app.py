import streamlit as st
import pandas as pd
import pyreadstat
import plotly.graph_objects as go

st.title("Visualização de Dados do Afrobarômetro")
st.markdown("""
Os dados a seguir são extraídos do conjunto de dados do Round 9 (2022) referentes a Angola, do Afrobarômetro.
""")
st.markdown("---")

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

# Define the columns for filtering (non-sequential)
filter_columns = ['URBRUR', 'REGION', 'THISINT']

# Create the filter options
st.sidebar.title('Filtros')
filter_values = {}
for col in filter_columns:
    # Get unique values and their descriptions
    unique_values = df[col].unique()
    value_labels = meta.variable_value_labels[col]
    unique_descriptions = [value_labels[i] for i in unique_values]
    
    # Replace column name with custom text
    custom_text = {
        'URBRUR': 'Contexto',
        'REGION': 'Província',
        'THISINT': 'Gênero'
    }.get(col, col)  # Use custom text if available, otherwise use column name

    filter_values[col] = st.sidebar.multiselect(f'Selecione valores para {custom_text}', unique_descriptions, placeholder="Escolha uma opção")

# Filter the data based on selected values
filtered_df = df.copy()
for col, values in filter_values.items():
    if values:
        # Get the value labels for the current column
        value_labels = meta.variable_value_labels[col] 
        # Get the corresponding indices for the selected descriptions
        selected_indices = [list(value_labels.keys())[i] for i, desc in enumerate(value_labels.values()) if desc in values]
        # Apply the filter correctly using the indices
        filtered_df = filtered_df[filtered_df[col].isin(selected_indices)]

# Check if any data remains after filtering
if filtered_df.empty:
    st.header("Nenhuma resposta corresponde aos filtros.")
else:
    # Display all answer charts for questions inside the selected category
    st.header(category)
    st.markdown("---")
    for question_var in df.columns[2:]:  # Start from column Q3 (index 2)
        if question_var in question_descriptions[category]:
            question_description = question_descriptions[category][question_var]
            answer_counts = filtered_df[question_var].value_counts()
            answer_labels = meta.variable_value_labels[question_var]
            answer_counts.index = [answer_labels[i] for i in answer_counts.index]
            st.subheader(question_description)
            # Create a Plotly bar chart
            fig = go.Figure(data=[go.Bar(
                x=answer_counts.values,
                y=answer_counts.index,
                orientation='h'  # Horizontal bars
            )])

            # Add labels to the top of each bar
            for i in range(len(answer_counts)):
                # Calculate percentage
                percentage = (answer_counts.values[i] / answer_counts.sum()) * 100
                # Format percentage to two decimal places
                percentage_str = f"{percentage:.2f}%"
                fig.add_annotation(
                    x=answer_counts.values[i],
                    y=answer_counts.index[i],
                    text=f"{answer_counts.values[i]} ({percentage_str})",  # Add percentage to label
                    showarrow=False,
                    font=dict(size=10, color='black', weight='bold'),  # Black and bold text
                    yshift=0,  # Center the label on the bar
                    xanchor='center',  # Center the label horizontally
                    bgcolor='yellow',  # Yellow background
                    opacity=0.8  # Adjust background transparency
                )

            legend_text = []
            for col, values in filter_values.items():
                if values:
                    legend_text.append(f"{col}: {', '.join(values)}")
            fig.update_layout(
                xaxis_title="Total de Respostas",
                yaxis_title="Respostas",
                legend_title="Filtros activos",
                legend=dict(
                    traceorder="normal",
                    font=dict(
                        family="sans-serif",
                        size=12,
                        color="black"
                    ),
                    bgcolor="LightSteelBlue",
                    bordercolor="Black",
                    borderwidth=2
                )
            )
            st.plotly_chart(fig)
            st.markdown("---")