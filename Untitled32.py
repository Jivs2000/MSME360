#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import datetime
import json
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="MSME ERP System",
    page_icon="💼",
    layout="wide"
)

# --- Data Persistence Functions ---
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def load_user_data(username):
    """Loads a user's data from a JSON file."""
    filepath = os.path.join(DATA_DIR, f"{username}.json")
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {} # Return an empty dict if file is corrupted
    return {}

def save_user_data(username, data):
    """Saves a user's data to a JSON file."""
    filepath = os.path.join(DATA_DIR, f"{username}.json")
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4, default=str)

# --- Session State Initialization ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None

# --- Login Logic ---
def login_form():
    st.title("Welcome to the MSME ERP System")
    st.info("Please log in to continue. Use any username to create a new profile.")

    with st.form("login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")

        if submit_button:
            if username and password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Logged in as {username}!")
                st.rerun()
            else:
                st.error("Please enter both username and password.")

# --- Main Application Logic ---
if not st.session_state.logged_in:
    login_form()
else:
    # --- Corrected Data Loading ---
    st.session_state['products'] = user_data.get('products', {})
st.session_state['customers'] = user_data.get('customers', {})
st.session_state['suppliers'] = user_data.get('suppliers', {})
st.session_state['sales_orders'] = user_data.get('sales_orders', [])
st.session_state['purchase_orders'] = user_data.get('purchase_orders', [])

