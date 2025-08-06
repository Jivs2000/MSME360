#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import streamlit as st
import pandas as pd
from datetime import datetime
import uuid

# Set a wide layout for better display of data tables and charts
st.set_page_config(layout="wide")

# Initialize session state for data storage
if 'inventory' not in st.session_state:
    st.session_state.inventory = pd.DataFrame(columns=[
        'Product ID', 'Product Name', 'Description', 'Unit Price',
        'Current Stock Quantity', 'Reorder Level'
    ])
if 'sales_orders' not in st.session_state:
    st.session_state.sales_orders = pd.DataFrame(columns=[
        'Order ID', 'Date', 'Customer Name', 'Products', 'Total Amount'
    ])
if 'purchase_orders' not in st.session_state:
    st.session_state.purchase_orders = pd.DataFrame(columns=[
        'Order ID', 'Date', 'Supplier Name', 'Products', 'Total Amount'
    ])
if 'customers' not in st.session_state:
    st.session_state.customers = pd.DataFrame(columns=[
        'Customer ID', 'Name', 'Contact Person', 'Email', 'Phone', 'Address'
    ])
if 'suppliers' not in st.session_state:
    st.session_state.suppliers = pd.DataFrame(columns=[
        'Supplier ID', 'Name', 'Contact Person', 'Email', 'Phone', 'Address'
    ])
if 'sales_history' not in st.session_state:
    st.session_state.sales_history = pd.DataFrame(columns=['Date', 'Product ID', 'Product Name', 'Quantity', 'Total Sale'])

# --- Sidebar Navigation ---
st.sidebar.title("MSME360")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Inventory Management", "Sales Management",
     "Purchase Management", "Customer Management", "Supplier Management",
     "Reporting"]
)
st.sidebar.markdown("---")
st.sidebar.info("A simple, user-friendly ERP for managing your business operations.")

# --- Utility Functions ---

def generate_unique_id(prefix):
    """Generates a unique ID with a given prefix."""
    return f"{prefix}-{str(uuid.uuid4())[:8]}"

def update_stock(product_id, quantity_change, operation):
    """Updates the stock of a product based on a sale or purchase."""
    if product_id in st.session_state.inventory['Product ID'].values:
        idx = st.session_state.inventory[
            st.session_state.inventory['Product ID'] == product_id
        ].index[0]
        current_stock = st.session_state.inventory.loc[idx, 'Current Stock Quantity']
        if operation == 'sale':
            st.session_state.inventory.loc[idx, 'Current Stock Quantity'] = current_stock - quantity_change
        elif operation == 'purchase':
            st.session_state.inventory.loc[idx, 'Current Stock Quantity'] = current_stock + quantity_change

# --- Page Content ---

# Dashboard
if page == "Dashboard":
    st.title("Dashboard")
    st.markdown("---")

    # Metrics
    col1, col2, col3, col4 = st.columns(4)

    total_sales = st.session_state.sales_orders['Total Amount'].sum()
    col1.metric("Total Sales", f"₹{total_sales:,.2f}")

    current_stock_value = (st.session_state.inventory['Unit Price'] * st.session_state.inventory['Current Stock Quantity']).sum()
    col2.metric("Current Stock Value", f"₹{current_stock_value:,.2f}")

    pending_orders = st.session_state.sales_orders.shape[0] - st.session_state.sales_orders[
        'Order ID'
    ].shape[0]  # A simple placeholder
    col3.metric("Pending Orders", st.session_state.sales_orders.shape[0])

    low_stock_items = st.session_state.inventory[
        st.session_state.inventory['Current Stock Quantity'] <= st.session_state.inventory['Reorder Level']
    ].shape[0]
    col4.metric("Low Stock Items", low_stock_items)

    st.markdown("---")

    # Sales Trend Chart
    st.subheader("Sales Trends")
    if not st.session_state.sales_history.empty:
        # Ensure 'Date' is datetime and 'Total Sale' is numeric for plotting
        st.session_state.sales_history['Date'] = pd.to_datetime(st.session_state.sales_history['Date'])
        st.session_state.sales_history['Total Sale'] = pd.to_numeric(st.session_state.sales_history['Total Sale'], errors='coerce')
        sales_by_date = st.session_state.sales_history.groupby('Date')['Total Sale'].sum().reset_index()
        st.line_chart(sales_by_date.set_index('Date'))
    else:
        st.info("No sales data available to display trends.")

    # Top-Selling Products Chart
    st.subheader("Top-Selling Products")
    if not st.session_state.sales_history.empty:
        st.session_state.sales_history['Quantity'] = pd.to_numeric(st.session_state.sales_history['Quantity'], errors='coerce')
        clean_sales_history = st.session_state.sales_history.dropna(subset=['Quantity'])

        if not clean_sales_history.empty:
            top_products = clean_sales_history.groupby('Product Name')['Quantity'].sum().nlargest(5)
            st.bar_chart(top_products)
        else:
            st.info("No valid sales data available to display top-selling products.")
    else:
        st.info("No sales data available to display top-selling products.")

