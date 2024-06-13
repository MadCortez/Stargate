<h1>Stargate Test Task</h1>

# National Bank of the Republic of Belarus Api

### Made by Pestunov Ilya

## How to get started on Windows
* Clone this repo
```
git clone https://github.com/MadCortez/Stargate
```
* Go to dir with repo
```
cd Stargate
```
* Install requirements
```
pip install -r requirements.txt
```
* Start
```
py main.py
```

## Usage
* To get rate for all values use
```
http://localhost:5000/rates?date={date}
Where date in format yyyy-mm-dd
Example: http://localhost:5000/rates?date=2023-06-12
```
* To get rate for value by it's code and date use
```
http://localhost:5000/rate?date={date}&code={code}
Where date in format yyyy-mm-dd, code - number
Example: http://localhost:5000/rate?date=2023-06-12&code=431
```
* To get logs
```
http://localhost:5000/logs
```
