# Loan Repayment vs. Investment Growth Analyzer

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://loan-investment-analyzer.streamlit.app/)

This interactive web application, built with Python and Streamlit, helps you visualize and determine the optimal strategy for allocating your money between paying off a loan and investing. By adjusting your monthly payments, you can find the "sweet spot" that maximizes your net worth over time.

## Why This Is Important

Deciding how to best use your money can be challenging. Should you aggressively pay down debt to save on interest, or should you invest to take advantage of market returns? This tool helps answer that question by simulating your financial future based on your personal financial situation. It provides a clear, data-driven approach to making one of the most critical financial decisions.

The key challenge is balancing two competing financial goals:
1.  **Paying off a loan:** Reduces debt and saves you money on interest payments.
2.  **Investing:** Grows your wealth through compound returns.

This application helps you find the optimal balance between these two goals to maximize your final net worth.

## How to Use the App

The application is designed to be intuitive and easy to use.

### 1. Financial Inputs (Sidebar)
On the left sidebar, you will find the following input fields:
*   **Loan Amount:** The total amount of your loan.
*   **Loan Rate (%):** The annual interest rate of your loan.
*   **Investment Return Rate (%):** Your expected annual return on investment.
*   **Max Monthly Payment:** The total amount you can afford to put towards your loan and investments each month.
*   **Years:** The time horizon for your financial plan.

### 2. Allocation Strategy (Sidebar)
*   **Monthly Loan Payment Slider:** This is the core interactive element. Use this slider to adjust how much of your `Max Monthly Payment` goes towards your loan. The remainder will be automatically allocated to your investments. The slider's minimum value is set to the amount required to pay off the loan within the specified number of years.
*   **Find Optimal Split Button:** Not sure where to start? Click this button, and the app will automatically calculate the best allocation for you and set the slider to that value.

### 3. Understanding the Output (Main Panel)
*   **Financial Summary:** This section provides a snapshot of your financial future based on the current slider setting, including your final net worth, total interest paid, investment gains, and the estimated time to pay off your loan.
*   **Interactive Financial Journey:** This graph visualizes your financial progress over time. You can see how your loan balance decreases, your investment portfolio grows, and your net worth increases.
*   **Yearly Data Summary:** A table that provides a year-by-year breakdown of your financial situation.

## How It Was Built

This application was built using the following technologies:
*   **Python:** The core programming language.
*   **Streamlit:** For creating the interactive web application and user interface.
*   **Pandas:** For data manipulation and analysis.
*   **NumPy:** For numerical calculations.
*   **Plotly:** For creating the interactive charts and graphs.

## How to Run It Locally

To run this application on your local machine, follow these steps:

1.  **Clone the repository or download the files.**

2.  **Create a Python virtual environment.** It's recommended to use a virtual environment to keep the project's dependencies separate.
    ```bash
    python -m venv .venv
    ```

3.  **Activate the virtual environment.**
    *   On Windows:
        ```bash
        .venv\Scripts\activate
        ```
    *   On macOS/Linux:
        ```bash
        source .venv/bin/activate
        ```

4.  **Install the required packages.**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Run the Streamlit application.**
    ```bash
    streamlit run loan_vs_investment_app.py
    ```

The application will open in a new tab in your web browser.
