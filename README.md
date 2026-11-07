# HAM Radio Class 2 Practice Test

A local Bulgarian-language practice quiz based on the Class 2 amateur-radio question sets. The web app runs on your computer; it is not a hosted service.

## Requirements

- Python 3.10 or newer
- pip

## Setup

From the project directory, create and activate a virtual environment, then install the dependencies:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process RemoteSigned` in that terminal and activate again. Alternatively, run the launcher directly; it uses `.venv` automatically when present.

## Run

```powershell
python web_app.py
```

Or double-click `run_web.bat`. Open `http://localhost:8000` if the browser does not open automatically. Stop the server with Ctrl+C.

The launcher starts the app from the project folder, so it can also be invoked from another working directory.

## Question Data

The quiz runs from the generated question banks and figure crops in `class2/`; the source PDFs are not needed at runtime. `extract_questions.py` is optional and only needed to regenerate the question banks and crops. Place authorized source PDFs in `class2/` before running it:

```powershell
python extract_questions.py
```

PDFs are excluded from Git by `.gitignore` because they contain answer keys and may have distribution restrictions.

The simulated exam selects 60 questions: 28 from Section 1, 13 from Section 2, and 19 from Section 3. Passing requires at least 48 correct answers (80%).

## GitHub Visibility

`class2/questions.json` contains the correct answers, and the local web API currently sends that file to the browser for scoring. The source PDFs also include answer keys. **Do not publish this repository publicly if those answers should remain private.** Use a private repository or remove the answer-bearing data and revise the app's scoring/data flow before making it public.

The PDFs may also have distribution or copyright restrictions; verify permission before uploading them.