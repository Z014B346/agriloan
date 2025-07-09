***DISCLAIMER AI was used during this project for front end and structure, I mainly wanted to focus on the logic as this is my own personal learning goal***

This contains a calculator for amortized loans.

### How to use ### 

I have a hosted site at https://amortisedloan.onrender.com/ which is also available as an api in the RapidApi marketplace: https://rapidapi.com/samsewell95/api/agribusiness-loan-calculator/playground/apiendpoint_40c02b7a-fbb6-43b5-acea-a3d99be73d74.

If you wish to run locally for testing you can use this command in cmd: uvicorn main::app --reload (just make sure the directory is pointing to where the main.py file is)

current accepted variables:<br>
  principle <br>
  interest rate<br>
  term (years)<br>
  Payments per year<br>
  seasonal months (Month on which you pay, int range 1-12)<br>
  interest only years (how many years are interest only)<br>
