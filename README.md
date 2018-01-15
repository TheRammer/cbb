# cbb
Tally ccbpoll.com's ballots by team and output "ranked.html".

Usage:
 1) get all ballots with: curl -o poll_18_11.html http://cbbpoll.com/poll/2018/11?detailed=1
 2) run the script: python ./cbb.py poll_18_11.html
 
 Or
 1) modify the "url" variable in the script (first line in "main") for current week
 2) run the script with no arguments: python ./cbb.py
 
 File schools.json is automatically updated.   However, school colors will default to black text on white background.
