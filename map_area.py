import math
import json
import warnings

import pandas as pd
import geopandas as gpd
import folium
from branca.element import Figure
from shapely.geometry import Point

import streamlit as st
import streamlit.components.v1 as components
from streamlit_folium import st_folium

# Import the sidebar function from sidebar.py
from sidebar import sidebar

# 3.16000, 101.71000 : Kuala Lumpur
st.image('mmu-multimedia-university6129.png', use_column_width=False, caption='', width=200, )
def read_file(filename, sheetname):
    excel_file = pd.ExcelFile(filename)
    data_d = excel_file.parse(sheet_name=sheetname)

    return data_d

if __name__ == '__main__':
    st.title('Available ITP companies in Malaysia')
    # Call the sidebar function to include it in your app
    sidebar()

    # Create an empty space in the sidebar to display company information
    company_info_container = st.empty()

    file_input = 'MMU ITP List 13_9_9_11.xlsx'
    geojson_file = "msia_district.geojson"

    text_load_state = st.text('Reading files ...')
    with open(geojson_file) as gj_f:
        geojson_data = gpd.read_file(gj_f)

    itp_list_state = read_file(file_input, 0)
    text_load_state.text('Reading files ... Done!')

    map_size = Figure(width=800, height=600)
    map_my = folium.Map(location=[4.2105, 108.9758], zoom_start=6)
    map_size.add_child(map_my)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
    
    itp_list_state['geometry'] = itp_list_state.apply(lambda x: Point(x['map_longitude'], x['map_latitude']), axis=1)
    itp_list_state = gpd.GeoDataFrame(itp_list_state, geometry='geometry')

    joined_data = gpd.sjoin(geojson_data, itp_list_state, op="contains").groupby(["NAME_1", "NAME_2"]).size().reset_index(name="count")

    merged_gdf = geojson_data.merge(joined_data, on=["NAME_1", "NAME_2"], how="left")
    merged_gdf['count'].fillna(0, inplace=True)

    threshold_scale = [0, 1, 2, 4, 8, 16, 32, 64, 128, 200, 300, 400] 

    choropleth = folium.Choropleth(
        geo_data=merged_gdf,
        name='choropleth',
        data=merged_gdf,
        columns=['NAME_2', 'count'],
        key_on='feature.properties.NAME_2',
        fill_color='RdYlGn',
        fill_opacity=0.7,
        line_opacity=0.2,
        threshold_scale=threshold_scale,
        line_color='black',
        legend_name='District Counts',
        highlight=False  # Disable the darkened coloration when hovering
    ).add_to(map_my)

    folium.GeoJsonTooltip(fields=['NAME_1','NAME_2', 'count'], aliases=['State','District', 'Count']).add_to(choropleth.geojson)

    # Create a section in Streamlit to display the detailed company information
    st.sidebar.title('Company Details')
    selected_company = st.sidebar.empty()

    text_load_state.text('Plotting ...')

    for itp_data in itp_list_state.to_dict(orient='records'):
        latitude = itp_data['map_latitude']
        longitude = itp_data['map_longitude']
        company_name = itp_data['Company name']
        company_address = itp_data['Company address']
        company_email = itp_data['Company Email'] 
        company_tel = itp_data['Company Tel'] 
        company_industry = itp_data['industry'] 
        
        # Create a customized HTML popup with two sections
        popup_content_basic = f"""
        <strong>{company_name}</strong><br>
        <em>Address:</em> {company_address}<br>
        <a href="#" onclick="selectCompany('{company_name}')">Show Details</a>
        """

        if not math.isnan(latitude) and not math.isnan(longitude):
            # Create a marker with the customized HTML popup
            marker = folium.Marker(location=[latitude, longitude], tooltip=company_name)
            marker.add_to(map_my)

            # Add a click event to the marker to display a popup on click
            folium.Popup(popup_content_basic, max_width=300).add_to(marker)

            # Create a customized HTML popup for detailed information
            popup_content_detailed = f"""
            <strong>{company_name}</strong><br>
            <em>Address:</em> {company_address}<br>
            <em>Email:</em> {company_email}<br>
            <em>Tel:</em> {company_tel}<br>
            <em>Industry:</em> {company_industry}
            """

            # Use Streamlit to display detailed company information when the basic popup link is clicked
            if st.sidebar.button(f"Show Details for {company_name}", key=f"{company_name}_button"):
                selected_company.markdown(popup_content_detailed, unsafe_allow_html=True)

    # Save the map with markers and basic popups to an HTML file
    map_my.save('itp_area_map.html')

    # Display the HTML file in Streamlit
    with open('itp_area_map.html', 'r', encoding='utf-8') as map_file:
        map_html = map_file.read()
        components.html(map_html, 1000, 600)
   

    # for itp_data in itp_list_state.to_dict(orient='records'):
    #     latitude = itp_data['map_latitude']
    #     longitude = itp_data['map_longitude']
    #     company_name = itp_data['Company name']
    #     company_address = itp_data['Company address']
    #     popup_name = '<strong>' + str(company_name) + '</strong>\n' + str(company_address)
    #     if not math.isnan(latitude) and not math.isnan(longitude):
    #         marker = folium.Marker(location=[latitude, longitude], popup=popup_name, tooltip=company_name)
    #         marker.add_to(map_my)

    #         # Create a function to update the sidebar with company information when marker is clicked
    #         def update_sidebar(marker=marker, company_info_container=company_info_container):
    #             company_info_container.write(f"**Company Name:** {company_name}")
    #             company_info_container.write(f"**Company Address:** {company_address}")

    #         # Add a click event to the marker
    #         marker.add_to(map_my)
    #         marker.add_child(folium.ClickForMarker(popup=update_sidebar))
    
    text_load_state.text('Plotting ... Done!')

    map_my.save('itp_area_map.html')
    # p = open('itp_area_map.html')
    p = open('itp_area_map.html', 'r', encoding='utf-8')
    components.html(p.read(), 1000, 600)


#python -m streamlit run map_area.py
