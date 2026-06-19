import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, text
import time

#  1. PAGE CONFIGURATION 
st.set_page_config(page_title="Community Food Share Portal", layout="wide")

# 2. DATABASE SETUP  
# Streamlit deployment ke liye hum SQLite database file ka use kar rahe hain

db_engine = create_engine("sqlite:///food_wastage.db")

@st.cache_data
def fetch_database_records(sql_query):
    return pd.read_sql(sql_query, db_engine)

# 3. FETCHING ALL 4 TABLES 
try:
    inventory_data = fetch_database_records("SELECT * FROM food_listings")
    donor_data = fetch_database_records("SELECT * FROM providers")
    receiver_data = fetch_database_records("SELECT * FROM receivers")
    transaction_data = fetch_database_records("SELECT * FROM claims")
except Exception as err:
    st.error(f"Failed to connect to backend: {err}")
    st.stop()

#  4. SIDEBAR NAVIGATION 
st.sidebar.title(" Navigation Menu")
st.sidebar.markdown("Welcome to the Community Food Share backend system.")
app_mode = st.sidebar.radio("Go to Section:", ["Dashboard Overview", " Food Directory", " System Admin (CRUD)"])

st.title(" Community Food Share Portal")
st.markdown("Bridging the gap between surplus food and communities in need.")
st.divider()

# PAGE 1: DASHBOARD OVERVIEW

if app_mode == "Dashboard Overview":
    st.subheader("Global Metrics & Insights")
    
    # --- ADDING HORIZONTAL FILTERS FOR CHARTS ---
    st.markdown("**Filter Dashboard Data:**")
    f1, f2, f3 = st.columns(3)
    
    # 'key' attribute zaroori hai taaki Streamlit in filters ko Page 2 ke filters se confuse na kare
    dash_loc = f1.selectbox(" Select City", ["All Cities"] + inventory_data['Location'].dropna().unique().tolist(), key="dash_loc")
    dash_prov = f2.selectbox(" Select Donor Type", ["All Donors"] + inventory_data['Provider_Type'].dropna().unique().tolist(), key="dash_prov")
    dash_diet = f3.selectbox(" Select Diet", ["All Diets"] + inventory_data['Food_Type'].dropna().unique().tolist(), key="dash_diet")
    
    # Filtering the data based on selection
    filtered_dash_data = inventory_data.copy()
    if dash_loc != "All Cities":
        filtered_dash_data = filtered_dash_data[filtered_dash_data['Location'] == dash_loc]
    if dash_prov != "All Donors":
        filtered_dash_data = filtered_dash_data[filtered_dash_data['Provider_Type'] == dash_prov]
    if dash_diet != "All Diets":
        filtered_dash_data = filtered_dash_data[filtered_dash_data['Food_Type'] == dash_diet]
        
    st.divider()

    # KPIs using Filtered Data
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Items Available", len(filtered_dash_data))
    m2.metric("Filtered Quantity", int(filtered_dash_data['Quantity'].sum()) if not filtered_dash_data.empty else 0)
    m3.metric("Registered Donors", len(donor_data))
    m4.metric("Partnered NGOs", len(receiver_data))
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 4 Standard Charts 
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        if not filtered_dash_data.empty:
            fig_pie = px.pie(filtered_dash_data, names='Provider_Type', values='Quantity', 
                             title='Food Volume by Provider Type', hole=0.3, 
                             color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_pie, use_container_width=True)
            
    with chart_col2:
        if not filtered_dash_data.empty:
            fig_bar = px.bar(filtered_dash_data.groupby('Meal_Type', as_index=False)['Quantity'].sum(), 
                             x='Meal_Type', y='Quantity', color='Meal_Type',
                             title='Demand by Meal Type', text_auto=True)
            st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    chart_col3, chart_col4 = st.columns(2)
    
    with chart_col3:
        if not filtered_dash_data.empty:
            city_counts = filtered_dash_data['Location'].value_counts().reset_index().head(7)
            city_counts.columns = ['City', 'Listings']
            fig_city = px.bar(city_counts, x='City', y='Listings', title='Top 7 Cities by Food Listings', 
                              color='Listings', color_continuous_scale='Magma')
            st.plotly_chart(fig_city, use_container_width=True)
            
    with chart_col4:
        if not transaction_data.empty:
            claim_status = transaction_data['Status'].value_counts().reset_index()
            claim_status.columns = ['Status', 'Count']
            fig_status = px.pie(claim_status, names='Status', values='Count', title='Overall Claim Status Distribution')
            st.plotly_chart(fig_status, use_container_width=True)


# PAGE 2: FOOD DIRECTORY 

elif app_mode == " Food Directory":
    st.subheader("Search & Filter Inventory")
    
    # Filters on top instead of sidebar
    f1, f2, f3 = st.columns(3)
    loc_filter = f1.selectbox("Filter by City", ["All Cities"] + inventory_data['Location'].dropna().unique().tolist())
    type_filter = f2.selectbox("Filter by Donor Type", ["All Donors"] + inventory_data['Provider_Type'].dropna().unique().tolist())
    diet_filter = f3.selectbox("Filter by Diet", ["All Diets"] + inventory_data['Food_Type'].dropna().unique().tolist())
    
    # Apply logic
    display_data = inventory_data.copy()
    if loc_filter != "All Cities": display_data = display_data[display_data['Location'] == loc_filter]
    if type_filter != "All Donors": display_data = display_data[display_data['Provider_Type'] == type_filter]
    if diet_filter != "All Diets": display_data = display_data[display_data['Food_Type'] == diet_filter]
    
    st.dataframe(display_data, use_container_width=True)
    
    st.markdown("###  Donor Contact List")
    if not display_data.empty:
        contacts = pd.merge(display_data[['Provider_ID']], donor_data, on='Provider_ID', how='left').drop_duplicates()
        st.dataframe(contacts[['Name', 'Type', 'City', 'Contact']], use_container_width=True)