# Inventory Management
elif page == "Inventory Management":
    st.title("Inventory Management")
    st.markdown("---")

    inventory_tab, add_product_tab, update_stock_tab = st.tabs(
        ["View Inventory", "Add New Product", "Update Stock"]
    )

    with add_product_tab:
        st.subheader("Add New Product")
        with st.form("add_product_form"):
            product_name = st.text_input("Product Name")
            description = st.text_area("Description")
            unit_price = st.number_input("Unit Price", min_value=0.01, format="%.2f")
            current_stock_quantity = st.number_input(
                "Current Stock Quantity", min_value=0, step=1
            )
            reorder_level = st.number_input("Reorder Level", min_value=0, step=1)
            submitted = st.form_submit_button("Add Product")

            if submitted:
                if product_name and unit_price and current_stock_quantity >= 0:
                    new_product = pd.DataFrame([{
                        'Product ID': generate_unique_id('PROD'),
                        'Product Name': product_name,
                        'Description': description,
                        'Unit Price': unit_price,
                        'Current Stock Quantity': current_stock_quantity,
                        'Reorder Level': reorder_level
                    }])
                    st.session_state.inventory = pd.concat(
                        [st.session_state.inventory, new_product], ignore_index=True
                    )
                    st.success(f"Product '{product_name}' added successfully!")
                else:
                    st.error("Please fill in all required fields.")

    with inventory_tab:
        st.subheader("All Products")
        if not st.session_state.inventory.empty:
            # Highlight low stock items
            def highlight_low_stock(row):
                if row['Current Stock Quantity'] <= row['Reorder Level']:
                    return ['background-color: #ffcccc'] * len(row)
                return [''] * len(row)

            st.dataframe(
                st.session_state.inventory.style.apply(
                    highlight_low_stock, axis=1
                ).set_properties(
                    **{'background-color': '#fff3cd'},
                    subset=pd.IndexSlice[
                        st.session_state.inventory[
                            'Current Stock Quantity'
                        ] <= st.session_state.inventory['Reorder Level'], :
                    ]
                )
            )

            low_stock_items = st.session_state.inventory[
                st.session_state.inventory['Current Stock Quantity'] <= st.session_state.inventory['Reorder Level']
            ]
            if not low_stock_items.empty:
                st.warning("Low Stock Alert! The following products are below their reorder level.")
                st.dataframe(low_stock_items)
        else:
            st.info("No products in inventory. Add a new product to get started.")

    with update_stock_tab:
        st.subheader("Update Stock")
        if not st.session_state.inventory.empty:
            product_to_update = st.selectbox(
                "Select Product", st.session_state.inventory['Product Name']
            )
            product_id = st.session_state.inventory[
                st.session_state.inventory['Product Name'] == product_to_update
            ]['Product ID'].iloc[0]
            operation = st.radio("Operation", ["Receive Stock", "Dispatch Stock"])
            quantity_change = st.number_input(
                "Quantity to Update", min_value=1, step=1
            )
            update_button = st.button("Update Stock Quantity")

            if update_button:
                if operation == "Receive Stock":
                    update_stock(product_id, quantity_change, 'purchase')
                    st.success(f"Successfully received {quantity_change} units of {product_to_update}.")
                else:
                    current_stock = st.session_state.inventory[
                        st.session_state.inventory['Product ID'] == product_id
                    ]['Current Stock Quantity'].iloc[0]
                    if current_stock >= quantity_change:
                        update_stock(product_id, quantity_change, 'sale')
                        st.success(f"Successfully dispatched {quantity_change} units of {product_to_update}.")
                    else:
                        st.error("Cannot dispatch more than current stock.")
        else:
            st.warning("Please add products to inventory before updating stock.")