# --- Logout Function ---
    def logout():
        # Save current session data before logging out
        data_to_save = {
            'products': st.session_state.products,
            'customers': st.session_state.customers,
            'suppliers': st.session_state.suppliers,
            'sales_orders': st.session_state.sales_orders,
            'purchase_orders': st.session_state.purchase_orders
        }
        save_user_data(st.session_state.username, data_to_save)
        
        # Clear session state for next login
        for key in list(st.session_state.keys()):
            del st.session_state[key]
            
        st.info("Logged out successfully.")
        st.rerun()

    # --- Helper Functions (inside the main app loop) ---
    def get_next_id(prefix, data_dict):
        """Generates a new ID based on a prefix and existing data."""
        if not data_dict:
            return f"{prefix}001"
        last_id_num = max([int(k[len(prefix):]) for k in data_dict.keys()])
        new_id_num = last_id_num + 1
        return f"{prefix}{new_id_num:03d}"

    def get_next_order_id(prefix, data_list):
        """Generates a new order ID."""
        if not data_list:
            return f"{prefix}001"
        last_id_num = max([int(item['id'][len(prefix):]) for item in data_list])
        new_id_num = last_id_num + 1
        return f"{prefix}{new_id_num:03d}"

    # --- Sidebar Navigation ---
    st.sidebar.title(f"Welcome, {st.session_state.username} 👋")
    page = st.sidebar.radio(
        "Go to",
        ["Dashboard", "Inventory", "Sales", "Purchases", "Customers", "Suppliers", "Financial Health", "Business Expansion"]
    )
    st.sidebar.button("Logout", on_click=logout)

    # --- Main App ---

    # --- Dashboard Module ---
    if page == "Dashboard":
        st.title("Dashboard 📈")
        st.header("Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        total_products = len(st.session_state.products)
        col1.metric("Total Products", total_products)
        total_sales = sum(item['total_amount'] for item in st.session_state.sales_orders)
        col2.metric("Total Sales Value", f"₹{total_sales:,.2f}")
        total_customers = len(st.session_state.customers)
        col3.metric("Total Customers", total_customers)
        low_stock_items = [p for p in st.session_state.products.values() if p['stock'] < p['reorder_level']]
        col4.metric("Low Stock Items", len(low_stock_items))
        if st.session_state.sales_orders:
            st.header("Sales Trend")
            sales_df = pd.DataFrame(st.session_state.sales_orders)
            sales_df['date'] = pd.to_datetime(sales_df['date'])
            sales_by_date = sales_df.groupby(sales_df['date'].dt.date)['total_amount'].sum().reset_index()
            sales_by_date.rename(columns={'date': 'Date', 'total_amount': 'Total Sales'}, inplace=True)
            st.line_chart(sales_by_date.set_index('Date'))
        
    # --- Inventory Module ---
    elif page == "Inventory":
        st.title("Inventory Management 📦")
        with st.expander("➕ Add New Product"):
            with st.form("new_product_form", clear_on_submit=True):
                product_name = st.text_input("Product Name", placeholder="Laptop Pro")
                description = st.text_area("Description", placeholder="15-inch screen, 8GB RAM")
                unit_price = st.number_input("Unit Price (₹)", min_value=0.01, format="%.2f")
                stock = st.number_input("Initial Stock Quantity", min_value=0, step=1)
                reorder_level = st.number_input("Reorder Level", min_value=0, step=1)
                submit_button = st.form_submit_button("Add Product")
                if submit_button and product_name:
                    product_id = get_next_id("PROD", st.session_state.products)
                    st.session_state.products[product_id] = {
                        "name": product_name, "description": description, "unit_price": unit_price,
                        "stock": stock, "reorder_level": reorder_level
                    }
                    st.success(f"Product '{product_name}' added successfully! ID: {product_id}")
                    save_user_data(st.session_state.username, st.session_state)
                elif submit_button:
                    st.error("Product Name is required.")
        st.header("Current Inventory")
        if st.session_state.products:
            products_df = pd.DataFrame(st.session_state.products).T
            products_df.index.name = "Product ID"
            products_df['Stock Status'] = products_df.apply(lambda row: 'Low Stock' if row['stock'] < row['reorder_level'] else 'OK', axis=1)
            st.dataframe(products_df.style.apply(lambda x: ['background-color: #ff9999' if x['Stock Status'] == 'Low Stock' else '' for i in x], axis=1), use_container_width=True)
        else:
            st.info("No products in inventory. Add a new product to get started.")
    
    # --- Sales Module ---
    elif page == "Sales":
        st.title("Sales Management 🛒")
        with st.expander("📝 Create New Sale Order"):
            with st.form("new_sale_order_form", clear_on_submit=True):
                customer_options = {v['name']: k for k, v in st.session_state.customers.items()}
                customer_name = st.selectbox("Customer", [""] + list(customer_options.keys()))
                st.markdown("---")
                st.subheader("Items")
                if st.session_state.products:
                    product_options = {v['name']: k for k, v in st.session_state.products.items()}
                    selected_products = []
                    for i in range(5):
                        st.markdown(f"**Item {i+1}**")
                        col_p, col_q = st.columns([3, 1])
                        product_name = col_p.selectbox(f"Product", [""] + list(product_options.keys()), key=f'sale_product_{i}')
                        quantity = col_q.number_input(f"Quantity", min_value=0, step=1, key=f'sale_quantity_{i}')
                        if product_name and quantity > 0:
                            selected_products.append({'id': product_options[product_name], 'name': product_name, 'quantity': quantity})
                        st.markdown("---")
                else:
                    st.warning("No products available. Please add products in the Inventory section first.")
                submit_button = st.form_submit_button("Create Sale Order")
                if submit_button and customer_name and selected_products:
                    order_id = get_next_order_id("SO", st.session_state.sales_orders)
                    total_amount = 0
                    items = []
                    for item in selected_products:
                        product = st.session_state.products[item['id']]
                        if product['stock'] >= item['quantity']:
                            subtotal = product['unit_price'] * item['quantity']
                            total_amount += subtotal
                            items.append({'product_id': item['id'], 'product_name': item['name'], 'quantity': item['quantity'], 'unit_price': product['unit_price'], 'subtotal': subtotal})
                            st.session_state.products[item['id']]['stock'] -= item['quantity']
                        else:
                            st.error(f"Cannot create order: Not enough stock for {item['name']} (Available: {product['stock']})")
                            break
                    else:
                        st.session_state.sales_orders.append({
                            "id": order_id, "date": datetime.date.today(), "customer_id": customer_options[customer_name],
                            "customer_name": customer_name, "items": items, "total_amount": total_amount
                        })
                        st.success(f"Sale order {order_id} created successfully!")
                        save_user_data(st.session_state.username, st.session_state)
                elif submit_button:
                    st.error("Please select a customer and at least one product.")
        st.header("Recent Sales Orders")
        if st.session_state.sales_orders:
            sales_df = pd.DataFrame(st.session_state.sales_orders)
            sales_df = sales_df.drop(columns=['items'])
            st.dataframe(sales_df, use_container_width=True)
    
    # --- Purchases Module ---
    elif page == "Purchases":
        st.title("Purchase Management 📝")
        with st.expander("📝 Create New Purchase Order"):
            with st.form("new_purchase_order_form", clear_on_submit=True):
                supplier_options = {v['name']: k for k, v in st.session_state.suppliers.items()}
                supplier_name = st.selectbox("Supplier", [""] + list(supplier_options.keys()))
                st.markdown("---")
                st.subheader("Items to Purchase")
                if st.session_state.products:
                    product_options = {v['name']: k for k, v in st.session_state.products.items()}
                    selected_products = []
                    for i in range(5):
                        st.markdown(f"**Item {i+1}**")
                        col_p, col_q = st.columns([3, 1])
                        product_name = col_p.selectbox(f"Product", [""] + list(product_options.keys()), key=f'purchase_product_{i}')
                        quantity = col_q.number_input(f"Quantity", min_value=0, step=1, key=f'purchase_quantity_{i}')
                        if product_name and quantity > 0:
                            selected_products.append({'id': product_options[product_name], 'name': product_name, 'quantity': quantity})
                        st.markdown("---")
                else:
                    st.warning("No products available. Please add products in the Inventory section first.")
                submit_button = st.form_submit_button("Create Purchase Order")
                if submit_button and supplier_name and selected_products:
                    order_id = get_next_order_id("PO", st.session_state.purchase_orders)
                    total_amount = 0
                    items = []
                    for item in selected_products:
                        product = st.session_state.products[item['id']]
                        subtotal = product['unit_price'] * item['quantity']
                        total_amount += subtotal
                        items.append({'product_id': item['id'], 'product_name': item['name'], 'quantity': item['quantity'], 'unit_price': product['unit_price'], 'subtotal': subtotal})
                        st.session_state.products[item['id']]['stock'] += item['quantity']
                    st.session_state.purchase_orders.append({
                        "id": order_id, "date": datetime.date.today(), "supplier_id": supplier_options[supplier_name],
                        "supplier_name": supplier_name, "items": items, "total_amount": total_amount
                    })
                    st.success(f"Purchase order {order_id} created successfully!")
                    save_user_data(st.session_state.username, st.session_state)
                elif submit_button:
                    st.error("Please select a supplier and at least one product.")
        st.header("Recent Purchase Orders")
        if st.session_state.purchase_orders:
            purchases_df = pd.DataFrame(st.session_state.purchase_orders)
            purchases_df = purchases_df.drop(columns=['items'])
            st.dataframe(purchases_df, use_container_width=True)
    
    # --- Customers Module ---
    elif page == "Customers":
        st.title("Customer Relationship Management 👥")
        with st.expander("➕ Add New Customer"):
            with st.form("new_customer_form", clear_on_submit=True):
                customer_name = st.text_input("Name", placeholder="John Doe")
                contact_person = st.text_input("Contact Person (if applicable)")
                email = st.text_input("Email")
                phone = st.text_input("Phone")
                address = st.text_area("Address")
                submit_button = st.form_submit_button("Add Customer")
                if submit_button and customer_name:
                    customer_id = get_next_id("CUST", st.session_state.customers)
                    st.session_state.customers[customer_id] = {
                        "name": customer_name, "contact_person": contact_person,
                        "email": email, "phone": phone, "address": address
                    }
                    st.success(f"Customer '{customer_name}' added successfully! ID: {customer_id}")
                    save_user_data(st.session_state.username, st.session_state)
                elif submit_button:
                    st.error("Customer Name is required.")
        st.header("Existing Customers")
        if st.session_state.customers:
            customers_df = pd.DataFrame(st.session_state.customers).T
            customers_df.index.name = "Customer ID"
            st.dataframe(customers_df, use_container_width=True)
    
    # --- Suppliers Module ---
    elif page == "Suppliers":
        st.title("Supplier Management 🚚")
        with st.expander("➕ Add New Supplier"):
            with st.form("new_supplier_form", clear_on_submit=True):
                supplier_name = st.text_input("Name", placeholder="Supplier A Ltd.")
                contact_person = st.text_input("Contact Person")
                email = st.text_input("Email")
                phone = st.text_input("Phone")
                address = st.text_area("Address")
                submit_button = st.form_submit_button("Add Supplier")
                if submit_button and supplier_name:
                    supplier_id = get_next_id("SUPP", st.session_state.suppliers)
                    st.session_state.suppliers[supplier_id] = {
                        "name": supplier_name, "contact_person": contact_person,
                        "email": email, "phone": phone, "address": address
                    }
                    st.success(f"Supplier '{supplier_name}' added successfully! ID: {supplier_id}")
                    save_user_data(st.session_state.username, st.session_state)
                elif submit_button:
                    st.error("Supplier Name is required.")
        st.header("Existing Suppliers")
        if st.session_state.suppliers:
            suppliers_df = pd.DataFrame(st.session_state.suppliers).T
            suppliers_df.index.name = "Supplier ID"
            st.dataframe(suppliers_df, use_container_width=True)
    
    # --- Financial Health Module ---
    elif page == "Financial Health":
        st.title("Financial Health & Capital Requirement 💰")
        st.write("This module provides a simplified view of your business's financial status and suggests potential needs for capital.")
        st.warning("⚠️ **Disclaimer:** This is a simplified model for demonstration purposes and should not be considered professional financial advice. Please consult with a financial advisor for real-world decisions.")
        total_sales = sum(item['total_amount'] for item in st.session_state.sales_orders)
        total_purchases = sum(item['total_amount'] for item in st.session_state.purchase_orders)
        net_cash_flow = total_sales - total_purchases
        replenishment_cost = 0
        low_stock_items = []
        for product_id, product_data in st.session_state.products.items():
            if product_data['stock'] < product_data['reorder_level']:
                quantity_needed = (product_data['reorder_level'] - product_data['stock']) + 10
                cost = quantity_needed * product_data['unit_price']
                replenishment_cost += cost
                low_stock_items.append({
                    "Product ID": product_id, "Product Name": product_data['name'], "Current Stock": product_data['stock'],
                    "Reorder Level": product_data['reorder_level'], "Quantity Needed": quantity_needed, "Estimated Cost": cost
                })
        st.header("Key Financial Indicators")
        col1, col2 = st.columns(2)
        col1.metric("Net Cash Flow (Sales - Purchases)", f"₹{net_cash_flow:,.2f}", delta=f"₹{net_cash_flow:,.2f}", delta_color="inverse")
        col2.metric("Projected Inventory Replenishment Cost", f"₹{replenishment_cost:,.2f}")
        st.markdown("---")
        st.header("Capital Requirement Suggestion")
        if net_cash_flow < 0 and replenishment_cost > 0:
            st.error("🔴 **Capital Requirement Alert:** Your business has a negative net cash flow and a significant cost to replenish inventory. This indicates a potential need for a **short-term loan or capital infusion** to cover operational expenses and maintain stock.")
            st.write("The projected replenishment cost for low-stock items is `₹{:,.2f}`. Securing a loan could help you meet this demand and prevent stockouts.".format(replenishment_cost))
            if low_stock_items:
                with st.expander("See details of items requiring capital"):
                    low_stock_df = pd.DataFrame(low_stock_items)
                    st.dataframe(low_stock_df.set_index("Product ID"), use_container_width=True)
        elif replenishment_cost > 0:
            st.warning("🟡 **Low Stock Alert:** While your cash flow is positive, you have items below their reorder level. Keep an eye on your cash reserves to ensure you can cover the estimated `₹{:,.2f}` cost for replenishment.".format(replenishment_cost))
        elif net_cash_flow < 0:
            st.warning("🟡 **Cash Flow Warning:** Your total purchases exceed your total sales. Monitor your expenses closely to avoid a cash crunch, even though you have no immediate inventory needs.")
        else:
            st.success("🟢 **Financial Status:** Your business appears to be in a healthy position with positive cash flow and no immediate low-stock inventory issues.")

    # --- Business Expansion Module ---
    elif page == "Business Expansion":
        st.title("Business Expansion Toolkit 🚀")
        st.write("Based on your total sales, here's a personalized toolkit to help you grow your business.")
        total_sales = sum(item['total_amount'] for item in st.session_state.sales_orders)
        st.metric("Total Sales", f"₹{total_sales:,.2f}")
        if total_sales < 50000:
            st.header("Stage: Emerging Business 🐣")
            st.info("Your business is in its early stages. The focus should be on building a solid foundation and reaching your first key customers.")
            st.subheader("Actionable Toolkit:")
            st.markdown("""
            - **Formalize Your Business Plan:** Solidify your mission, vision, and long-term goals.
            - **Focus on Core Product/Service:** Master your primary offering before diversifying.
            - **Gather Customer Feedback:** Use surveys and direct conversations to understand what your customers need and want.
            - **Explore Basic Digital Marketing:** Set up a social media presence and a simple website to showcase your products.
            - **Build a Strong Network:** Connect with other small business owners and potential mentors.
            """)
        elif 50000 <= total_sales < 200000:
            st.header("Stage: Growth Business 🌱")
            st.info("You have a proven product/market fit. The goal now is to scale your operations and expand your reach.")
            st.subheader("Actionable Toolkit:")
            st.markdown("""
            - **Optimize Your Sales Funnel:** Refine your marketing and sales processes to increase conversion rates.
            - **Consider New Channels:** Explore selling on e-commerce platforms like Amazon or Flipkart to reach a wider audience.
            - **Invest in Customer Retention:** Implement a loyalty program or email marketing to keep existing customers engaged.
            - **Hire Strategically:** Consider bringing on your first employees to delegate tasks and free up your time.
            - **Introduce New Product Lines:** Expand your offerings with complementary products to increase average order value.
            """)
        else:
            st.header("Stage: Scaling Business 🚀")
            st.info("Your business is a well-oiled machine. It's time to think about long-term growth and market dominance.")
            st.subheader("Actionable Toolkit:")
            st.markdown("""
            - **Diversify Your Revenue Streams:** Explore new markets, products, or even services like franchising.
            - **Optimize Your Supply Chain:** Negotiate better deals with suppliers and improve logistics for efficiency.
            - **Implement Advanced Financial Management:** Use professional accounting software to get a clearer picture of your finances.
            - **Adopt Technology for Automation:** Invest in tools to automate marketing, customer service, or other repetitive tasks.
            - **Build a Strong Leadership Team:** Focus on building a team that can manage key areas of the business independently.
            """)
