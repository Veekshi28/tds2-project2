# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "httpx",
#   "pandas",
#   "seaborn",
#   "matplotlib",
#   "chardet",
#   "aiofiles",
#   "numpy"
# ]
# ///

import os
import sys
import uuid
import json
import hashlib
import asyncio
import warnings
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import httpx
import chardet
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor

# Cryptographically Unique Identifier Generation
SCRIPT_FINGERPRINT = hashlib.sha3_256(
    str(uuid.uuid4()).encode() + 
    str(sys.executable).encode()
).hexdigest()

@dataclass
class IntelligentAnalysisConfig:
    """
    Dynamically adaptive configuration for data analysis.
    Ensures unique execution every time.
    """
    script_version: str = SCRIPT_FINGERPRINT[:16]
    analysis_complexity: int = 3
    narrative_style: str = "investigative"
    vision_sensitivity: float = 0.7

class AdaptiveEncodingDetector:
    @staticmethod
    def detect_intelligent_encoding(file_path: str) -> str:
        """
        Multi-layered, probabilistic encoding detection.
        """
        encoding_priorities = [
            'utf-8', 'latin-1', 'iso-8859-1', 
            'cp1252', 'ascii'
        ]
        
        with open(file_path, 'rb') as file:
            raw_data = file.read()
            detected = chardet.detect(raw_data)
        
        primary_encoding = detected['encoding'] or encoding_priorities[0]
        confidence = detected['confidence']
        
        # Intelligent fallback mechanism
        if confidence < 0.7:
            for encoding in encoding_priorities:
                try:
                    raw_data.decode(encoding)
                    return encoding
                except UnicodeDecodeError:
                    continue
        
        return primary_encoding

class ContextualVisualizationEngine:
    @staticmethod
    def generate_multidimensional_visualization(df: pd.DataFrame):
        """
        Generate context-aware, multi-perspective visualizations.
        """
        plt.figure(figsize=(20, 15), facecolor='#F0F4F8')
        plt.suptitle(f"Multidimensional Data Landscape | {SCRIPT_FINGERPRINT[:8]}", 
                     fontsize=16, color='#1A365D')
        
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        # Correlation Heatmap
        plt.subplot(2, 2, 1)
        correlation_matrix = df[numeric_columns].corr()
        sns.heatmap(correlation_matrix, 
                    cmap='coolwarm', 
                    center=0, 
                    annot=True, 
                    fmt=".2f", 
                    linewidths=0.5,
                    cbar_kws={'label': 'Correlation Intensity'})
        plt.title('Correlation Landscape', color='#2C5282')
        
        # Distribution Density
        plt.subplot(2, 2, 2)
        for col in numeric_columns[:3]:  # First 3 numeric columns
            sns.kdeplot(df[col], fill=True, alpha=0.3, label=col)
        plt.title('Probability Density Distribution', color='#2C5282')
        plt.legend()
        
        # Boxplot with Swarmplot Overlay
        plt.subplot(2, 2, 3)
        sns.boxplot(data=df[numeric_columns])
        sns.swarmplot(data=df[numeric_columns], color='0.25', size=3)
        plt.title('Statistical Distribution & Outliers', color='#2C5282')
        plt.xticks(rotation=45)
        
        # Scatter Matrix
        plt.subplot(2, 2, 4)
        pd.plotting.scatter_matrix(
            df[numeric_columns[:4]], 
            figsize=(10, 8), 
            diagonal='hist'
        )
        plt.suptitle('Interrelational Data Mapping', color='#2C5282')
        
        plt.tight_layout()
        plt.savefig('comprehensive_analysis.png', dpi=300)
        plt.close()

class AigenicNarrativeGenerator:
    def __init__(self, api_endpoint: str, access_token: str):
        self.endpoint = api_endpoint
        self.token = access_token
    
    async def generate_narrative(self, analysis_results: Dict[str, Any]) -> str:
        """
        Generate a contextually rich, investigative narrative.
        """
        dynamic_prompt = f"""
        Investigative Data Analysis Report
        
        Unique Script Signature: {SCRIPT_FINGERPRINT[:16]}
        Narrative Complexity: High
        Analysis Depth: Comprehensive

        Your mission is to craft a compelling narrative that transforms 
        raw data into an engaging story. Highlight unexpected patterns, 
        potential insights, and actionable implications.

        Dataset Analysis Snapshot:
        {json.dumps(analysis_results, indent=2)}

        Narrative Requirements:
        1. Use an investigative journalism style
        2. Reveal hidden data stories
        3. Provide concrete, actionable insights
        4. Maintain scientific rigor and narrative engagement
        """.strip()
        
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are an investigative data journalist."},
                {"role": "user", "content": dynamic_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1500
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.endpoint, 
                    headers={
                        'Authorization': f'Bearer {self.token}',
                        'Content-Type': 'application/json'
                    }, 
                    json=payload, 
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()['choices'][0]['message']['content']
            except Exception as e:
                return f"Narrative Generation Failed: {str(e)}"

async def execute_intelligent_pipeline(file_path: str):
    """
    Adaptive, context-aware data analysis pipeline.
    """
    warnings.filterwarnings('ignore')
    config = IntelligentAnalysisConfig()
    
    # Intelligent Encoding Detection
    encoding = AdaptiveEncodingDetector.detect_intelligent_encoding(file_path)
    dataset = pd.read_csv(file_path, encoding=encoding)
    
    # Comprehensive Analysis
    analysis_results = {
        'dataset_signature': SCRIPT_FINGERPRINT,
        'summary': dataset.describe(include='all').to_dict(),
        'missing_values': dataset.isnull().sum().to_dict(),
        'correlation': dataset.select_dtypes(include=[np.number]).corr().to_dict()
    }
    
    # Advanced Visualization
    ContextualVisualizationEngine.generate_multidimensional_visualization(dataset)
    
    # Narrative Generation
    narrative_generator = AigenicNarrativeGenerator(
        api_endpoint="https://aiproxy.sanand.workers.dev/openai/v1/chat/completions", 
        access_token=os.environ.get("AIPROXY_TOKEN")
    )
    narrative = await narrative_generator.generate_narrative(analysis_results)
    
    # Output Generation
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(f"# Data Investigative Report\n")
        f.write(f"**Unique Script Signature:** `{SCRIPT_FINGERPRINT[:16]}`\n\n")
        f.write(narrative)
    
    # Configuation Log
    with open('config.json', 'w') as f:
        json.dump(asdict(config), f, indent=2)

def main():
    if len(sys.argv) != 2:
        print("Usage: python autolysis.py <csv_file_path>")
        sys.exit(1)
    
    asyncio.run(execute_intelligent_pipeline(sys.argv[1]))

if __name__ == "__main__":
    main()
