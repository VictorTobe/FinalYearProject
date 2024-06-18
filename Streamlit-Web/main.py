import streamlit as st
import joblib
import numpy as np
import json
import folium
from folium.plugins import HeatMap
from streamlit_folium import folium_static

# Load the pre-trained model using joblib
@st.cache_resource
def load_model():
    return joblib.load('../notebooks/gradient_boosting_model.joblib')

# Load the district coordinates
@st.cache_resource
def load_district_coordinates():
    with open('../data/district.json', 'r') as f:
        return json.load(f)

# Model Prediction
def model_prediction(month, day, hour, district):
    model = load_model()
    # Create input array
    input_arr = np.array([[month, day, hour, district]])
    predictions = model.predict(input_arr)
    return predictions[0]  # Returns the predicted alarm value

# Define class names and deployment methods
class_names = ['Low', 'Medium', 'High']
deployment_methods = {
    0: 'Low crime rate - No special deployment needed.',
    1: 'Medium crime rate - Increased patrolling recommended.',
    2: 'High crime rate - Deploy maximum force.'
}

# Function to get the list of days in a month
day_name = {
    'Sunday': 1, 'Monday': 2, 'Tuesday': 3, 'Wednesday': 4,
    'Thursday': 5, 'Friday': 6, 'Saturday': 7
}

# Map for month names to numerical values
month_names = {
    'January': 1, 'February': 2, 'March': 3, 'April': 4,
    'May': 5, 'June': 6, 'July': 7, 'August': 8,
    'September': 9, 'October': 10, 'November': 11, 'December': 12
}

# Sidebar
st.sidebar.title('Dashboard')
app_mode = st.sidebar.selectbox('Select Page', ['Home', 'About Project', 'Hotspot Prediction'])

# Main Page
if app_mode == 'Home':
    st.header('Crime Hotspot Prediction Project')
    st.subheader('Prediction for Effective Patrolling')
    st.text('Built By: Tobenna Nwankwo, 19CK025884')
    image_path = 'NPF.jpg'
    st.image(image_path)

# About Project
elif app_mode == 'About Project':
    st.header('About Project')
    st.text(
        '''
        This project uses machine learning models
        to predict crime hotspots and suggest appropriate
        deployment methods for effective patrolling.
        '''
    )

    st.subheader('Problem')
    st.text('Crime is a significant issue in many areas. Proper prediction of crime hotspots can help in efficient allocation of police resources and timely intervention.')

    st.subheader('About Dataset')
    st.text('Name: Crime Hotspot Prediction Data')
    st.text('This dataset contains information about various crimes along with their time and location details.')

    st.subheader('DataSet Link')
    st.text('Dataset is used for training machine learning models to predict crime hotspots.')

    st.subheader('Content')
    st.text('The dataset includes various features such as Month, Day, Hour, and District to help predict crime hotspots.')

# Crime Hotspot Prediction Page
elif app_mode == 'Hotspot Prediction':
    st.header('Crime Hotspot Prediction')
    
    # Load district coordinates
    district_coordinates = load_district_coordinates()
    
    # User inputs
    selected_month = st.selectbox('Month', list(month_names.keys()))
    month = month_names[selected_month]
    selected_day = st.selectbox('Day', list(day_name.keys()))
    day = day_name[selected_day]
    hour = st.selectbox('Hour', list(range(0, 24)))

    # Prediction Button
    if st.button('Predict'):
        st.write("Model Hotspot Prediction Result:")

        predictions = []
        heat_data_low = []
        heat_data_medium = []
        heat_data_high = []

        # Predict for all districts except district 13, 21, and 23
        for district in range(1, 26):  # Assuming districts are numbered from 1 to 25
            if district in {13, 21, 23}:
                continue
            result_index = model_prediction(month, day, hour, district)
            result_class = class_names[result_index]
            deployment_method = deployment_methods[result_index]
            predictions.append({
                'District': district,
                'Predicted Alarms': result_class,
                'Deployment Method': deployment_method,
                'Location': district_coordinates[str(district)]['Name'],
                'Latitude': district_coordinates[str(district)]['Latitude'],
                'Longitude': district_coordinates[str(district)]['Longitude']
            })

            # Add to heatmap data based on risk level
            if result_class == 'Low':
                heat_data_low.append([
                    district_coordinates[str(district)]['Latitude'],
                    district_coordinates[str(district)]['Longitude'],
                    1  # Heat intensity; you can use a different metric if available
                ])
            elif result_class == 'Medium':
                heat_data_medium.append([
                    district_coordinates[str(district)]['Latitude'],
                    district_coordinates[str(district)]['Longitude'],
                    1
                ])
            elif result_class == 'High':
                heat_data_high.append([
                    district_coordinates[str(district)]['Latitude'],
                    district_coordinates[str(district)]['Longitude'],
                    1
                ])

        # Display predictions and create a Folium map
        folium_map = folium.Map(location=[41.8781, -87.6298], zoom_start=11)

        color_map = {
            'Low': 'green',
            'Medium': 'orange',
            'High': 'red'
        }

        for prediction in predictions:
            st.markdown(f"**District {prediction['District']}**: {prediction['Predicted Alarms']}")
            st.markdown(f"Deployment Method: {prediction['Deployment Method']}\n")

            folium.Marker(
                location=[prediction['Latitude'], prediction['Longitude']],
                popup=f"District {prediction['District']}: {prediction['Predicted Alarms']}\n\n {prediction['Location']}",
                icon=folium.Icon(color=color_map[prediction['Predicted Alarms']])
            ).add_to(folium_map)

        # Add the heatmap layers
        if heat_data_low:
            HeatMap(heat_data_low, name='Low Risk', gradient={0.4: 'green', 0.65: 'lime', 1: 'yellow'}).add_to(folium_map)
        if heat_data_medium:
            HeatMap(heat_data_medium, name='Medium Risk', gradient={0.4: 'orange', 0.65: 'yellow', 1: 'red'}).add_to(folium_map)
        if heat_data_high:
            HeatMap(heat_data_high, name='High Risk', gradient={0.4: 'red', 0.65: 'darkred', 1: 'maroon'}).add_to(folium_map)

        folium.LayerControl().add_to(folium_map)

        folium_static(folium_map)