# Sales Management
elif page == "Sales Management":
    st.title("Sales Management")
    st.markdown("---")

    create_sale_tab, view_sales_tab = st.tabs(["Create Sale Order", "View Sales Orders"])

    with create_sale_tab:
        st.subheader("Create New Sale Order")
        if st.session_state.inventory.empty or st.session_state.customers.empty:
            st.warning("Please add products to inventory and customers before creating a sale.")
        else:
            with st.form("create_sale_form"):
                customer_name = st.selectbox(
                    "Select Customer", st.session_state.customers['Name']
                )
                products_sold = st.multiselect(
                    "Select Products", st.session_state.inventory['Product Name']
                )
                sale_products = []
                total_amount = 0

                for product in products_sold:
                    product_id = st.session_state.inventory[
                        st.session_state.inventory['Product Name'] == product
                    ]['Product ID'].iloc[0]
                    unit_price = st.session_state.inventory[
                        st.session_state.inventory['Product Name'] == product
                    ]['Unit Price'].iloc[0]
                    quantity = st.number_input(
                        f"Quantity for {product} (Unit Price: ₹{unit_price:.2f})",
                        min_value=1, step=1, key=f"sale_qty_{product_id}"
                    )
                    sale_products.append({
                        'product_id': product_id,
                        'product_name': product,
                        'quantity': quantity,
                        'unit_price': unit_price
                    })
                    total_amount += quantity * unit_price

                st.write(f"**Total Amount: ₹{total_amount:,.2f}**")
                submitted = st.form_submit_button("Record Sale")

                if submitted:
                    success = True
                    for item in sale_products:
                        current_stock = st.session_state.inventory[
                            st.session_state.inventory['Product ID'] == item['product_id']
                        ]['Current Stock Quantity'].iloc[0]
                        if current_stock < item['quantity']:
                            st.error(f"Cannot sell {item['quantity']} units of {item['product_name']}. Only {current_stock} available.")
                            success = False
                            break
                    
                    if success:
                        new_sale = pd.DataFrame([{
                            'Order ID': generate_unique_id('SALE'),
                            'Date': datetime.now().strftime("%Y-%m-%d"),
                            'Customer Name': customer_name,
                            'Products': sale_products,
                            'Total Amount': total_amount
                        }])
                        st.session_state.sales_orders = pd.concat(
                            [st.session_state.sales_orders, new_sale], ignore_index=True
                        )

                        for item in sale_products:
                            update_stock(item['product_id'], item['quantity'], 'sale')
                            new_history = pd.DataFrame([{
                                'Date': datetime.now().strftime("%Y-%m-%d"),
                                'Product ID': item['product_id'],
                                'Product Name': item['product_name'],
                                'Quantity': int(item['quantity']),
                                'Total Sale': float(item['quantity'] * item['unit_price'])
                            }])
                            st.session_state.sales_history = pd.concat(
                                [st.session_state.sales_history, new_history], ignore_index=True
                            )

                        st.success(f"Sale order for '{customer_name}' recorded successfully!")

    with view_sales_tab:
        st.subheader("All Sales Orders")
        if not st.session_state.sales_orders.empty:
            st.dataframe(st.session_state.sales_orders)
        else:
            st.info("No sales orders recorded yet.")

