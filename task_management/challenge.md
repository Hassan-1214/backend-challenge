# Challenge Instructions

## Setting Up the Django Application

1. **Navigate to the `task_management` folder:**

**With Makefile** Install make (if not already installed):

- On macOS with Homebrew:

    ```bash
    brew install make
    ```
- On Linux:

    ```bash
    sudo apt-get install make
    ```
**Run all tasks using make:**

In the root of your project, run:

```bash
  make all
```
**This will execute the following tasks:**

1. Run Django server at 0.0.0.0:8080
2. Make migrations
3. Apply migrations
4. Run tests with pytest
5. Run flake8 for linting
6. Open Django shell
7. Install requirements after making env

# OR
   ```bash
   cd task_management
   ```
2. **Create a virtual environment:**
    ```bash
   python -m venv env
    ```
3. **Activate the virtual environment:**

   - On Windows:
    ```bash
    .\env\Scripts\activate
    ```
   - On macOS/Linux:

    ```bash
   source env/bin/activate
   ```
4. **Install the required packages:**

    ```bash
    pip install -r requirements.txt
    ```

5. **Run tests:**

    ```bash
    pytest
    ```