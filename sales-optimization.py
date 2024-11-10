import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
import requests
from io import StringIO

class SalesOptimizer:
    def __init__(self):
        self.data = None
        self.summary = None
        self.load_real_data()
        
    def load_real_data(self):
        """
        Loads real sales data from Berkeley's public dataset
        Source: Berkeley Prices and Promotions Database
        """
        # Using Berkeley's public retail dataset
        url = "https://raw.githubusercontent.com/berkeleydb/berkeley-db-price/main/sample_data.csv"
        response = requests.get(url)
        data = StringIO(response.text)
        
        self.data = pd.read_csv(data)
        self.data['date'] = pd.to_datetime(self.data['week'], format='%Y%m%d')
        self.clean_data()
    
    def clean_data(self):
        """Cleans and preprocesses the data"""
        # Remove any duplicates
        self.data = self.data.drop_duplicates()
        
        # Calculate key metrics
        self.data['revenue'] = self.data['price'] * self.data['units']
        self.data['profit'] = self.data['revenue'] - (self.data['units'] * self.data['base_price'])
        
        # Create customer segments based on purchase frequency
        customer_frequency = self.data.groupby('store')['units'].sum()
        self.data['customer_segment'] = self.data['store'].map(
            pd.qcut(customer_frequency, q=3, labels=['Low', 'Medium', 'High']).to_dict()
        )

    def analyze_sales_trends(self):
        """Analyzes sales trends and generates insights"""
        # Weekly sales trends
        weekly_sales = self.data.groupby('date').agg({
            'revenue': 'sum',
            'units': 'sum',
            'profit': 'sum'
        }).reset_index()
        
        # Customer segment analysis
        segment_analysis = self.data.groupby('customer_segment').agg({
            'revenue': 'sum',
            'units': 'sum',
            'profit': 'mean'
        }).round(2)
        
        # Promotion effectiveness
        promo_analysis = self.data.groupby('featured').agg({
            'units': 'mean',
            'revenue': 'mean',
            'profit': 'mean'
        }).round(2)
        
        self.summary = {
            'weekly_sales': weekly_sales,
            'segment_analysis': segment_analysis,
            'promo_analysis': promo_analysis
        }
        
        return self.summary

    def generate_visualizations(self):
        """Generates visualization reports"""
        if not self.summary:
            self.analyze_sales_trends()
            
        # Create output directory
        Path("reports").mkdir(exist_ok=True)
        
        # Sales Trend Plot
        plt.figure(figsize=(12, 6))
        sns.lineplot(data=self.summary['weekly_sales'], x='date', y='revenue')
        plt.title('Weekly Sales Trend')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('reports/sales_trend.png')
        plt.close()
        
        # Customer Segment Analysis
        plt.figure(figsize=(10, 6))
        self.summary['segment_analysis']['revenue'].plot(kind='bar')
        plt.title('Revenue by Customer Segment')
        plt.tight_layout()
        plt.savefig('reports/segment_analysis.png')
        plt.close()
        
        # Promotion Effectiveness
        plt.figure(figsize=(10, 6))
        self.summary['promo_analysis']['units'].plot(kind='bar')
        plt.title('Average Units Sold by Promotion Status')
        plt.tight_layout()
        plt.savefig('reports/promo_effectiveness.png')
        plt.close()

    def generate_report(self):
        """Generates a comprehensive analysis report"""
        if not self.summary:
            self.analyze_sales_trends()
            
        report = f"""
Sales Optimization Analysis Report
Generated on: {datetime.now().strftime('%Y-%m-%d')}

1. Overall Performance Metrics:
   - Total Revenue: ${self.data['revenue'].sum():,.2f}
   - Total Units Sold: {self.data['units'].sum():,}
   - Average Profit per Sale: ${self.data['profit'].mean():.2f}

2. Customer Segment Analysis:
{self.summary['segment_analysis'].to_string()}

3. Promotion Effectiveness:
{self.summary['promo_analysis'].to_string()}

4. Key Insights:
   - Most valuable customer segment: {self.summary['segment_analysis']['revenue'].idxmax()}
   - Promotional effectiveness: {
    'Positive' if self.summary['promo_analysis'].loc[1, 'profit'] > 
    self.summary['promo_analysis'].loc[0, 'profit'] else 'Negative'
   } impact on profits
   
5. Recommendations:
   - Focus on {self.summary['segment_analysis']['revenue'].idxmax()} segment for immediate revenue
   - {'Increase' if self.summary['promo_analysis'].loc[1, 'profit'] > 
      self.summary['promo_analysis'].loc[0, 'profit'] else 'Decrease'} promotional activities
   
Visualizations have been saved in the 'reports' directory.
"""
        
        # Save report
        with open('reports/analysis_report.txt', 'w') as f:
            f.write(report)
        
        return report

if __name__ == "__main__":
    # Initialize and run the analysis
    optimizer = SalesOptimizer()
    optimizer.analyze_sales_trends()
    optimizer.generate_visualizations()
    report = optimizer.generate_report()
    print("Analysis complete! Check the 'reports' directory for results.")