# Purchase Management
elif page == "Purchase Management":
    st.title("Purchase Management")
    st.markdown("---")

    create_purchase_tab, view_purchases_tab = st.tabs(["Create Purchase Order", "View Purchase Orders"])

    with create_purchase_tab:
        st.subheader("Create New Purchase Order")
        if st.session_state.inventory.empty or st.session_state.suppliers.empty:
            st.warning("Please add products to inventory and suppliers before creating a purchase.")
        else:
            with st.form("create_purchase_form"):
                supplier_name = st.selectbox(
                    "Select Supplier", st.session_state.suppliers['Name']
                )
                products_to_buy = st.multiselect(
                    "Select Products", st.session_state.inventory['Product Name']
                )
                purchase_products = []
                total_amount = 0

                for product in products_to_buy:
                    product_id = st.session_state.inventory[
                        st.session_state.inventory['Product Name'] == product
                    ]['Product ID'].iloc[0]
                    unit_price = st.session_state.inventory[
                        st.session_state.inventory['Product Name'] == product
                    ]['Unit Price'].iloc[0]
                    quantity = st.number_input(
                        f"Quantity for {product} (Unit Price: ₹{unit_price:.2f})",
                        min_value=1, step=1, key=f"purchase_qty_{product_id}"
                    )
                    purchase_products.append({
                        'product_id': product_id,
                        'product_name': product,
                        'quantity': quantity,
                        'unit_price': unit_price
                    })
                    total_amount += quantity * unit_price

                st.write(f"**Total Amount: ₹{total_amount:,.2f}**")
                submitted = st.form_submit_button("Record Purchase")

                if submitted:
                    new_purchase = pd.DataFrame([{
                        'Order ID': generate_unique_id('PURCH'),
                        'Date': datetime.now().strftime("%Y-%m-%d"),
                        'Supplier Name': supplier_name,
                        'Products': purchase_products,
                        'Total Amount': total_amount
                    }])
                    st.session_state.purchase_orders = pd.concat(
                        [st.session_state.purchase_orders, new_purchase], ignore_index=True
                    )

                    for item in purchase_products:
                        update_stock(item['product_id'], item['quantity'], 'purchase')

                    st.success(f"Purchase order from '{supplier_name}' recorded successfully!")

    with view_purchases_tab:
        st.subheader("All Purchase Orders")
        if not st.session_state.purchase_orders.empty:
            st.dataframe(st.session_state.purchase_orders)
        else:
            st.info("No purchase orders recorded yet.")

# Customer Management
elif page == "Customer Management":
    st.title("Customer Management (CRM)")
    st.markdown("---")

    add_customer_tab, view_customers_tab = st.tabs(["Add New Customer", "View Customers"])

    with add_customer_tab:
        st.subheader("Add New Customer")
        with st.form("add_customer_form"):
            name = st.text_input("Company Name")
            contact_person = st.text_input("Contact Person")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
            address = st.text_area("Address")
            submitted = st.form_submit_button("Add Customer")

            if submitted:
                if name:
                    new_customer = pd.DataFrame([{
                        'Customer ID': generate_unique_id('CUST'),
                        'Name': name,
                        'Contact Person': contact_person,
                        'Email': email,
                        'Phone': phone,
                        'Address': address
                    }])
                    st.session_state.customers = pd.concat(
                        [st.session_state.customers, new_customer], ignore_index=True
                    )
                    st.success(f"Customer '{name}' added successfully!")
                else:
                    st.error("Please enter a company name.")

    with view_customers_tab:
        st.subheader("All Customers")
        if not st.session_state.customers.empty:
            st.dataframe(st.session_state.customers)
        else:
            st.info("No customers added yet.")

