import numpy as np
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QCheckBox,
    QComboBox,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QGroupBox,
    QScrollArea,
)
from PySide6.QtCore import Qt

import numpy as np
from scipy.optimize import fsolve

# Constants
R = 8.314  # J/(mol·K)

class GasEstimationApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Natural Gas Properties Estimation")
        self.setGeometry(300, 200, 800, 600)

        # Main layout
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # List of possible gas components
        self.available_components = [
            "Ethane (C₂H₆)", "Propane (C₃H₈)", "Butane (C₄H₁₀)", "Pentane (C₅H₁₂)",
            "Hexane (C₆H₁₄)", "Heptane (C₇H₁₆)", "Octane (C₈H₁₈)", "Nonane (C₉H₂₀)",
            "Decane (C₁₀H₂₂)", "Carbon Dioxide (CO₂)", "Nitrogen (N₂)", "Oxygen (O₂)",
            "Hydrogen (H₂)", "Hydrogen Sulfide (H₂S)", "Helium (He)", "Water Vapor (H₂O)",
            "Benzene (C₆H₆)", "Toluene (C₇H₈)", "Xylenes (C₈H₁₀)", "Ethylene (C₂H₄)",
            "Propylene (C₃H₆)", "Carbonyl Sulfide (COS)", "Carbon Disulfide (CS₂)",
            "Argon (Ar)", "Neon (Ne)"
        ]

        # Step 1: Gas Component Selection
        self.create_gas_selection_screen()

    def create_gas_selection_screen(self):
        # Gas selection screen
        self.gas_selection_group = QGroupBox("Select Gas Components")
        gas_selection_layout = QHBoxLayout()  # Main layout for two columns

        # Create two vertical layouts for stacking components into two columns
        left_column = QVBoxLayout()
        right_column = QVBoxLayout()

        # Checkboxes for each component
        self.component_checkboxes = {}
        half_index = len(self.available_components) // 2

        # Add checkboxes to two columns
        for i, component in enumerate(self.available_components):
            checkbox = QCheckBox(component)
            self.component_checkboxes[component] = checkbox
            if i < half_index:
                left_column.addWidget(checkbox)
            else:
                right_column.addWidget(checkbox)

        # Add left and right columns to the main layout
        gas_selection_layout.addLayout(left_column)
        gas_selection_layout.addLayout(right_column)

        # Set layout for the gas selection group
        self.gas_selection_group.setLayout(gas_selection_layout)

        # Next button
        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.create_main_input_screen)

        # Add to main layout
        self.main_layout.addWidget(self.gas_selection_group)
        self.main_layout.addWidget(self.next_button)

    def create_main_input_screen(self):
        # Collect selected components
        self.selected_components = [
            comp
            for comp, checkbox in self.component_checkboxes.items()
            if checkbox.isChecked()
        ]
        if not self.selected_components:
            return

        # Clear the selection screen
        self.clear_layout(self.main_layout)

        # Gas Composition Section with Scroll Area
        gas_composition_group = QGroupBox("Gas Composition")
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        scroll_widget = QWidget()
        gas_composition_layout = QFormLayout(scroll_widget)

        # Add input fields for each selected component
        self.molar_fraction_inputs = {}
        for component in self.selected_components:
            molar_input = QLineEdit()
            gas_composition_layout.addRow(f"{component} Molar Fraction:", molar_input)
            self.molar_fraction_inputs[component] = molar_input

        scroll_area.setWidget(scroll_widget)
        layout_with_scroll = QVBoxLayout()
        layout_with_scroll.addWidget(scroll_area)
        gas_composition_group.setLayout(layout_with_scroll)

        # Pressure and Temperature Section
        pressure_temp_group = QGroupBox("Pressure and Temperature")
        pressure_temp_layout = QFormLayout()

        self.pressure_input = QLineEdit()
        self.temperature_input = QLineEdit()

        pressure_temp_layout.addRow("Pressure (Pa):", self.pressure_input)
        pressure_temp_layout.addRow("Temperature (K):", self.temperature_input)

        pressure_temp_group.setLayout(pressure_temp_layout)

        # Submit Button
        self.submit_button = QPushButton("Calculate Properties")
        self.submit_button.clicked.connect(self.calculate_properties)

        # Add sections to main layout
        self.main_layout.addWidget(gas_composition_group)
        self.main_layout.addWidget(pressure_temp_group)
        self.main_layout.addWidget(self.submit_button)

    def calculate_properties(self):
            # Retrieve molar fractions, pressure, and temperature
            molar_fractions = {
                component: float(self.molar_fraction_inputs[component].text())
                for component in self.selected_components
            }
            pressure = float(self.pressure_input.text())
            temperature = float(self.temperature_input.text())

            # Define critical properties for each component
            component_data = {
                "Methane": {"T_c": 190.6, "P_c": 4599000, "M": 0.016},
                "Ethane": {"T_c": 305.3, "P_c": 4872000, "M": 0.030},
                # Add more components as needed
            }

            # Calculate Van der Waals constants
            components = []
            for comp, fraction in molar_fractions.items():
                data = component_data.get(comp)
                if data:
                    a = (27 / 64) * (R ** 2 * data["T_c"] ** 2) / data["P_c"]
                    b = (R * data["T_c"]) / (8 * data["P_c"])
                    components.append({"y": fraction, "a": a, "b": b, "M": data["M"]})

            # Apply mixing rules
            a_mix = sum(components[i]["y"] * components[j]["y"] * np.sqrt(components[i]["a"] * components[j]["a"])
                        for i in range(len(components)) for j in range(len(components)))
            b_mix = sum(comp["y"] * comp["b"] for comp in components)
            molar_mass_mix = sum(comp["y"] * comp["M"] for comp in components)

            # Calculate molar volume
            Vm = self.calculate_molar_volume_vdw(pressure, temperature, a_mix, b_mix)
            compressibility_factor = (pressure * Vm) / (R * temperature)
            density = molar_mass_mix / Vm

            # Show results
            self.show_results(Vm, compressibility_factor, density)



    def calculate_molar_volume_vdw(self, P, T, a_mix, b_mix):
        def van_der_waals_eq(Vm):
            return P * Vm**3 - (R * T) * Vm**2 + (P * b_mix + a_mix) * Vm - a_mix * b_mix
        
        # Solve for molar volume Vm
        Vm_initial_guess = (R * T) / P  # Ideal gas approximation
        Vm_solution = fsolve(van_der_waals_eq, Vm_initial_guess)[0]
        return Vm_solution

    def calculate_density(self, Vm):
        # Example placeholder for density calculation
        return 1 / Vm

    def show_results(self, molar_volume, compressibility_factor, density):
        # Clear previous layout
        self.clear_layout(self.main_layout)

        # Display results in a new page
        results_layout = QVBoxLayout()

        results_layout.addWidget(QLabel(f"Molar Volume: {molar_volume:.2f} m³/mol"))
        results_layout.addWidget(QLabel(f"Compressibility Factor: {compressibility_factor:.2f}"))
        results_layout.addWidget(QLabel(f"Density: {density:.2f} kg/m³"))

        # Button to start a new calculation
        new_calc_button = QPushButton("New Calculation")
        new_calc_button.clicked.connect(self.reset_to_start)
        results_layout.addWidget(new_calc_button)

        # Set the new layout to main layout
        self.main_layout.addLayout(results_layout)

    def reset_to_start(self):
        # Clear layout and restart from the beginning
        self.clear_layout(self.main_layout)
        self.create_gas_selection_screen()

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

if __name__ == "__main__":
    app = QApplication([])
    window = GasEstimationApp()
    window.show()
    app.exec()