Here’s the updated README to ensure the React codebase is on version `v18.3.1` before running the analysis in the notebook:

---

# UZH FSS SE-01 - React Codebase Analysis

## Repository Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/schwarzjakob/uzh_fss_se01.git
   ```
2. Change into the newly created directory:
   ```bash
   cd uzh_fss_se01
   ```
3. Download the React codebase by running:
   ```bash
   git clone https://github.com/facebook/react
   ```
4. Check out the required React version:
   ```bash
   cd react
   git checkout v18.3.1
   cd ..
   ```
   > **Note:** React files are included in `.gitignore` to avoid adding them to this repository. This ensures we analyze the correct version, `v18.3.1`, in the Jupyter Notebook.

## Jupyter Notebook Environment

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   ```
2. Activate the environment:
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     .\venv\Scripts\activate
     ```
3. Install required packages:
   ```bash
   pip3 install -r requirements.txt
   ```

---

With this setup, you’re ready to run the Jupyter notebook. The analysis will use the checked-out `v18.3.1` version of React.