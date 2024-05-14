import streamlit as st
import pandas as pd
import io

# Set the app title
st.title("Energy Consumption Analysis")

# Function to create sample data
def create_sample_data():
    # Define the required columns and their initial zero values
    columns = [
        "Month", "Interior Lighting (MWh)", "Receptacle Equipment (MWh)", "Refrigeration (MWh)",
        "Other Process (MWh)", "Space Heating (MWh)", "Service Water Heating (MWh)", "Space Cooling (MWh)",
        "Heat Rejection (MWh)", "Interior Central Fans (MWh)", "Interior Local Fans (MWh)", "Exhaust Fans (MWh)",
        "Pumps (MWh)", "Net Geo Heating available", "Net Geo Cooling available", "Net Geo DHW available"
    ]
    
    # Define a list of month names
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]
    
    # Create a DataFrame with the specified columns and initial zero values
    sample_df = pd.DataFrame({col: [0] * 12 for col in columns})
    # Assign the month names to the "Month" column
    sample_df["Month"] = months
    
    return sample_df

# Add a button to allow the user to download the sample data file
# Create an in-memory buffer to store the Excel file data
buffer = io.BytesIO()

# Create sample data
sample_df = create_sample_data()

# Save the sample DataFrame as an Excel file to the buffer
sample_df.to_excel(buffer, index=False, engine="openpyxl")

# Rewind the buffer so it can be read from the beginning
buffer.seek(0)

