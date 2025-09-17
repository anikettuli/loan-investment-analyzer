import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from decimal import Decimal, ROUND_HALF_UP

# --- Configuration ---
st.set_page_config(
    layout="wide", page_title="Loan Repayment vs. Investment Growth Analyzer"
)


# --- Financial Calculations ---
def calculate_financials(
    loan_amount,
    loan_rate,
    investment_rate,
    total_monthly_payment,
    monthly_loan_payment,
    years,
):
    """
    Calculates loan, investment, and net worth over time using Decimal for precision.
    """
    # Use Decimal for all monetary values
    loan_amount = Decimal(loan_amount).quantize(Decimal("0.01"))
    total_monthly_payment = Decimal(total_monthly_payment).quantize(Decimal("0.01"))
    monthly_loan_payment = Decimal(monthly_loan_payment).quantize(Decimal("0.01"))

    # Monthly rates as Decimals
    monthly_loan_rate = Decimal(loan_rate) / Decimal(12)
    monthly_investment_rate = Decimal(investment_rate) / Decimal(12)
    total_months = years * 12

    # Initial values
    loan_balance = loan_amount
    investment_balance = Decimal("0.00")
    monthly_investment_payment = total_monthly_payment - monthly_loan_payment

    # Data storage
    data = []
    total_interest_paid = Decimal("0.00")
    total_principal_paid = Decimal("0.00")
    total_invested = Decimal("0.00")

    loan_paid_off = False

    for month in range(1, total_months + 1):
        # --- Update Balances ---
        # Investment
        investment_balance *= Decimal(1) + monthly_investment_rate
        investment_balance += monthly_investment_payment
        total_invested += monthly_investment_payment

        # Loan
        if loan_balance > 0:
            loan_interest = (loan_balance * monthly_loan_rate).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            total_interest_paid += loan_interest

            # Determine payment for this month
            if not loan_paid_off:
                principal_payment = monthly_loan_payment - loan_interest

                # Is the loan paid off this month?
                if loan_balance <= principal_payment:
                    final_principal_payment = loan_balance
                    total_principal_paid += final_principal_payment

                    # Any leftover from the allocated loan payment goes to investments
                    overpayment = monthly_loan_payment - (
                        final_principal_payment + loan_interest
                    )
                    investment_balance += overpayment
                    total_invested += overpayment

                    loan_balance = Decimal("0.00")
                    loan_paid_off = True
                    # After payoff, all funds go to investments
                    monthly_investment_payment = total_monthly_payment
                else:
                    loan_balance -= principal_payment
                    total_principal_paid += principal_payment
            # This else block should not be needed if logic is correct, but as a safeguard
            else:
                monthly_investment_payment = total_monthly_payment

        # Store current state after calculations
        net_worth = investment_balance - loan_balance
        data.append(
            {
                "Month": month,
                "Loan Balance": -float(loan_balance),
                "Investment Portfolio": float(investment_balance),
                "Net Worth": float(net_worth),
            }
        )

    df = pd.DataFrame(data)
    investment_gains = investment_balance - total_invested
    final_net_worth = df["Net Worth"].iloc[-1]

    return (
        df,
        float(total_principal_paid),
        float(total_interest_paid),
        float(total_invested),
        float(investment_gains),
        float(final_net_worth),
    )


