#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="MSME 360",
    page_icon="💼",
    layout="wide"
)

# --- Session State Initialization ---
if 'products' not in st.session_state:
    st.session_state.products = {}
if 'customers' not in st.session_state:
    st.session_state.customers = {}
if 'suppliers' not in st.session_state:
    st.session_state.suppliers = {}
if 'sales_orders' not in st.session_state:
    st.session_state.sales_orders = []
if 'purchase_orders' not in st.session_state:
    st.session_state.purchase_orders = []

# --- Helper Functions ---
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
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Dashboard", "Inventory", "Sales", "Purchases", "Customers", "Suppliers"]
)

# --- Main App ---

# --- Dashboard Module ---
if page == "Dashboard":
    st.title("Dashboard 📈")
    
    # --- Key Metrics ---
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

    # --- Charts ---
    if st.session_state.sales_orders:
        st.header("Sales Trend")
        sales_df = pd.DataFrame(st.session_state.sales_orders)
        sales_df['date'] = pd.to_datetime(sales_df['date'])
        sales_by_date = sales_df.groupby(sales_df['date'].dt.date)['total_amount'].sum().reset_index()
        sales_by_date.rename(columns={'date': 'Date', 'total_amount': 'Total Sales'}, inplace=True)
        st.line_chart(sales_by_date.set_index('Date'))
        
    if st.session_state.products:
        st.header("Top 5 Selling Products (Placeholder)")
        # This is a placeholder as sales orders don't track item quantities yet.
        # A more advanced version would track product-level sales.
        st.info("Functionality to track top-selling products will be added in a future version.")

# --- Inventory Module ---
elif page == "Inventory":
    st.title("Inventory Management 📦")
    
    # --- Add Product Form ---
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
                    "name": product_name,
                    "description": description,
                    "unit_price": unit_price,
                    "stock": stock,
                    "reorder_level": reorder_level
                }
                st.success(f"Product '{product_name}' added successfully! ID: {product_id}")
            elif submit_button:
                st.error("Product Name is required.")

    # --- View Inventory Table ---
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
    
    # --- Create Sale Order Form ---
    with st.expander("📝 Create New Sale Order"):
        with st.form("new_sale_order_form", clear_on_submit=True):
            customer_options = {v['name']: k for k, v in st.session_state.customers.items()}
            customer_name = st.selectbox("Customer", list(customer_options.keys()))
            
            st.markdown("---")
            st.subheader("Items")
            
            if st.session_state.products:
                products_df = pd.DataFrame(st.session_state.products).T
                product_options = {v['name']: k for k, v in st.session_state.products.items()}
                
                selected_products = []
                for i in range(5): # Allow up to 5 items per order
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
                
                # Process each item in the order
                for item in selected_products:
                    product = st.session_state.products[item['id']]
                    if product['stock'] >= item['quantity']:
                        subtotal = product['unit_price'] * item['quantity']
                        total_amount += subtotal
                        items.append({'product_id': item['id'], 'product_name': item['name'], 'quantity': item['quantity'], 'unit_price': product['unit_price'], 'subtotal': subtotal})
                        
                        # Update inventory stock
                        st.session_state.products[item['id']]['stock'] -= item['quantity']
                    else:
                        st.error(f"Cannot create order: Not enough stock for {item['name']} (Available: {product['stock']})")
                        break # Stop order creation if any item fails
                else: # The `else` block runs if the `for` loop completes without a `break`
                    st.session_state.sales_orders.append({
                        "id": order_id,
                        "date": datetime.date.today(),
                        "customer_id": customer_options[customer_name],
                        "customer_name": customer_name,
                        "items": items,
                        "total_amount": total_amount
                    })
                    st.success(f"Sale order {order_id} created successfully!")
            elif submit_button:
                st.error("Please select a customer and at least one product.")

    # --- View Sales Orders Table ---
    st.header("Recent Sales Orders")
    if st.session_state.sales_orders:
        sales_df = pd.DataFrame(st.session_state.sales_orders)
        sales_df = sales_df.drop(columns=['items']) # Hide complex list of items for table
        st.dataframe(sales_df, use_container_width=True)
    else:
        st.info("No sales orders have been placed yet.")

# --- Purchases Module ---
elif page == "Purchases":
    st.title("Purchase Management 📝")
    
    # --- Create Purchase Order Form ---
    with st.expander("📝 Create New Purchase Order"):
        with st.form("new_purchase_order_form", clear_on_submit=True):
            supplier_options = {v['name']: k for k, v in st.session_state.suppliers.items()}
            supplier_name = st.selectbox("Supplier", list(supplier_options.keys()))
            
            st.markdown("---")
            st.subheader("Items to Purchase")
            
            if st.session_state.products:
                products_df = pd.DataFrame(st.session_state.products).T
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

                # Process each item
                for item in selected_products:
                    product = st.session_state.products[item['id']]
                    # Assume purchase price is the same as unit price for simplicity
                    subtotal = product['unit_price'] * item['quantity']
                    total_amount += subtotal
                    items.append({'product_id': item['id'], 'product_name': item['name'], 'quantity': item['quantity'], 'unit_price': product['unit_price'], 'subtotal': subtotal})
                    
                    # Update inventory stock
                    st.session_state.products[item['id']]['stock'] += item['quantity']

                st.session_state.purchase_orders.append({
                    "id": order_id,
                    "date": datetime.date.today(),
                    "supplier_id": supplier_options[supplier_name],
                    "supplier_name": supplier_name,
                    "items": items,
                    "total_amount": total_amount
                })
                st.success(f"Purchase order {order_id} created successfully!")
            elif submit_button:
                st.error("Please select a supplier and at least one product.")

    # --- View Purchase Orders Table ---
    st.header("Recent Purchase Orders")
    if st.session_state.purchase_orders:
        purchases_df = pd.DataFrame(st.session_state.purchase_orders)
        purchases_df = purchases_df.drop(columns=['items'])
        st.dataframe(purchases_df, use_container_width=True)
    else:
        st.info("No purchase orders have been placed yet.")

# --- Customers Module ---
elif page == "Customers":
    st.title("Customer Relationship Management 👥")
    
    # --- Add Customer Form ---
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
                    "name": customer_name,
                    "contact_person": contact_person,
                    "email": email,
                    "phone": phone,
                    "address": address
                }
                st.success(f"Customer '{customer_name}' added successfully! ID: {customer_id}")
            elif submit_button:
                st.error("Customer Name is required.")
                
    # --- View Customers Table ---
    st.header("Existing Customers")
    if st.session_state.customers:
        customers_df = pd.DataFrame(st.session_state.customers).T
        customers_df.index.name = "Customer ID"
        st.dataframe(customers_df, use_container_width=True)
    else:
        st.info("No customers have been added yet.")

# --- Suppliers Module ---
elif page == "Suppliers":
    st.title("Supplier Management 🚚")

    # --- Add Supplier Form ---
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
                    "name": supplier_name,
                    "contact_person": contact_person,
                    "email": email,
                    "phone": phone,
                    "address": address
                }
                st.success(f"Supplier '{supplier_name}' added successfully! ID: {supplier_id}")
            elif submit_button:
                st.error("Supplier Name is required.")

    # --- View Suppliers Table ---
    st.header("Existing Suppliers")
    if st.session_state.suppliers:
        suppliers_df = pd.DataFrame(st.session_state.suppliers).T
        suppliers_df.index.name = "Supplier ID"
        st.dataframe(suppliers_df, use_container_width=True)
    else:
        st.info("No suppliers have been added yet.")
