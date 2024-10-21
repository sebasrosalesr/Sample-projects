# -*- coding: utf-8 -*-
"""RCV_analyzer.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1p5tA_U6Kd0ytve38AEaTQdFcKey8epvK

### Python Data Classification for RCV Patients

This script provides a comprehensive solution to classify and analyze data for RCV patients based on various medical parameters. Here is a summary of the steps and functions used:

1.	Finding Column Indices:
	•	The function find_column_index searches for columns containing specific keywords (e.g., “Estadio ERC” and “Sexo”) and returns their indices.

	2.	Column Index Identification:
	•	Using the find_column_index function, the indices for “Estadio ERC” and “Sexo” columns are identified and stored.

	3.	Data Preparation:
	•	Leading and trailing spaces are removed from column names.
	•	All columns containing the word “Fecha” are converted to datetime format.
	•	The column at the identified index for “Estadio ERC” is converted to numeric format.
	•	The DataFrame is filtered to include only rows where “Estadio ERC” equals 2, creating df1.

	4.	Converting TFG Columns to Floats:
	•	Columns TFG 1, TFG2, and TFG3 are converted to floats, handling non-numeric values.

	5.	Checking Interval Between Dates:
	•	The check_interval function checks if the interval between three date columns is less than or equal to 4 months.
	•	Applied to both “Creatinina” and “RAC” date columns to create new columns in df1.

	6.	Creatinine Levels Analysis:
	•	The check_creatinine_levels function evaluates creatinine levels based on sex and categorizes the number of abnormal readings.
	•	Applied to df1 to create a new column indicating creatinine level status.

	7.	TFG Levels Analysis:
	•	The check_tfg_levels function checks if TFG levels in three columns are below 60 and categorizes them accordingly.
	•	Applied to df1 to create a new column indicating TFG level status.
  
	8.	RAC Expiration Check:
	•	The check_rac_expiration function determines if the RAC date is more than a year old and flags it as expired.
	•	Applied to df1 to create a new column indicating RAC expiration status.
"""

# Import necessary libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

#Creating data frame.(Doesn't matter if the typos of the columns has subtle differences the code will fix it)
df= pd.read_csv('/content/drive/MyDrive/Deep Learning Projects/r_projects /data/BD RCV JUNIO 2024 VIDA.xlsx - BASE RCV CISVIDA.csv')
df.columns.value_counts()

#find the column ESTADIO ERC and SEX, This function, find_column_index, converts both the column names and the keywords to
#lowercase before checking for the presence of the keywords.
#This ensures that the function can handle case variations and find the correct column indices.

def find_column_index(df, keywords):
    """
    Function to find the index of the column that contains the given keywords.

    Parameters:
    df (pd.DataFrame): The DataFrame to search.
    keywords (list of str): The keywords to search for.

    Returns:
    int: The index of the column that contains the keywords, or -1 if not found.
    """
    for col in df.columns:
        if all(keyword in col for keyword in keywords):
            return df.columns.get_loc(col)
    return -1

# Example usage
keywords = ['Estadio ERC']
column_index = find_column_index(df, keywords)

if column_index != -1:
    print(f"The index of the column containing the keywords '{keywords}' is: {column_index}")
else:
    print(f"No column found containing the keywords '{keywords}'")


keywords_sexo = ['Sexo']
column_index_sexo = find_column_index(df, keywords_sexo)

if column_index_sexo != -1:
    print(f"The index of the column containing the keyword '{keywords_sexo}' is: {column_index_sexo}")
else:
    print(f"No column found containing the keyword '{keywords_sexo}'")

sex_c = column_index_sexo

# Strip leading and trailing spaces from column names
df.columns = df.columns.str.strip()

# Print column names to check for discrepancies
print(df.columns)

# Convert all columns containing the word "Fecha" to datetime
date_columns = df.filter(like='Fecha').columns
df[date_columns] = df[date_columns].apply(pd.to_datetime, errors='coerce')

# Convert the column at index column_index  to numeric
df.iloc[:, column_index ] = pd.to_numeric(df.iloc[:, column_index ], errors='coerce')

# Filter for '39. Estadio ERC (Enfermedad Renal: Ver las notas finales numeral V)' equal to 2
df1 = df[df.iloc[:, column_index] == 2].copy()

