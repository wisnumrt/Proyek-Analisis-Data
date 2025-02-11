import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Function to load data
def load_data():
    try:
        order_items_df = pd.read_csv('dashboard/order_items.csv')
        products_df = pd.read_csv('dashboard/products_items.csv')
        orders_df = pd.read_csv('dashboard/orders.csv')
        product_category_df = pd.read_csv('dashboard/product_category.csv')
        order_review_df = pd.read_csv('dashboard/order_review.csv')
        customers_df = pd.read_csv('dashboard/customers.csv')
        sellers_df = pd.read_csv('dashboard/sellers.csv')

        return order_items_df, products_df, orders_df, product_category_df, order_review_df, customers_df, sellers_df
    except FileNotFoundError as e:
        st.error(f"File not found: {e.filename}. Please make sure all CSV files are present in the same directory as this script.")
        return None, None, None, None, None, None, None

# Load data
order_items_df, products_df, orders_df, product_category_df, order_review_df, customers_df, sellers_df = load_data()

# Check if all data is loaded before displaying anything
if order_items_df is not None and products_df is not None and orders_df is not None:
    # Streamlit app
    st.title('E-commerce Dashboard')

    # Sidebar
    st.sidebar.header('Navigation')
    page = st.sidebar.radio('Go to', ['Top 5 Product Categories', 'Customer Satisfaction', 'Geographic Distribution', 'Top 5 Sellers'])

    if page == 'Top 5 Product Categories':
        st.header('Top 5 Product Categories Performance')

        # Data preparation
        merged_df = pd.merge(order_items_df, products_df, on='product_id')
        merged_df = pd.merge(merged_df, orders_df[['order_id', 'order_purchase_timestamp']], on='order_id')
        merged_df = pd.merge(merged_df, product_category_df, on='product_category_name')

        merged_df['year'] = pd.to_datetime(merged_df['order_purchase_timestamp']).dt.year
        category_sales = merged_df.groupby(['product_category_name_english', 'year'])['price'].sum().reset_index()

        top_5_categories = category_sales.groupby('product_category_name_english')['price'].sum().nlargest(5).index
        top_5_sales = category_sales[category_sales['product_category_name_english'].isin(top_5_categories)]

        # Visualization
        fig, ax = plt.subplots(figsize=(12, 6))
        for category in top_5_categories:
            data = top_5_sales[top_5_sales['product_category_name_english'] == category]
            ax.plot(data['year'], data['price'], marker='o', label=category)

        ax.set_title('Performance of Top 5 Product Categories')
        ax.set_xlabel('Year')
        ax.set_ylabel('Total Sales')
        ax.legend()
        ax.grid(True)

        years = sorted(top_5_sales['year'].unique())
        ax.set_xticks(years)

        st.pyplot(fig)

        st.write("Top 5 Product Categories:")
        st.write(top_5_categories.tolist())

    elif page == 'Customer Satisfaction':
        st.header('Customer Satisfaction Trends')

        # Data preparation
        merged_df = pd.merge(order_review_df, orders_df[['order_id', 'order_purchase_timestamp']], on='order_id')
        merged_df['year'] = pd.to_datetime(merged_df['order_purchase_timestamp']).dt.year

        satisfaction_data = merged_df.groupby(['year', 'review_score']).size().unstack()
        satisfaction_percentage = satisfaction_data.divide(satisfaction_data.sum(axis=1), axis=0) * 100

        # Visualization
        fig, ax = plt.subplots(figsize=(14, 6))
        satisfaction_percentage.plot(kind='bar', stacked=False, ax=ax)
        ax.set_title('Customer Satisfaction Percentage by Review Score')
        ax.set_xlabel('Year')
        ax.set_ylabel('Percentage')
        ax.legend(title='Review Score', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()

        for c in ax.containers:
            ax.bar_label(c, fmt='%.2f%%', label_type='edge')

        st.pyplot(fig)

    elif page == 'Geographic Distribution':
        st.header('Geographic Distribution of Customers')

        # Data preparation
        state_distribution = customers_df['customer_state'].value_counts()

        # Visualization
        fig, ax = plt.subplots(figsize=(12, 6))
        state_distribution.plot(kind='bar', ax=ax)
        ax.set_title('Customer Distribution by State')
        ax.set_xlabel('State')
        ax.set_ylabel('Number of Customers')
        plt.xticks(rotation=45)
        plt.tight_layout()

        st.pyplot(fig)

        st.write("Top 5 States with Most Customers:")
        st.write(state_distribution.head())

    elif page == 'Top 5 Sellers':
        st.header('Top 5 Sellers Performance')

        # Data preparation
        seller_performance = order_items_df.groupby('seller_id').agg({
            'order_id': 'count',
            'price': 'sum'
        }).rename(columns={'order_id': 'total_sales', 'price': 'total_revenue'})

        top_5_sellers = seller_performance.sort_values('total_sales', ascending=False).head()

        # Visualization
        fig, ax1 = plt.subplots(figsize=(14, 8))
        pos = np.arange(len(top_5_sellers.index))
        width = 0.35

        sales_bars = ax1.bar(pos - width/2, top_5_sellers['total_sales'], width, label='Total Sales', color='#3498db')
        ax1.set_ylabel('Total Sales', color='#2980b9')
        ax1.tick_params(axis='y', labelcolor='#2980b9')

        ax2 = ax1.twinx()
        revenue_bars = ax2.bar(pos + width/2, top_5_sellers['total_revenue'], width, label='Total Revenue', color='#008000')
        ax2.set_ylabel('Total Revenue ($)', color='#008000')
        ax2.tick_params(axis='y', labelcolor='#008000')

        ax1.set_xticks(pos)
        ax1.set_xticklabels(top_5_sellers.index, rotation=45, ha='right')

        def add_value_labels(bars, ax):
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:,.0f}',
                        ha='center', va='bottom', fontweight='bold')

        add_value_labels(sales_bars, ax1)
        add_value_labels(revenue_bars, ax2)

        plt.title('Top 5 Sellers by Total Sales', fontsize=16, fontweight='bold')
        plt.subplots_adjust(bottom=0.2)

        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        fig.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=12)

        st.pyplot(fig)

else:
    st.warning("Please make sure all required CSV files are available.")
