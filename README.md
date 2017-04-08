# workout-flask
A REST API for accessing some running data, python-flavored.

# Prerequisites
1. A database storing running data
1. python + pip

# Installation
1. Clone this repository
1. pip install -r requirements.txt
1. python manage.py

# Running the service
1. python app.py

# Getting started
The API is pretty simple. CRUD operations on the /runs endpoint add/update/remove runs.
The /stats endpoints are for statistics,
 * /last/<int:days> returns statistics about the last <int:days> of runs. This defaults to seven days
   * number of miles run during the period
   * total elapsed time running during the period
 * /ytd returns statistics about runs in the current year, starting January 1. Data returned includes
   * number of miles run
   * total elapsed time for current year

