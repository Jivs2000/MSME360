#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- Page Configuration ---
st.set_page_config(
    page_title="Advanced Loan Amortization Calculator",
    layout="wide", # Set layout to wide for landscape view
    initial_sidebar_state="expanded"
)

# --- Custom CSS for better aesthetics ---
st.markdown("""
    <style>
        /* General styling for the app */
        .stApp {
            background-color: #f0f2f6; /* Light gray background */
            color: #333333; /* Darker text */
        }
        /* Header styling */
        h1, h2, h3 {
            color: #1a73e8; /* Google Blue */
        }
        /* Buttons styling */
        .stButton>button {
            background-color: #4285f4; /* Google Blue */
            color: white;
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 16px;
            border: none;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #357ae8; /* Darker blue on hover */
            box-shadow: 3px 3px 8px rgba(0,0,0,0.3);
            transform: translateY(-2px);
        }
        /* Input fields styling */
        .stTextInput>div>div>input {
            border-radius: 8px;
            border: 1px solid #ccc;
            padding: 8px 12px;
        }
        .stNumberInput>div>div>input {
            border-radius: 8px;
            border: 1px solid #ccc;
            padding: 8px 12px;
        }
        /* Expander styling */
        .streamlit-expanderHeader {
            background-color: #e8f0fe; /* Light blue for expander header */
            border-radius: 8px;
            padding: 10px;
            font-weight: bold;
            color: #1a73e8;
        }
        /* Metrics styling */
        [data-testid="stMetric"] {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            margin-bottom: 15px;
        }
        [data-testid="stMetricLabel"] {
            font-size: 1.1em;
            color: #555555;
        }
        [data-testid="stMetricValue"] {
            font-size: 1.8em;
            font-weight: bold;
            color: #1a73e8;
        }
        /* Table styling */
        .dataframe {
            font-size: 0.9em;
        }
    </style>
""", unsafe_allow_html=True)

# --- Title and Description ---
st.title("🏡 Advanced Loan Amortization Calculator")
st.write("Calculate your loan payments, generate a detailed amortization schedule, and visualize your repayment journey.")

# --- Input Section (Sidebar for better organization) ---
st.sidebar.header("Loan Details")

principal = st.sidebar.number_input("Principal Amount ($)", min_value=1000.0, value=200000.0, step=1000.0)
annual_rate = st.sidebar.number_input("Annual Interest Rate (%)", min_value=0.01, value=4.5, step=0.01)
term_years = st.sidebar.number_input("Loan Term (Years)", min_value=1, value=30, step=1)
extra_payment = st.sidebar.number_input("Optional: Extra Monthly Payment ($)", min_value=0.0, value=0.0, step=10.0)

calculate_button = st.sidebar.button("Calculate Amortization")

# --- Calculation Logic ---
if calculate_button:
    if principal <= 0 or annual_rate < 0 or term_years <= 0:
        st.error("Please enter positive values for Principal, Rate, and Term.")
    else:
        # Convert annual rate to monthly rate and term to months
        monthly_rate = (annual_rate / 100) / 12
        term_months = term_years * 12

        # Calculate monthly payment using the loan amortization formula
        if monthly_rate == 0: # Handle zero interest rate case
            monthly_payment_base = principal / term_months
        else:
            monthly_payment_base = principal * (monthly_rate * (1 + monthly_rate)**term_months) / ((1 + monthly_rate)**term_months - 1)

        # Total monthly payment including extra payment
        total_monthly_payment = monthly_payment_base + extra_payment

        st.subheader("Summary")

        # --- Summary Metrics ---
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Base Monthly Payment", f"${monthly_payment_base:,.2f}")
        col2.metric("Total Monthly Payment", f"${total_monthly_payment:,.2f}")

        # --- Amortization Schedule Generation ---
        schedule_data = []
        remaining_balance = principal
        total_interest_paid = 0
        total_principal_paid = 0
        payment_number = 0

        while remaining_balance > 0.01 and payment_number < term_months * 2: # Add a safety break for very long loans with small extra payments
            payment_number += 1
            interest_for_period = remaining_balance * monthly_rate
            principal_for_period = total_monthly_payment - interest_for_period

            # Adjust last payment to not overpay
            if remaining_balance < principal_for_period:
                principal_for_period = remaining_balance
                total_monthly_payment = principal_for_period + interest_for_period # Adjust last payment amount
                remaining_balance = 0
            else:
                remaining_balance -= principal_for_period

            total_interest_paid += interest_for_period
            total_principal_paid += principal_for_period

            schedule_data.append({
                "Payment No.": payment_number,
                "Payment Amount": total_monthly_payment,
                "Principal Paid": principal_for_period,
                "Interest Paid": interest_for_period,
                "Remaining Balance": remaining_balance
            })

        df_schedule = pd.DataFrame(schedule_data)

        col3.metric("Total Interest Paid", f"${total_interest_paid:,.2f}")
        col4.metric("Loan Duration (Months)", f"{payment_number}")

        # --- Visualizations Section ---
        st.subheader("Visualizations")

        # Plot 1: Principal vs. Interest Paid Over Time
        fig_payments = px.line(df_schedule, x="Payment No.", y=["Principal Paid", "Interest Paid"],
                               title="Principal vs. Interest Paid Over Time",
                               labels={"value": "Amount ($)", "variable": "Component"},
                               hover_data={"Payment No.": True, "value": ":,.2f", "variable": True})
        fig_payments.update_layout(hovermode="x unified")
        st.plotly_chart(fig_payments, use_container_width=True)

        # Plot 2: Remaining Balance Over Time
        fig_balance = px.area(df_schedule, x="Payment No.", y="Remaining Balance",
                              title="Remaining Loan Balance Over Time",
                              labels={"Remaining Balance": "Balance ($)"},
                              line_shape="spline",
                              hover_data={"Payment No.": True, "Remaining Balance": ":,.2f"})
        fig_balance.update_layout(hovermode="x unified")
        st.plotly_chart(fig_balance, use_container_width=True)

        # --- Amortization Schedule Section (Expandable) ---
        with st.expander("View Full Amortization Schedule"):
            st.dataframe(df_schedule.style.format({
                "Payment Amount": "${:,.2f}",
                "Principal Paid": "${:,.2f}",
                "Interest Paid": "${:,.2f}",
                "Remaining Balance": "${:,.2f}"
            }), use_container_width=True)

else:
    st.info("Enter loan details in the sidebar and click 'Calculate Amortization' to generate the schedule.")

