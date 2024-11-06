from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QCheckBox, QComboBox, QPushButton,
    QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox, QScrollArea
)
from PySide6.QtCore import Qt


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
            "Methane (CH₄)", "Ethane (C₂H₆)", "Propane (C₃H₈)", "Butane (C₄H₁₀)",
            "Pentane (C₅H₁₂)", "Hexane (C₆H₁₄)", "Carbon Dioxide (CO₂)", "Nitrogen (N₂)"
        ]

        # Step 1: Gas Component Selection
        self.create_gas_selection_screen()

    def create_gas_selection_screen(self):
        # Gas selection screen
        self.gas_selection_group = QGroupBox("Select Gas Components")
        gas_selection_layout = QVBoxLayout()

        # Checkboxes for each component
        self.component_checkboxes = {}
        for component in self.available_components:
            checkbox = QCheckBox(component)
            gas_selection_layout.addWidget(checkbox)
            self.component_checkboxes[component] = checkbox

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
            comp for comp, checkbox in self.component_checkboxes.items() if checkbox.isChecked()
        ]
        if not self.selected_components:
            # If no components are selected, show the selection screen again
            return

        # Clear the selection screen
        self.clear_layout(self.main_layout)

        # Scrollable area for inputs
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        input_widget = QWidget()
        input_layout = QFormLayout()

        # Gas Composition Section
        gas_composition_group = QGroupBox("Gas Composition")
        gas_composition_layout = QFormLayout()

        # Add input fields for each selected component
        self.molar_fraction_inputs = {}
        for component in self.selected_components:
            molar_input = QLineEdit()
            gas_composition_layout.addRow(f"{component} Molar Fraction:", molar_input)
            self.molar_fraction_inputs[component] = molar_input

        gas_composition_group.setLayout(gas_composition_layout)
        input_layout.addWidget(gas_composition_group)

        # Pressure and Temperature Section
        pressure_temp_group = QGroupBox("Pressure and Temperature")
        pressure_temp_layout = QFormLayout()

        self.pressure_input = QLineEdit()
        self.temperature_input = QLineEdit()

        pressure_temp_layout.addRow("Pressure (Pa):", self.pressure_input)
        pressure_temp_layout.addRow("Temperature (K):", self.temperature_input)

        pressure_temp_group.setLayout(pressure_temp_layout)
        input_layout.addWidget(pressure_temp_group)

        # EOS Selection Section
        eos_group = QGroupBox("Equation of State Selection")
        eos_layout = QHBoxLayout()

        self.eos_dropdown = QComboBox()
        self.eos_dropdown.addItems(["Peng-Robinson", "Redlich-Kwong", "Soave-Redlich-Kwong"])
        eos_layout.addWidget(QLabel("Select EOS:"))
        eos_layout.addWidget(self.eos_dropdown)

        eos_group.setLayout(eos_layout)
        input_layout.addWidget(eos_group)

        # Additional Parameters Section
        additional_params_group = QGroupBox("Additional Parameters")
        additional_params_layout = QFormLayout()

        self.critical_pressure_input = QLineEdit()
        self.critical_temperature_input = QLineEdit()
        self.acentric_factor_input = QLineEdit()

        additional_params_layout.addRow("Critical Pressure (Pa):", self.critical_pressure_input)
        additional_params_layout.addRow("Critical Temperature (K):", self.critical_temperature_input)
        additional_params_layout.addRow("Acentric Factor:", self.acentric_factor_input)

        additional_params_group.setLayout(additional_params_layout)
        input_layout.addWidget(additional_params_group)

        # Submit Button
        self.submit_button = QPushButton("Calculate Properties")
        self.submit_button.clicked.connect(self.calculate_properties)
        input_layout.addWidget(self.submit_button)

        # Set input layout to scrollable area
        input_widget.setLayout(input_layout)
        scroll_area.setWidget(input_widget)

        # Add the scrollable area to the main layout
        self.main_layout.addWidget(scroll_area)

    def calculate_properties(self):
        # Retrieve molar fractions for each selected component
        molar_fractions = {
            component: self.molar_fraction_inputs[component].text() for component in self.selected_components
        }

        # Retrieve pressure, temperature, EOS, and additional parameters
        pressure = self.pressure_input.text()
        temperature = self.temperature_input.text()
        selected_eos = self.eos_dropdown.currentText()
        critical_pressure = self.critical_pressure_input.text()
        critical_temperature = self.critical_temperature_input.text()
        acentric_factor = self.acentric_factor_input.text()

        # Display or process the input values (print for example purposes)
        print("Selected Components and Molar Fractions:", molar_fractions)
        print("Pressure:", pressure, "Temperature:", temperature)
        print("Selected EOS:", selected_eos)
        print("Additional Parameters:", f"Critical Pressure: {critical_pressure} Pa",
              f"Critical Temperature: {critical_temperature} K", f"Acentric Factor: {acentric_factor}")

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