# NS_train
Program that take NS history data from your NS account and gives you informations about your time spent in transport, amount of money spent and km travelled (by month and day of week for each category)

argument :
-ns : your travel history in csv file (can be found at https://www.ns.nl/en/mijnns#reishistorie ) 
If you don't have any travel history you can use sample.csv from this repo to try.

The program use dash package to plot everything so you need to copy paste the local adress to view it in your browser.

run in terminal :
cd NS_train
python main.py -ns {your csv}
