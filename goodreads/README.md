# Analysis Report

## Dataset: goodreads.csv

## Insights
Based on the provided dataset summary and analysis, here are some insights regarding the `goodreads.csv` dataset:

### General Overview
- The dataset contains **10,000 records** of books.
- Key features include **book identifiers**, **authors**, **publication year**, **average ratings**, **ratings counts**, and **text reviews**.
- The dataset is fairly comprehensive but has some missing values in specific columns, particularly `isbn`, `isbn13`, `original_publication_year`, and `language_code`, which could impact any analysis performed on these features.

### Key Insights

#### Publication Year
- The **mean publication year** is approximately **1982**, with a range from **-1750** to **2017**. 
  - This suggests that the dataset includes older works as well as contemporary titles, though the majority of the books are likely more recent based on the mean.

#### Ratings
- The **average rating** across all books is approximately **4.00**. 
- Ratings are predominantly in the higher range, indicating that the dataset may largely contain popular or well-received books.
- There is a notable **positive skew** in `ratings_count`, which has a median of approximately **20,000**, while the mean is considerably higher (**50,000**). This indicates a few books receive a disproportionately high number of ratings.

#### Authors
- The top author in the dataset is **Stephen King**, with **60** entries of books authored by him.
- The dataset features a total of **4,664 unique titles**, suggesting a diverse collection of literature.

#### Correlations
- Some significant correlations to note include:
  - There is a moderately strong negative correlation between `work_text_reviews_count` and `average_rating` (-0.419), which might suggest that books with more critical text reviews receive lower average ratings.
  - `ratings_count` and `work_ratings_count` show an exceptionally strong positive correlation (0.995), indicating a consistency in how ratings are aggregated or counted within the original book work context.
  - Surprisingly, there is a negative correlation between `books_count` and `average_rating` (-0.069). More books by an author may not necessarily indicate higher average ratings, hinting at either quality variance or potentially a fan base effect.

#### Missing Values
- **Missing values** are apparent in several fields:
  - **ISBN** numbers are missing for **700** entries.
  - The `original_publication_year` feature has **21** missing values, which can affect age-related analyses of books in the dataset.
  
### Recommendations for Further Analysis
1. **Explore Missing Data**: Address the missing values, possibly by investigating their patterns (e.g., whether missing values are concentrated within certain authors or years).
  
2. **Temporal Analysis**: Analyze trends in average ratings and ratings counts over the years to assess how reader preferences may have evolved.

3. **Comparative Author Analysis**: Focus on comparing ratings of books by popular authors versus lesser-known authors to examine bias or trends in reader ratings.

4. **Clustering**: Although no clustering was performed, segmenting books into categories (e.g., by genre, language, or rating thresholds) could unveil interesting patterns.

5. **Sentiment Analysis**: If reviews are available (potentially via an external dataset), conducting sentiment analysis could provide insights into how textual sentiment correlates with numeric ratings.

By leveraging these insights, more nuanced analyses could be performed to glean further understanding about reader preferences, author performance, and trends in published literature.


## Visualizations

![correlation_heatmap.png](correlation_heatmap.png)
![book_id_distribution.png](book_id_distribution.png)
![goodreads_book_id_distribution.png](goodreads_book_id_distribution.png)
![best_book_id_distribution.png](best_book_id_distribution.png)
![pairplot.png](pairplot.png)
