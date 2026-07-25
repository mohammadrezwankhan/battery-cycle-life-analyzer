# Battery Cycle Life Analyzer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Battery Cycle Life Analyzer** is a robust, open-source MATLAB/Simulink utility designed to help engineers and researchers fit degradation models to battery cycling data, project remaining useful life (RUL), and generate publication-ready figures.

Whether you're dealing with Li-ion cells for electric vehicles (EVs), battery energy storage systems (BESS), or 18650s for DIY projects, this tool provides a flexible architecture for comprehensive life cycle analysis.

## 🚀 Key Features
- **Degradation Modeling:** Apply empirical and semi-empirical models to track capacity fade and internal resistance growth.
- **RUL Projection:** Estimate the Remaining Useful Life of battery cells based on historical cycling data.
- **MATLAB/Simulink Integration:** Seamlessly integrates with existing Simulink battery models.
- **Publication-Ready Plots:** Automatically generates high-quality degradation curves.

## 🛠️ Installation & Prerequisites
### Prerequisites
- MATLAB (R2021a or newer recommended)
- Optimization Toolbox (for model fitting)
- Simulink (optional, for system-level integration)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer.git
   ```
2. Add the directory to your MATLAB path:
   ```matlab
   addpath(genpath('battery-cycle-life-analyzer'))
   savepath
   ```

## 📈 Quick Start / Usage
1. **Load your cycling data:** Ensure your data is formatted as a table or structure with cycle number and corresponding capacity/resistance values.
2. **Run the analyzer:**
   ```matlab
   % Example usage
   data = load('sample_battery_data.mat');
   results = analyzeCycleLife(data, 'ModelType', 'Empirical');
   
   % Generate plots
   plotDegradationCurve(results);
   ```

## 🧠 How the Models Work
The underlying cycle life models utilize non-linear least squares fitting to map capacity retention against cycle number and depth of discharge (DoD). The primary degradation equation considers:
- Solid Electrolyte Interphase (SEI) layer growth (typically $t^{1/2}$ dependency).
- Active material loss.
- Stress-induced micro-cracking over extended cycles.

## 🤝 Contributing
We welcome contributions! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to get started.

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.