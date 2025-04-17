## 📊 Pathfinding & Visualization Toolkit

This project provides a modular toolkit for computing and visualizing optimal paths or routes based on custom algorithms. It includes a core algorithm module and a visualizer to render results interactively using Python libraries.

---

### 🧠 Features

- Custom pathfinding or optimization algorithm (`algorithm.py`)
- Visualization of results with support for maps or plots (`visualize.py`)
- Leverages scientific and geospatial libraries for high-quality analysis
- Easy-to-modify code for adapting to different pathfinding use cases

---

### 📁 File Descriptions

- `algorithm.py`  
  Contains the core logic for computing routes, analyzing paths, or processing data using custom algorithms. Includes functions to create the graph out of the dataframe and find the path from start to end.

- `visualize.py`  
  Uses selenium to automate plotting points on the google maps.

- `requirements.txt`  
  Lists all Python dependencies needed to run the project, including:
  - `pandas`, `numpy`, `scipy`: for numerical and data manipulation
  - `matplotlib`: for plotting and visualizations
  - `selenium`: for web interaction (possibly used to scrape or automate data sources)
  - `rustworkx`: for graph-based operations
  - `geopy`: for geographic coordinate handling

---

### 🚀 Getting Started

#### 1. Clone the repository
```bash
git clone <your-repo-url>
cd <project-folder>
```

#### 2. Set up a virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

#### 3. Install dependencies
```bash
pip install -r requirements.txt
```

#### 4. Run the algorithm
```bash
python algorithm.py
```

#### 5. Visualize results
```bash
python visualize.py
```

---

### 🛠 Requirements

- Python 3.8+
- Internet connection (if using `selenium` for scraping or map services)
- WebDriver for Selenium (e.g., ChromeDriver or GeckoDriver)

---

### 📌 Notes

- Make sure to configure Selenium correctly if used in the visualization or data acquisition steps.
- If working with geographic data, ensure your inputs (e.g., coordinates, elevation files) are in the right format.
- Visualization behavior may depend on the data output by `algorithm.py`.

---