def calculate_minimum_loan_payment(loan_amount, loan_rate, years):
    """Calculates the minimum monthly payment for a standard amortized loan."""
    if loan_rate == 0:
        return loan_amount / (years * 12)

    monthly_rate = Decimal(loan_rate) / Decimal(12)
    num_payments = years * 12

    if num_payments == 0:
        return loan_amount

    min_payment = (
        Decimal(loan_amount)
        * (monthly_rate * (1 + monthly_rate) ** num_payments)
        / ((1 + monthly_rate) ** num_payments - 1)
    )
    # Round up to the nearest cent to ensure loan is paid off
    return float(min_payment.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


# --- Streamlit App UI ---
st.markdown(
    """
    <style>
        /* Reduce top padding on main page */
        .reportview-container .main .block-container {
            padding-top: 0rem;
        }
        /* Reduce top padding and gap between elements in sidebar */
        [data-testid="stSidebar"] .block-container {
            padding-top: 1rem;
        }
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
            gap: 0.5rem;
        }
        /* Headings */
        h1 { font-size: 2.5em; }
        h2 { font-size: 2em; }
        h3 { font-size: 1.5em; }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("Loan Repayment vs. Investment Growth Analyzer")

# Financial Inputs
st.sidebar.header("Financial Inputs")
loan_amount = st.sidebar.number_input(
    "Loan Amount", value=500000, step=10000, key="loan_amount"
)
loan_rate = (
    st.sidebar.number_input("Loan Rate (%)", value=5.50, step=0.5, key="loan_rate")
    / 100
)
investment_rate = (
    st.sidebar.number_input(
        "Investment Return Rate (%)", value=8.00, step=0.5, key="investment_rate"
    )
    / 100
)
total_monthly_payment = st.sidebar.number_input(
    "Max Monthly Payment (Loan + Investment)",
    value=4000,
    step=100,
    key="total_monthly_payment",
)
years = st.sidebar.number_input("Years", value=30, step=1, key="years")

# Calculate minimum payment
min_loan_payment = calculate_minimum_loan_payment(loan_amount, loan_rate, years)

# On first load, compute optimal allocation and set slider accordingly
if "loan_payment_slider" not in st.session_state:
    best_net_worth = -np.inf
    sweet_spot_allocation = min_loan_payment
    # Test allocations from minimum to max stepping by $50
    for allocation in np.arange(min_loan_payment, total_monthly_payment + 1, 50):
        _, _, _, _, _, final_net = calculate_financials(
            loan_amount,
            loan_rate,
            investment_rate,
            total_monthly_payment,
            allocation,
            years,
        )
        if final_net > best_net_worth:
            best_net_worth = final_net
            sweet_spot_allocation = allocation
    st.session_state.loan_payment_slider = sweet_spot_allocation

st.sidebar.header("Allocation Strategy")

# --- Optimization Button ---
if st.sidebar.button("Find Optimal Split", key="optimize_button"):
    with st.spinner("Calculating optimal allocation..."):
        best_net_worth = -np.inf
        sweet_spot_allocation = min_loan_payment
        # Iterate from min payment to max possible payment
        for allocation in np.arange(
            min_loan_payment, total_monthly_payment + 1, 50
        ):  # Stepping by $50 for speed
            _, _, _, _, _, final_net_worth = calculate_financials(
                loan_amount,
                loan_rate,
                investment_rate,
                total_monthly_payment,
                allocation,
                years,
            )
            if final_net_worth > best_net_worth:
                best_net_worth = final_net_worth
                sweet_spot_allocation = allocation
    st.session_state.loan_payment_slider = sweet_spot_allocation


# --- Allocation Slider (slider + numeric input, kept in sync) ---
# Ensure legacy/session default exists (from initial optimization run)
if "loan_payment_slider_widget" not in st.session_state:
    init_val = float(st.session_state.get("loan_payment_slider", min_loan_payment))
    st.session_state["loan_payment_slider_widget"] = init_val
    st.session_state["loan_payment_input"] = init_val


def _sync_slider_to_input():
    st.session_state["loan_payment_input"] = st.session_state[
        "loan_payment_slider_widget"
    ]


def _sync_input_to_slider():
    # clamp input into allowed range then sync
    v = st.session_state["loan_payment_input"]
    v = max(float(min_loan_payment), min(float(total_monthly_payment), float(v)))
    st.session_state["loan_payment_input"] = float(round(v, 2))
    st.session_state["loan_payment_slider_widget"] = st.session_state[
        "loan_payment_input"
    ]


# place slider and numeric input side-by-side in the sidebar
col_slider, col_input = st.sidebar.columns([3, 1])
col_label = col_slider.empty()
loan_payment_amount = col_slider.slider(
    "Monthly Loan Payment ($)",
    min_value=float(min_loan_payment),
    max_value=float(total_monthly_payment),
    value=st.session_state["loan_payment_slider_widget"],
    step=50.0,
    key="loan_payment_slider_widget",
    on_change=_sync_slider_to_input,
)
loan_payment_input = col_input.number_input(
    "",
    min_value=float(min_loan_payment),
    max_value=float(total_monthly_payment),
    value=st.session_state["loan_payment_input"],
    step=50.0,
    format="%0.2f",
    key="loan_payment_input",
    on_change=_sync_input_to_slider,
)
# canonical amount used by the rest of the app
loan_payment_amount = float(st.session_state["loan_payment_slider_widget"])


investment_payment_amount = total_monthly_payment - loan_payment_amount
st.sidebar.write(f"**Loan Payment:** ${loan_payment_amount:,.2f}")
st.sidebar.write(f"**Investment:** ${investment_payment_amount:,.2f}")
st.sidebar.info(
    f"Minimum required loan payment is ${min_loan_payment:,.2f} to pay off the loan in {years} years."
)


# --- Main Panel ---
st.header("Financial Projections")

# Calculate data for the selected allocation
(
    df,
    total_principal,
    total_interest,
    total_invested,
    investment_gains,
    final_net_worth,
) = calculate_financials(
    loan_amount,
    loan_rate,
    investment_rate,
    total_monthly_payment,
    loan_payment_amount,
    years,
)

# --- Financial Summary Stats ---
st.subheader("Financial Summary")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Final Net Worth", f"${final_net_worth:,.2f}")
    st.metric("Total Invested", f"${total_invested:,.2f}")
    st.metric(
        "Investment Gains",
        f"${investment_gains:,.2f}",
        help="Total value of the investment portfolio minus the total cash invested.",
    )
with col2:
    st.metric("Total Principal Paid", f"${total_principal:,.2f}")
    st.metric(
        "Total Interest Paid",
        f"${total_interest:,.2f}",
        help="The total cost of borrowing the money.",
    )
with col3:
    # Correctly find the first month the loan is paid off
    paid_off_months = df[df["Loan Balance"] == 0]
    if not paid_off_months.empty:
        loan_payoff_month = paid_off_months["Month"].min()
        # If paid off on the very last month, consider it "On Time"
        if loan_payoff_month == years * 12:
            st.metric("Loan Payoff Time", "On Time")
        else:
            st.metric("Loan Payoff Time", f"{loan_payoff_month / 12:.1f} years")
    # Check if the final balance is effectively zero
    elif abs(df["Loan Balance"].iloc[-1]) < 1:
        st.metric("Loan Payoff Time", "On Time")
    else:
        st.metric("Loan Payoff Time", "Not Paid Off")


# --- Chart ---
st.subheader("Interactive Financial Journey")
fig = px.line(
    df,
    x="Month",
    y=["Loan Balance", "Investment Portfolio", "Net Worth"],
    title="Loan, Investment, and Net Worth Over Time",
    labels={"value": "Amount ($)", "variable": "Metric"},
)
fig.update_layout(
    legend_title_text="Metrics",
    xaxis_title="Month",
    yaxis_title="Amount ($)",
    hovermode="x unified",
)
st.plotly_chart(fig, use_container_width=True)

# --- Data Table ---
st.subheader("Yearly Data Summary")
st.write("View the numbers at the end of each year.")
# Ensure we have data for every year, even if the simulation is short
display_years = list(range(1, years + 1))
yearly_summary = df[df["Month"] % 12 == 0].copy()
yearly_summary["Year"] = yearly_summary["Month"] // 12

# If the loan is paid off early, the last entry might not be a full year. Add it.
if not df.empty and df.iloc[-1]["Month"] % 12 != 0:
    last_row = df.iloc[[-1]].copy()
    last_row["Year"] = np.ceil(last_row["Month"] / 12)
    yearly_summary = pd.concat([yearly_summary, last_row]).drop_duplicates(
        subset="Year", keep="last"
    )

yearly_summary = yearly_summary[
    ["Year", "Loan Balance", "Investment Portfolio", "Net Worth"]
].sort_values("Year")
st.dataframe(
    yearly_summary.style.format(
        {
            "Loan Balance": "${:,.2f}",
            "Investment Portfolio": "${:,.2f}",
            "Net Worth": "${:,.2f}",
        }
    )
)
