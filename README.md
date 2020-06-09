# COVID LA Risk Index

## Introductions
The purpose of this project was (1) to evaluate disparities in socioeconomic factors across LA County neighborhoods using the community need index (CNI), (2) to study the role these disparities might have played in the spread of COVID-19 based on count of positive cases, and (3) to develop an application to help users evaluate the risk of leaving their home based on a personal risk profile, a neighborhood based risk profile, and an activity based risk profile (i.e. risks associated with type of activity, getting to activity, and location of activity).

## Directory overview
There are three folders:
1. `covid_neighborhood_risk_model.ipynb`: The Jupyter Notebook contains a decision tree model for calculating the neighborhood risk.
2. The web app (`app`) is built with HTML and JavaScript and can be easily run on the computer. It can be viewed on the web at https://covid-risk-la.now.sh/. 
3. The risk engine (`api`) is a Python/Flask app, with the program itself accessible at `app.py`, which is responsible for calculating an individual's risk profile and delivering it to the web app