# Supplier Management
elif page == "Supplier Management":
    st.title("Supplier Management")
    st.markdown("---")

    add_supplier_tab, view_suppliers_tab = st.tabs(["Add New Supplier", "View Suppliers"])

    with add_supplier_tab:
        st.subheader("Add New Supplier")
        with st.form("add_supplier_form"):
            name = st.text_input("Company Name")
            contact_person = st.text_input("Contact Person")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
            address = st.text_area("Address")
            submitted = st.form_submit_button("Add Supplier")

            if submitted:
                if name:
                    new_supplier = pd.DataFrame([{
                        'Supplier ID': generate_unique_id('SUPPL'),
                        'Name': name,
                        'Contact Person': contact_person,
                        'Email': email,
                        'Phone': phone,
                        'Address': address
                    }])
                    st.session_state.suppliers = pd.concat(
                        [st.session_state.suppliers, new_supplier], ignore_index=True
                    )
                    st.success(f"Supplier '{name}' added successfully!")
                else:
                    st.error("Please enter a company name.")

    with view_suppliers_tab:
        st.subheader("All Suppliers")
        if not st.session_state.suppliers.empty:
            st.dataframe(st.session_state.suppliers)
        else:
            st.info("No suppliers added yet.")

# Reporting
elif page == "Reporting":
    st.title("Reporting")
    st.markdown("---")

    sales_tab, inventory_tab, purchase_tab, toolkit_tab = st.tabs(
        ["Sales Report", "Inventory Report", "Purchase Report", "Expansion Toolkit"]
    )

    with sales_tab:
        st.subheader("Sales Report")
        if not st.session_state.sales_history.empty:
            st.dataframe(st.session_state.sales_history)
        else:
            st.info("No sales history to display.")

    with inventory_tab:
        st.subheader("Inventory Report")
        if not st.session_state.inventory.empty:
            st.dataframe(st.session_state.inventory)
            low_stock_items = st.session_state.inventory[
                st.session_state.inventory['Current Stock Quantity'] <= st.session_state.inventory['Reorder Level']
            ]
            if not low_stock_items.empty:
                st.warning("Low Stock Items")
                st.dataframe(low_stock_items)
            else:
                st.success("All inventory levels are good!")
        else:
            st.info("No inventory data to display.")

    with purchase_tab:
        st.subheader("Purchase Report")
        if not st.session_state.purchase_orders.empty:
            st.dataframe(st.session_state.purchase_orders)
        else:
            st.info("No purchase orders to display.")

    with toolkit_tab:
        st.subheader("Expansion Toolkit for MSMEs")
        total_sales = st.session_state.sales_orders['Total Amount'].sum()
        st.info(f"Your total lifetime sales are currently: ₹{total_sales:,.2f}")
        st.markdown("---")

        if total_sales < 100000:
            st.subheader("Level 1: Getting Started")
            st.write("Your sales are under ₹1,00,000. Focus on building a solid foundation.")
            st.markdown("""
            - **Marketing**: Utilize social media marketing and local community engagement.
            - **Operations**: Optimize your inventory management system and ensure efficient order processing.
            - **Finance**: Maintain clear financial records and understand your basic cash flow.
            - **Next Step**: Aim to reach a sales milestone of ₹5,00,000.
            """)
        elif total_sales < 1000000:
            st.subheader("Level 2: Growing Up")
            st.write("Your sales are between ₹1,00,000 and ₹10,00,000. It's time to scale up.")
            st.markdown("""
            - **Marketing**: Consider running targeted online ad campaigns (e.g., Google Ads, Facebook Ads).
            - **Operations**: Streamline your supply chain and explore new suppliers.
            - **Finance**: Look into business credit lines and understand your profit margins more deeply.
            - **Next Step**: Expand your customer base and aim for a sales milestone of ₹50,00,000.
            """)
        else:
            st.subheader("Level 3: Scaling & Expanding")
            st.write("Your sales exceed ₹10,00,000. You're ready for significant growth.")
            st.markdown("""
            - **Marketing**: Explore international markets or partnerships with larger companies.
            - **Operations**: Invest in automation tools and consider hiring specialized staff.
            - **Finance**: Consult with a financial advisor to plan for business expansion, potential investments, or franchising opportunities.
            - **Next Step**: Solidify your market position and explore new product lines.
            """)