# Use st.download_button to allow the user to download the sample data file
st.download_button(
    label="Download Sample Data",
    data=buffer,
    file_name="sample_data.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
# Function to calculate energy consumption from a DataFrame


def calculate_energy_consumption(df, file_type):
    # Calculate energy consumption for each end-use category
    # Convert MWh to kWh
    interior_lighting = df["Interior Lighting (MWh)"].sum() * 1000
    receptacle_equipment = df["Receptacle Equipment (MWh)"].sum() * 1000

    if file_type == 'proposed':
        # Calculate space heating with potential geothermal heating subtraction for the proposed file
        if "Net Geo Heating available" in df.columns:
            space_heating = (df["Space Heating (MWh)"].sum(
            ) - df["Net Geo Heating available"].sum()) * 1000
        else:
            space_heating = df["Space Heating (MWh)"].sum() * 1000

        # Calculate service water heating with potential geothermal DHW subtraction for the proposed file
        if "Net Geo DHW available" in df.columns:
            service_water_heating = (df["Service Water Heating (MWh)"].sum(
            ) - df["Net Geo DHW available"].sum()) * 1000
        else:
            service_water_heating = df["Service Water Heating (MWh)"].sum(
            ) * 1000

        # Calculate space cooling with potential geothermal cooling subtraction for the proposed file
        if "Net Geo Cooling available" in df.columns:
            space_cooling = (df["Space Cooling (MWh)"].sum(
            ) - df["Net Geo Cooling available"].sum()) * 1000
        else:
            space_cooling = df["Space Cooling (MWh)"].sum() * 1000

    else:  # For the comparison file
        # Calculate space heating without geothermal subtraction
        space_heating = df["Space Heating (MWh)"].sum() * 1000

        # Calculate service water heating without geothermal subtraction
        service_water_heating = df["Service Water Heating (MWh)"].sum() * 1000

        # Calculate space cooling without geothermal subtraction
        space_cooling = df["Space Cooling (MWh)"].sum() * 1000

    # Remaining calculations (not dependent on file type)
    heat_rejection = df["Heat Rejection (MWh)"].sum() * 1000
    hvac_fans = (df["Interior Central Fans (MWh)"].sum() +
                 df["Interior Local Fans (MWh)"].sum()) * 1000
    pumps = df["Pumps (MWh)"].sum() * 1000
    other_process = df["Other Process (MWh)"].sum() * 1000

    # Calculate the total energy consumption
    total_energy_consumption = (
        interior_lighting + receptacle_equipment + space_heating + service_water_heating +
        space_cooling + heat_rejection + hvac_fans + pumps + other_process
    )

    # Return a dictionary containing the calculated values
    return {
        "Interior Lighting": interior_lighting,
        "Receptacle Equipment": receptacle_equipment,
        "Space Heating": space_heating,
        "Service Water Heating": service_water_heating,
        "Space Cooling": space_cooling,
        "Heat Rejection": heat_rejection,
        "HVAC Fans": hvac_fans,
        "Pumps": pumps,
        "Other Process": other_process,
        "Total": total_energy_consumption
    }


def cam_calculate_energy_consumption(df, file_type):
    # Calculate energy consumption for each end-use category
    # Convert MWh to kWh
    interior_lighting = df["Interior Lighting (MWh)"].sum() * 1000
    receptacle_equipment = df["Receptacle Equipment (MWh)"].sum() * 1000
    space_heating = df["Space Heating (MWh)"].sum() * 1000
    service_water_heating = df["Service Water Heating (MWh)"].sum() * 1000
    space_cooling = df["Space Cooling (MWh)"].sum() * 1000
    heat_rejection = df["Heat Rejection (MWh)"].sum() * 1000
    hvac_fans = (df["Interior Central Fans (MWh)"].sum() +
                 df["Interior Local Fans (MWh)"].sum()) * 1000
    pumps = df["Pumps (MWh)"].sum() * 1000
    other_process = df["Other Process (MWh)"].sum() * 1000

    # Calculate the total energy consumption
    total_energy_consumption = (
        interior_lighting
        + receptacle_equipment
        + space_heating
        + service_water_heating
        + space_cooling
        + heat_rejection
        + hvac_fans
        + pumps
        + other_process
    )

    # Return a dictionary containing the calculated values
    return {
        "Interior Lighting": interior_lighting,
        "Receptacle Equipment": receptacle_equipment,
        "Space Heating": space_heating,
        "Service Water Heating": service_water_heating,
        "Space Cooling": space_cooling,
        "Heat Rejection": heat_rejection,
        "HVAC Fans": hvac_fans,
        "Pumps": pumps,
        "Other Process": other_process,
        "Total": total_energy_consumption
    }


# Create a file uploader widget for users to upload the first data file
uploaded_file_1 = st.file_uploader("Upload your proposed data file (CSV or Excel)", type=[
                                   "csv", "xlsx", "xls"], key="file_1")
# Initialize comparison data frame and energy consumption
df_1 = None
energy_consumption_1 = None
# Process the first data file if provided
if uploaded_file_1 is not None:
    # Determine the file type based on the file extension
    file_extension_1 = uploaded_file_1.name.split('.')[-1]

    # Load the data into a pandas DataFrame based on the file type
    if file_extension_1 == 'csv':
        df_1 = pd.read_csv(uploaded_file_1)
    elif file_extension_1 in ['xls', 'xlsx']:
        df_1 = pd.read_excel(uploaded_file_1)

    # Calculate energy consumption for the first data file (proposed data)
    energy_consumption_1 = calculate_energy_consumption(df_1, 'proposed')

# Create a file uploader widget for users to upload the second data file
uploaded_file_2 = st.file_uploader("Upload your comparison data file (CSV or Excel)", type=[
                                   "csv", "xlsx", "xls"], key="file_2")
# Initialize comparison data frame and energy consumption
df_2 = None
energy_consumption_2 = None
# Process the second data file if provided
if uploaded_file_2 is not None:
    # Determine the file type based on the file extension
    file_extension_2 = uploaded_file_2.name.split('.')[-1]

    # Load the data into a pandas DataFrame based on the file type
    if file_extension_2 == 'csv':
        df_2 = pd.read_csv(uploaded_file_2)
    elif file_extension_2 in ['xls', 'xlsx']:
        df_2 = pd.read_excel(uploaded_file_2)

    # Calculate energy consumption for the second data file (comparison data)
    energy_consumption_2 = cam_calculate_energy_consumption(df_2, 'comparison')
    
# Create a sidebar for month selection
month_options = ["All"] + [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

selected_month = st.sidebar.selectbox(
    "Select a month (or 'All' to show all data):",
    month_options,
    index=0  # By default, select 'All' to show all data
)

# Add a "Clear Filter" button in the sidebar
if st.sidebar.button("Clear Filter"):
    selected_month = "All"  # Reset the selected month to "All"

# Filter the proposed data based on the selected month
if df_1 is not None:
    if selected_month == "All":
        filtered_df_1 = df_1  # Show all data if 'All' is selected
    else:
        filtered_df_1 = df_1[df_1["Month"] == selected_month]  # Filter data based on selected month

    # Calculate energy consumption for proposed data (filtered)
    energy_consumption_1 = calculate_energy_consumption(filtered_df_1, 'proposed')

# Filter the comparison data based on the selected month
if df_2 is not None:
    if selected_month == "All":
        filtered_df_2 = df_2  # Show all data if 'All' is selected
    else:
        filtered_df_2 = df_2[df_2["Month"] == selected_month]  # Filter data based on selected month

    # Calculate energy consumption for comparison data (filtered)
    energy_consumption_2 = calculate_energy_consumption(filtered_df_2, 'comparison')

# Ask the user to input the area in square feet (ft²)
area_input = st.text_input("Enter the area in square feet (ft²):")

# Initialize the area variable as None
area = None

# Check if the user has provided input and if it's not empty
if area_input:
    try:
        # Attempt to convert the input to a float
        area = float(area_input)
    except ValueError:
        # If conversion fails, display an error message
        st.error("Please enter a valid number for the area in square feet.")

# Proceed only if area has been successfully converted to float
if area is not None:
    # Convert the area from square feet (ft²) to square meters (m²)
    m2 = area / 10.7639  # Conversion factor

    # Display the area in square feet and square meters
    st.write(f"Area in square feet: {area:.2f} ft²")
    st.write(f"Area in square meters: {m2:.2f} m²")

# Define the calculate_eui function before it is called
def calculate_eui(energy_consumption, area):
    # Calculate HVAC+DHW EUI
    hvac_dhw_eui_kwh_m2 = (
        energy_consumption["Space Heating"] +
        energy_consumption["Service Water Heating"] +
        energy_consumption["Space Cooling"] +
        energy_consumption["Heat Rejection"] +
        energy_consumption["HVAC Fans"] +
        energy_consumption["Pumps"]
    ) / area
    
    # Convert kWh/m² to kBtu/ft²
    hvac_dhw_eui_kbtu_ft2 = hvac_dhw_eui_kwh_m2 * 0.317  # Conversion factor
  
    
    # Calculate Total EUI
    total_eui_kwh_m2 = energy_consumption["Total"] / area
    
    # Convert kWh/m² to kBtu/ft²
    total_eui_kbtu_ft2 = total_eui_kwh_m2 * 0.317  # Conversion factor
    
    # Return EUI values
    return {
        "HVAC+DHW EUI (kWh/m²)": hvac_dhw_eui_kwh_m2,
        "HVAC+DHW EUI (kBtu/ft²)": hvac_dhw_eui_kbtu_ft2,
        "Total EUI (kWh/m²)": total_eui_kwh_m2,
        "Total EUI (kBtu/ft²)": total_eui_kbtu_ft2
    }


# Assuming energy_consumption_1 is the proposed data and m2 is the area in square meters



# Calculate percentage reduction for each end-use category and display the comparison table
if uploaded_file_1 is not None and uploaded_file_2 is not None:
    # Calculate the percentage reduction for each end-use category
    percentage_reduction = []
    for proposed_value, compare_value in zip(energy_consumption_1.values(), energy_consumption_2.values()):
        # Calculate the absolute percentage reduction and format it
        reduction = abs(((proposed_value - compare_value) / proposed_value) * 100)
        percentage_reduction.append(f"{reduction:.2f}%")

    # Create a DataFrame for the comparison table
    comparison_df = pd.DataFrame({
        "End Use": list(energy_consumption_1.keys()),
        "Proposed Energy Consumption (kWh)": [f"{value:,.0f}" for value in energy_consumption_1.values()],
        "Comparison Energy Consumption (kWh)": [f"{value:,.0f}" for value in energy_consumption_2.values()],
        "Percentage Reduction (%)": percentage_reduction
    })
    
    # Display the comparison table
    st.write("Comparison of Energy Consumption (kWh):")
    st.dataframe(comparison_df)
# If proposed and comparison data files are uploaded, calculate and display EUI table
if uploaded_file_1 is not None and uploaded_file_2 is not None:
    # Calculate EUI for proposed data
    eui_proposed = calculate_eui(energy_consumption_1, m2)
    
    # Calculate EUI for comparison data
    eui_comparison = calculate_eui(energy_consumption_2, m2)

    # Create a DataFrame to display the EUI table
    eui_df = pd.DataFrame({
        "EUI Type": ["HVAC+DHW EUI", "Total EUI"],
        "Proposed (kWh/m²)": [f"{eui_proposed['HVAC+DHW EUI (kWh/m²)']:.2f}",
                              f"{eui_proposed['Total EUI (kWh/m²)']:.2f}"],
        "Proposed (kBtu/ft²)": [f"{eui_proposed['HVAC+DHW EUI (kBtu/ft²)']:.2f}",
                               f"{eui_proposed['Total EUI (kBtu/ft²)']:.2f}"],
        "Comparison (kWh/m²)": [f"{eui_comparison['HVAC+DHW EUI (kWh/m²)']:.2f}",
                                f"{eui_comparison['Total EUI (kWh/m²)']:.2f}"],
        "Comparison (kBtu/ft²)": [f"{eui_comparison['HVAC+DHW EUI (kBtu/ft²)']:.2f}",
                                 f"{eui_comparison['Total EUI (kBtu/ft²)']:.2f}"]
    })

    # Display the EUI table with a title
    st.write("Energy Use Intensity (EUI) Table:")
    st.dataframe(eui_df)
# Calculate GHG emissions for proposed and comparison data
def calculate_ghg_emissions(energy_consumption):
    # Emission factor (kgCO2e per kWh)
    emission_factor = 108.72
    
    # Calculate total energy consumption in MWh to kWh conversion and apply emission factor
    total_energy_kWh = energy_consumption["Total"]
    ghg_emission_kgCO2e = (total_energy_kWh *3412/1000000)*emission_factor # Convert to kgCO2e
    
    # Convert kgCO2e to tCO2e (metric tons)
    ghg_emission_tCO2e = ghg_emission_kgCO2e / 1000
    
    # Calculate HVAC only emissions
    hvac_energy_kWh = (
        energy_consumption["Space Heating"] +
        energy_consumption["Space Cooling"] +
        energy_consumption["HVAC Fans"] +
        energy_consumption["Pumps"]
    )*3412/1000000  # Convert from MWh to kWh
    hvac_ghg_emission_kgCO2e = hvac_energy_kWh * emission_factor / 1000  # Convert to kgCO2e
    
    # Convert kgCO2e to tCO2e
    hvac_ghg_emission_tCO2e = hvac_ghg_emission_kgCO2e 
    
    # Return a dictionary containing GHG emission values
    return {
        "GHG Emission (kgCO2e)": ghg_emission_kgCO2e,
        "GHG Emission (tCO2e)": ghg_emission_tCO2e,
        "GHG Emission (tCO2e) HVAC only": hvac_ghg_emission_tCO2e
    }

# Check if proposed and comparison data files are uploaded
if uploaded_file_1 is not None and uploaded_file_2 is not None:
    # Calculate GHG emissions for proposed data
    ghg_emissions_proposed = calculate_ghg_emissions(energy_consumption_1)
    
    # Calculate GHG emissions for comparison data
    ghg_emissions_comparison = calculate_ghg_emissions(energy_consumption_2)
    
    # Create a DataFrame for GHG emissions
    ghg_df = pd.DataFrame({
        "GHG Emission": ["GHG Emission (kgCO2e)", "GHG Emission (tCO2e)", "GHG Emission (tCO2e) HVAC only"],
        "Proposed": [f"{ghg_emissions_proposed['GHG Emission (kgCO2e)']:.3f}",
                     f"{ghg_emissions_proposed['GHG Emission (tCO2e)']:.3f}",
                     f"{ghg_emissions_proposed['GHG Emission (tCO2e) HVAC only']:.3f}"],
        "Comparison": [f"{ghg_emissions_comparison['GHG Emission (kgCO2e)']:.3f}",
                       f"{ghg_emissions_comparison['GHG Emission (tCO2e)']:.3f}",
                       f"{ghg_emissions_comparison['GHG Emission (tCO2e) HVAC only']:.3f}"]
    })

    # Display the GHG emissions table
    st.write("GHG Emissions (Greenhouse Gas) Table:")
    st.dataframe(ghg_df)
