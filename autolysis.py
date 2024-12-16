# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "pandas",
#   "seaborn",
#   "matplotlib",
#   "numpy",
#   "scipy",
#   "openai",
#   "scikit-learn",
#   "requests",
#   "ipykernel",
# ]
# ///

import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import argparse
import requests
import json
from sklearn.ensemble import IsolationForest
from scipy.stats import shapiro

# Constants
API_URL = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIyZjMwMDA0NDhAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.poWui37OxCs-EgxkK0_i382_ckWLbW_8xdrIVIaUr2s"
}

# Function to preprocess data (handle missing values)
def preprocess_data(df):
    numeric_cols = df.select_dtypes(include=[np.number])
    return numeric_cols.fillna(numeric_cols.mean())

# Function to analyze the data
def analyze_data(df):
    print("Analyzing the data...")
    summary_stats = df.describe()
    missing_values = df.isnull().sum()
    numeric_cols = df.select_dtypes(include=[np.number])
    corr_matrix = numeric_cols.corr() if not numeric_cols.empty else pd.DataFrame()
    print("Data analysis complete.")
    return summary_stats, missing_values, corr_matrix

# Function to detect outliers using Isolation Forest
def detect_outliers(df):
    numeric_cols = df.select_dtypes(include=[np.number]).dropna()
    if numeric_cols.empty:
        return pd.Series(dtype=int)
    model = IsolationForest(random_state=42)
    outlier_labels = model.fit_predict(numeric_cols)
    outliers = pd.Series(outlier_labels == -1, index=numeric_cols.index)
    return outliers.value_counts()

# Function to perform Shapiro-Wilk test for normality
def perform_shapiro_test(df):
    print("Performing Shapiro-Wilk normality test...")
    shapiro_results = {}
    numeric_cols = df.select_dtypes(include=[np.number])
    for col in numeric_cols.columns:
        if len(numeric_cols[col]) > 5000:
            shapiro_results[col] = "Sample size > 5000, test might not be accurate."
        else:
            stat, p_value = shapiro(numeric_cols[col])
            shapiro_results[col] = {"statistic": stat, "p_value": p_value}
    print("Shapiro-Wilk test complete.")
    return shapiro_results

# Function to generate visualizations
def visualize_data(df, corr_matrix, output_dir):
    numeric_cols = df.select_dtypes(include=[np.number])
    os.makedirs(output_dir, exist_ok=True)
    plots = []

    # Correlation Heatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
    heatmap_file = os.path.join(output_dir, "correlation_heatmap.png")
    plt.savefig(heatmap_file)
    plots.append(heatmap_file)
    plt.close()

    # Violin Plot
    plt.figure(figsize=(10, 6))
    sns.violinplot(data=numeric_cols)
    violin_file = os.path.join(output_dir, "violin_plot.png")
    plt.savefig(violin_file)
    plots.append(violin_file)
    plt.close()

    # Box Plot
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=numeric_cols)
    boxplot_file = os.path.join(output_dir, "boxplot.png")
    plt.savefig(boxplot_file)
    plots.append(boxplot_file)
    plt.close()

    # KDE Plot
    plt.figure(figsize=(10, 6))
    sns.kdeplot(data=numeric_cols, fill=True, common_norm=False)
    kde_file = os.path.join(output_dir, "kde_plot.png")
    plt.savefig(kde_file)
    plots.append(kde_file)
    plt.close()

    # Regression Plot
    if len(numeric_cols.columns) >= 2:
        plt.figure(figsize=(10, 6))
        sns.regplot(x=numeric_cols.columns[0], y=numeric_cols.columns[1], data=numeric_cols)
        regression_file = os.path.join(output_dir, "regression_plot.png")
        plt.savefig(regression_file)
        plots.append(regression_file)
        plt.close()

    # Distribution Plot
    if len(numeric_cols.columns) > 0:
        plt.figure(figsize=(10, 6))
        sns.histplot(numeric_cols.iloc[:, 0], kde=True, bins=30)
        distribution_file = os.path.join(output_dir, "distribution_plot.png")
        plt.savefig(distribution_file)
        plots.append(distribution_file)
        plt.close()

    # Scatter Plot
    if len(numeric_cols.columns) >= 2:
        plt.figure(figsize=(10, 6))
        sns.scatterplot(x=numeric_cols.columns[0], y=numeric_cols.columns[1], data=numeric_cols)
        scatter_file = os.path.join(output_dir, "scatterplot.png")
        plt.savefig(scatter_file)
        plots.append(scatter_file)
        plt.close()

    # Outliers Bar Plot
    outliers = detect_outliers(df)
    if not outliers.empty:
        plt.figure(figsize=(10, 6))
        outliers.plot(kind="bar", color="red")
        outliers_file = os.path.join(output_dir, "outliers_plot.png")
        plt.savefig(outliers_file)
        plots.append(outliers_file)
        plt.close()

    print("Visualizations generated.")
    return plots

# Function to generate narrative using OpenAI API
def generate_narrative(summary_stats, missing_values, corr_matrix, outliers, shapiro_results):
    print("Generating narrative using AI...")
    try:
        full_prompt = f"""
        You are a data scientist. Based on the following analysis results, provide insights and recommendations:
        - Summary Statistics: {summary_stats.to_dict()}
        - Missing Values: {missing_values.to_dict()}
        - Correlation Matrix: {corr_matrix.to_dict() if not corr_matrix.empty else 'No correlations detected.'}
        - Outliers Detected: {outliers.to_dict()}
        - Shapiro-Wilk Test Results: {shapiro_results}

        Write a narrative that:
        - Explains key findings from the data.
        - Highlights patterns from the visualizations like normal distributions and outliers.
        - Provides actionable insights and potential applications for the findings.
        - Concludes with recommendations based on your analysis.
        """
        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": full_prompt}
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }
        response = requests.post(API_URL, headers=HEADERS, data=json.dumps(data))
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            print(f"Error with AI response: {response.status_code} - {response.text}")
            return "Failed to generate narrative."
    except Exception as e:
        print(f"Error in narrative generation: {e}")
        return "Narrative generation failed."

# Function to create README file
def create_readme(narrative, output_dir):
    readme_file = os.path.join(output_dir, "README.md")
    with open(readme_file, "w") as f:
        f.write("# Automated Data Analysis Report\n\n")
        f.write(narrative)
    print(f"README file created at {readme_file}")
    return readme_file

# Main function
def main(csv_file):
    print("Starting analysis...")
    try:
        df = pd.read_csv(csv_file, encoding="ISO-8859-1")
        df = preprocess_data(df)
        print("Missing values handled.")

        summary_stats, missing_values, corr_matrix = analyze_data(df)
        outliers = detect_outliers(df)
        shapiro_results = perform_shapiro_test(df)

        plots = visualize_data(df, corr_matrix, output_dir=".")
        narrative = generate_narrative(summary_stats, missing_values, corr_matrix, outliers, shapiro_results)
        readme_file = create_readme(narrative, output_dir=".")
        print(f"Analysis complete! README file: {readme_file}")
    except Exception as e:
        print(f"Error during analysis: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python autolysis.py <dataset_path>")
        sys.exit(1)
    main(sys.argv[1])
