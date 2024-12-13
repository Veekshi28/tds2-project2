# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pandas",
#     "matplotlib",
#     "seaborn",
#     "openai",
#     "httpx",
#     "numpy"
# ]
# ///

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import httpx
import openai

# Ensure AIPROXY_TOKEN is available
def get_ai_proxy_token():
    token = os.environ.get("AIPROXY_TOKEN")
    if not token:
        raise EnvironmentError("AI Proxy Token is required but not provided. Please set it as an environment variable.")
    return token

AIPROXY_TOKEN = get_ai_proxy_token()
openai.api_base = "https://aiproxy.sanand.workers.dev/openai/v1"
openai.api_key = AIPROXY_TOKEN

# Retry logic for API calls
def query_llm(messages, retries=3):
    headers = {"Authorization": f"Bearer {AIPROXY_TOKEN}"}
    data = {"model": "gpt-4o-mini", "messages": messages}
    for attempt in range(retries):
        try:
            response = httpx.post(
                f"{openai.api_base}/chat/completions",
                json=data,
                headers=headers,
                timeout=60.0,
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except httpx.RequestError as e:
            if attempt < retries - 1:
                print(f"Error: {e}. Retrying ({attempt + 1}/{retries})...")
            else:
                raise

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
    summary = df.describe(include="all").to_string()
    missing_values = df.isnull().sum().to_string()
    correlations = df.corr()
    outliers = df.select_dtypes(include=[np.number]).apply(lambda x: x[(x - x.mean()).abs() > 3 * x.std()])
    return summary, missing_values, correlations, outliers

# Create visualizations
def create_visualizations(df, correlations):
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
        for col in numeric_cols.columns[:3]:
            plt.figure(figsize=(8, 6))
            sns.histplot(numeric_cols[col].dropna(), kde=True, bins=30, color="skyblue")
            plt.title(f"Distribution of {col}")
            plt.xlabel(col)
            plt.ylabel("Frequency")
            hist_file = f"{col}_distribution.png"
            plt.savefig(hist_file)
            charts.append(hist_file)
            plt.close()

    return charts

# Generate narrative from analysis
def generate_narrative(file_name, summary, missing_values, correlations):
    messages = [
        {"role": "system", "content": "You are a data analysis assistant."},
        {"role": "user", "content": f"Analyze the dataset {file_name} and provide insights.\n\nSummary:\n{summary}\n\nMissing Values:\n{missing_values}\n\nCorrelations:\n{correlations.to_string()}"},
    ]
    return query_llm(messages)

# Generate README.md
def save_report(file_name, narrative, charts):
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

    summary, missing_values, correlations, outliers = perform_analysis(df)

    charts = create_visualizations(df, correlations)

    narrative = generate_narrative(file_name, summary, missing_values, correlations)

    save_report(file_name, narrative, charts)

    print("Analysis complete. Files generated:")
    print("- README.md")
    for chart in charts:
        print(f"- {chart}")

if __name__ == "__main__":
    main()