# Convert TFG columns to floats, handling non-numeric values
tfg_columns = ['TFG 1', 'TFG2', 'TFG3']
df1[tfg_columns] = df1[tfg_columns].apply(pd.to_numeric, errors='coerce')

# Function to check if the interval between dates is less than or equal to 4 months
def check_interval(row):
    date1 = row['Fecha Creatinina - TOMA 1: (para estudio de ERC)']
    date2 = row['Fecha Creatinina - TOMA 2: (para estudio de ERC)']
    date3 = row['Fecha Creatinina - TOMA3: (para estudio de ERC)']

    if pd.isna(date1) or pd.isna(date2) or pd.isna(date3):
        return False
    interval1 = (date2 - date1).days <= 120  # Approximate 4 months as 120 days
    interval2 = (date3 - date2).days <= 120

    return interval1 and interval2

# Apply the function to the DataFrame
df1['Interval <= 4 Months for Creatinina'] = df1.apply(check_interval, axis=1)

# Function to check creatinine levels based on sex
def check_creatinine_levels(row):
    sexo = row.iloc[sex_c]
    creatinine_levels = [
        row['Creatinina - TOMA 1: (para estudio de ERC)'],
        row['Creatinina - TOMA 2: (para estudio de ERC)'],
        row['Creatinina - TOMA 3: (para estudio de ERC)']
    ]
    threshold = 1.3 if sexo == 'M' else 1.1
    num_above_threshold = sum(level > threshold for level in creatinine_levels)

    if num_above_threshold == 1:
        return '1 creatinina alterada'
    elif num_above_threshold == 2:
        return '2 creatininas alteradas'
    elif num_above_threshold == 3:
        return 'todas las creatininas alteradas'
    else:
        return 'sin alteraciones'

# Apply the function to the DataFrame
df1['Creatinine Levels'] = df1.apply(check_creatinine_levels, axis=1)

# Function to check TFG levels
def check_tfg_levels(row):
    tfg1 = row['TFG 1']
    tfg2 = row['TFG2']
    tfg3 = row['TFG3']
    result = []

    if tfg1 < 60:
        result.append('TFG 1 anormal')
    if tfg2 < 60:
        result.append('TFG 2 anormal')
    if tfg3 < 60:
        result.append('TFG 3 anormal')

    return ', '.join(result) if result else 'TFGs normales'

# Apply the function to the DataFrame
df1['TFG Levels'] = df1.apply(check_tfg_levels, axis=1)

# Display the updated DataFrame
print(df1)

df1.head(100)

#For RAC values, apply the same Function to check if the interval between dates is less than or equal to 4 months
def check_interval(row, date_col1, date_col2, date_col3):
    date1 = row[date_col1]
    date2 = row[date_col2]
    date3 = row[date_col3]

    if pd.isna(date1) or pd.isna(date2) or pd.isna(date3):
        return False
    interval1 = (date2 - date1).days <= 120  # Approximate 4 months as 120 days
    interval2 = (date3 - date2).days <= 120

    return interval1 and interval2

# Apply the function to the DataFrame for RAC
df1['RAC Interval <= 4 Months'] = df1.apply(lambda row: check_interval(row, 'Fecha RAC - TOMA 1: (para estudio de ERC)',
                                                                       'Fecha RAC - TOMA 2: (para estudio de ERC)',
                                                                       'Fecha RAC - TOMA 3: (para estudio de ERC)'), axis=1)

# Function to check RAC expiration
def check_rac_expiration(date1):
    if pd.isna(date1):
        return 'Fecha RAC 1 no disponible'
    today = pd.Timestamp.today()
    if (today - date1).days > 365:
        return 'RAC vencido'
    return 'RAC vigente'

# Apply the function to the DataFrame for RAC expiration
df1['RAC Expiration'] = df1['Fecha RAC - TOMA 1: (para estudio de ERC)'].apply(check_rac_expiration)

# Display the updated DataFrame
print(df1)

df1.head(100)

import os

# Define the directory and file path in Google Drive
directory = '/content/drive/MyDrive/Deep Learning Projects/r_projects_csv'
file_path = os.path.join(directory, 'cis_vida_pyy.csv')

# Ensure the directory exists
os.makedirs(directory, exist_ok=True)

# Save the DataFrame to a CSV file
df1.to_csv(file_path, index=False)

print(f"DataFrame saved to '{file_path}'")
