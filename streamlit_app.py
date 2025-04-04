# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col #import col function
import requests #import requests for API response in line 31,32
# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie")
st.write("The name on your Smoothie will be:", name_on_order)


#ADDING the table to streamlit
cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
# st.dataframe(data = my_dataframe, use_container_width = True)
# st.stop()

# convert the snowpark Dataframe to a Pandas dataframe so we can use the LOC function
pd_df = my_dataframe.to_pandas()
# st.dataframe(pd_df)
# st.stop() 

#adding a multiselect list option for the fruits
ingredients_list = st.multiselect(
    'Chooses up to 5 ingredients:',
    my_dataframe,
    max_selections = 5)

if ingredients_list: #to ensure null instead of showing brackets(rough work of values)
#to converst items from the smoothie list to string for addition to table
    ingredients_string = '' 
#add fruits chosen(ingredients_list) to empty string(ingredients_string)
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].ILOC[0]
        st.write('The search value for ', fruit_chosen,'.')

        st.subheader(fruit_chosen + 'Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + fruit_chosen) # New section to display smoothiefroot nutrition information
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True) #putting API response in a dataframe for viewability

#show ingredients_list selected by user or customer
    #st.write(ingredients_string)

    time_to_insert = st.button('Submit Order')
#
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredients_string + """','""" + name_on_order + """')"""

    #st.write(my_insert_stmt)
    #st.stop()
    if time_to_insert:
        session.sql(my_insert_stmt).collect()

        st.success('Your Smoothie is ordered,' + ' ' +name_on_order, icon="✅")

