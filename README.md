# HAM Radio Class 2 Practice Test

A local Bulgarian-language practice quiz based on the Class 2 amateur-radio question sets. The web app runs on your computer; it is not a hosted service.

## Run on Windows

Double-click `run_web.bat`. It starts the app with `py -3` if available, otherwise tries `python`. If neither is found, it asks whether to install Python 3.13 using `winget`; choosing **Y** installs it for the current user and continues, while choosing **N** cancels. If `winget` is unavailable or installation fails, install Python 3 manually and run the launcher again.

You can also start the app manually from the project directory:

```powershell
python web_app.py
```

Open `http://localhost:8000` if the browser does not open automatically. Stop the server with Ctrl+C. The launcher changes to the project directory first, so it can be run from elsewhere.

The quiz itself uses Python's standard library and the included question data.

## Run on Linux and macOS

Install Python 3.10 or newer, then make the launcher executable and run it from a terminal:

```sh
chmod +x run_web.sh
./run_web.sh
```

The script uses `python3` (or falls back to `python`), changes to the project directory, and starts the local server. Open `http://localhost:8000` if it does not open automatically. Stop the server with Ctrl+C.

## Question Data

The generated question banks and figure crops are included under `class2/`. Source PDFs and the extraction script are excluded from Git.

The simulated exam selects 60 questions: 28 from Section 1, 13 from Section 2, and 19 from Section 3. Passing requires at least 48 correct answers (80%).
