# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pandas",
#     "matplotlib",
#     "seaborn",
#     "httpx",
#     "numpy",
#     "scipy",
#     "scikit-learn",
#     "tabulate"
# ]
# ///

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import httpx
from scipy.stats import zscore, pearsonr
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from tabulate import tabulate

# API Configuration
API_ENDPOINT = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIyZjMwMDA0NDhAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.poWui37OxCs-EgxkK0_i382_ckWLbW_8xdrIVIaUr2s"

# Retry logic for API calls
def query_llm(messages, retries=3):
    if not ACCESS_TOKEN:
        print("Error: AIPROXY_TOKEN is not set. Please set it as an environment variable.")
        sys.exit(1)

    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    data = {"model": "gpt-4o-mini", "messages": messages}
    for attempt in range(retries):
        try:
            response = httpx.post(
                API_ENDPOINT,
                json=data,
                headers=headers,
                timeout=60.0,
            )
            if response.status_code == 401:
                print("Error: Unauthorized access. Check if your AIPROXY_TOKEN is valid.")
                sys.exit(1)

            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except httpx.RequestError as e:
            if attempt < retries - 1:
                print(f"Error: {e}. Retrying ({attempt + 1}/{retries})...")
            else:
                raise Exception(f"Failed after {retries} attempts. Last error: {e}")

# Load dataset
def load_data(file_path):
    print(f"Attempting to load dataset from {file_path}...")
    try:
        data = pd.read_csv(file_path, encoding="latin1")
        print("Dataset loaded successfully.")
        print(f"Dataset shape: {data.shape}")
        return data
    except Exception as e:
        print(f"Error loading dataset: {e}")
        sys.exit(1)

# Perform advanced analysis
def perform_analysis(df):
    print("Performing analysis...")
    summary = df.describe(include="all").to_string()
    missing_values = df.isnull().sum().to_string()

    numeric_cols = df.select_dtypes(include=[np.number])
    correlations = numeric_cols.corr() if not numeric_cols.empty else pd.DataFrame()
    outliers = numeric_cols.apply(lambda x: x[(x - x.mean()).abs() > 3 * x.std()]) if not numeric_cols.empty else pd.DataFrame()
    clusters = cluster_analysis(numeric_cols)

    return summary, missing_values, correlations, outliers, clusters

# Clustering analysis
def cluster_analysis(numeric_cols):
    print("Performing clustering analysis...")
    scaler = numeric_cols.apply(zscore).dropna()

    if scaler.shape[0] == 0:
        print("Warning: No data available for clustering.")
        return None

    kmeans = KMeans(n_clusters=min(3, len(scaler)), random_state=42)
    kmeans.fit(scaler)
    return pd.DataFrame({"Cluster": kmeans.labels_}, index=scaler.index)

# Create visualizations
def create_visualizations(df, correlations, clusters):
    print("Creating visualizations...")
    charts = []

    if not correlations.empty:
        plt.figure(figsize=(12, 8))
        sns.heatmap(correlations, annot=True, cmap="coolwarm", fmt=".2f")
        plt.title("Correlation Heatmap")
        plt.xlabel("Features")
        plt.ylabel("Features")
        heatmap_file = "correlation_heatmap.png"
        plt.savefig(heatmap_file)
        charts.append(heatmap_file)
        plt.close()

    numeric_cols = df.select_dtypes(include=[np.number])
    if not numeric_cols.empty:
        for col in numeric_cols.columns[:10]:
            plt.figure(figsize=(8, 6))
            sns.histplot(numeric_cols[col].dropna(), kde=True, bins=30, color="skyblue")
            plt.title(f"Distribution of {col}")
            plt.xlabel(col)
            plt.ylabel("Frequency")
            hist_file = f"{col}_distribution.png"
            plt.savefig(hist_file)
            charts.append(hist_file)
            plt.close()

        if numeric_cols.shape[1] > 1:
            sns.pairplot(df, vars=numeric_cols.columns[:3], diag_kind="kde")
            pairplot_file = "pairplot.png"
            plt.savefig(pairplot_file)
            charts.append(pairplot_file)
            plt.close()

    if clusters is not None:
        plt.figure(figsize=(8, 6))
        sns.scatterplot(data=clusters, x=clusters.index, y="Cluster", palette="viridis")
        plt.title("KMeans Clustering")
        plt.xlabel("Index")
        plt.ylabel("Cluster Group")
        cluster_file = "kmeans_clusters.png"
        plt.savefig(cluster_file)
        charts.append(cluster_file)
        plt.close()

    return charts

# Generate narrative from analysis
def generate_narrative(file_name, summary, missing_values, correlations, clusters):
    print("Generating narrative from analysis...")
    cluster_summary = clusters.value_counts().to_string() if clusters is not None else "No clustering performed."
    messages = [
        {"role": "system", "content": "You are a data analysis assistant."},
        {"role": "user", "content": f"Analyze the dataset {file_name} and provide insights.\n\nSummary:\n{summary}\n\nMissing Values:\n{missing_values}\n\nCorrelations:\n{correlations.to_string()}\n\nCluster Summary:\n{cluster_summary}"},
    ]
    return query_llm(messages)

# Generate README.md
def save_report(file_name, narrative, charts):
    print("Saving analysis report...")
    with open("README.md", "w") as f:
        f.write(f"# Analysis Report\n\n## Dataset: {file_name}\n\n## Insights\n{narrative}\n\n## Visualizations\n\n")
        for chart in charts:
            f.write(f"![{chart}]({chart})\n")

# Main function
def main():
    if len(sys.argv) != 2:
        print("Usage: uv run autolysis.py <dataset.csv>")
        sys.exit(1)

    file_name = sys.argv[1]
    df = load_data(file_name)

    summary, missing_values, correlations, outliers, clusters = perform_analysis(df)

    charts = create_visualizations(df, correlations, clusters)

    narrative = generate_narrative(file_name, summary, missing_values, correlations, clusters)

    save_report(file_name, narrative, charts)

    print("Analysis complete. Files generated:")
    print("- README.md")
    for chart in charts:
        print(f"- {chart}")

if __name__ == "__main__":
    main()