# PAGE 3: SYSTEM ADMIN


elif app_mode == " System Admin (CRUD)":
    st.subheader("Manage Database Records")
    st.write("Use the panels below to securely modify the food inventory database.")
    
    record_ids = inventory_data['Food_ID'].tolist() if not inventory_data.empty else []
    
    # CREATE
    with st.expander(" ADD NEW FOOD RECORD (Insert)"):
        
        
        if not inventory_data.empty:
            max_current_id = int(inventory_data['Food_ID'].max())
            next_valid_id = max_current_id + 1
        else:
            next_valid_id = 10000 # Default starting ID agar database khali ho
        # -----------------------------------
        
        with st.form("insert_form"):
            c1, c2 = st.columns(2)
            
            in_id = c1.number_input("Assign Food ID", min_value=next_valid_id, value=next_valid_id, step=1)
            
            in_name = c2.text_input("Item Name (e.g., Rice & Curry)")
            # Quantity mein bhi step=1 daal diya taaki decimals na aayein
            in_qty = c1.number_input("Item Quantity", min_value=1, step=1) 
            in_prov = c2.selectbox("Select Provider ID", donor_data['Provider_ID'].tolist() if not donor_data.empty else [1])
            in_loc = c1.text_input("City/Location")
            in_meal = c2.selectbox("Meal Category", ["Breakfast", "Lunch", "Dinner", "Snacks"])
            in_diet = c1.selectbox("Dietary Type", ["Vegetarian", "Non-Vegetarian", "Vegan"])
            
            if st.form_submit_button("Insert Record into Database"):
                try:
                    with db_engine.connect() as connection:
                        connection.execute(text(f"""
                            INSERT INTO food_listings (Food_ID, Food_Name, Quantity, Provider_ID, Location, Meal_Type, Food_Type) 
                            VALUES ({in_id}, '{in_name}', {in_qty}, {in_prov}, '{in_loc}', '{in_meal}', '{in_diet}')
                        """))
                        connection.commit()
                    st.cache_data.clear()
                    st.success("New record inserted successfully!")
                    time.sleep(1.5)
                    st.rerun()
                except Exception as e:
                    st.error(f"Insertion failed: {e}")

    #  UPDATE 
    with st.expander(" UPDATE EXISTING RECORD (Modify)"):
        up_id = st.selectbox("Select ID to Modify", record_ids, key="up_select")
        if up_id:
            row_data = inventory_data[inventory_data['Food_ID'] == up_id].iloc[0]
            with st.form("modify_form"):
                c3, c4 = st.columns(2)
                up_name = c3.text_input("Item Name", value=row_data['Food_Name'])
                up_qty = c4.number_input("Item Quantity", value=int(row_data['Quantity']))
                
                prov_list = donor_data['Provider_ID'].tolist() if not donor_data.empty else [1]
                idx_prov = prov_list.index(row_data['Provider_ID']) if row_data['Provider_ID'] in prov_list else 0
                up_prov = c3.selectbox("Provider ID", prov_list, index=idx_prov)
                
                up_loc = c4.text_input("City/Location", value=row_data['Location'])
                
                m_list = ["Breakfast", "Lunch", "Dinner", "Snacks"]
                idx_meal = m_list.index(row_data['Meal_Type']) if row_data['Meal_Type'] in m_list else 0
                up_meal = c3.selectbox("Meal Category", m_list, index=idx_meal)
                
                d_list = ["Vegetarian", "Non-Vegetarian", "Vegan"]
                idx_diet = d_list.index(row_data['Food_Type']) if row_data['Food_Type'] in d_list else 0
                up_diet = c4.selectbox("Dietary Type", d_list, index=idx_diet)
                
                if st.form_submit_button("Update Record"):
                    try:
                        with db_engine.connect() as connection:
                            connection.execute(text(f"""
                                UPDATE food_listings 
                                SET Food_Name='{up_name}', Quantity={up_qty}, Provider_ID={up_prov}, 
                                    Location='{up_loc}', Meal_Type='{up_meal}', Food_Type='{up_diet}' 
                                WHERE Food_ID={up_id}
                            """))
                            connection.commit()
                        st.cache_data.clear()
                        st.success("Record modified successfully!")
                        time.sleep(1.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Modification failed: {e}")

    #DELETE 
    with st.expander("DELETE RECORD (Remove)"):
        st.warning("This will permanently drop the record from the SQL backend.")
        del_id = st.selectbox("Select ID to Drop", record_ids, key="del_select")
        
        if st.button("Drop Record", type="primary"):
            try:
                with db_engine.connect() as connection:
                    connection.execute(text(f"DELETE FROM food_listings WHERE Food_ID={del_id}"))
                    connection.commit()
                st.cache_data.clear()
                st.success("Record dropped permanently!")
                time.sleep(1.5)
                st.rerun()
            except Exception as e:
                st.error(f"Drop failed: {e}")