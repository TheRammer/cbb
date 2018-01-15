#!/usr/bin/env python
import json
import subprocess
import sys

schools_fn = "schools.json"

'''
cbb.py - tally votes from http://cbbpoll.com/poll/2018/6?detailed=true

'''

def scrape_ballot(ballot):
    data = []
    b = ballot.split("<td>")
    for i in range(1,len(b)):
        if i == 1:
            user = b[i].split('</span>')[1].split('</td>')[0]
            data.append(user)
        else:
            college = b[i].split('alt="')[1].split(' Logo')[0]
            data.append(college)
    return data

def scrape_ballots(ballots):
    ballots_list = []
    for b in ballots:
        ballots_list.append(scrape_ballot(b))
    return ballots_list

def scrape_page(url):
    if len(sys.argv) > 1:                 # curl -o 1811.html http://cbbpoll.com/poll/2018/11?detailed=true
        cmd = ['/bin/cat', sys.argv[1]]   # python ./cbb.py 1811.html 
    else:
        cmd = ['/usr/bin/curl', '--silent', '-XGET', url]

    lines = subprocess.check_output(cmd).splitlines()

    start = False
    ballots = []
    for line in lines: 
        if "Official Ballot" in line:
            start = True
        if "Provisional Ballot" in line:
            start = False
        if start:
            l = line.strip()
            if l.startswith("<td>"):
                ballots.append(l)

    return scrape_ballots(ballots)
  

def update_schools(ballots):
    # {
    # "University of Florida": {"name":"Florida", "bgcolor":"#F74827", "fontcolor":"#1C28A3"},
    # ...
    # }

    with open(schools_fn) as infile:    
        schools = json.load(infile)

    school_names = schools.keys()
    
    for ballot in ballots:
        for i in range(1,len(ballot)):
            if ballot[i] not in school_names:
                school_names.append(ballot[i])
                schools[ballot[i]] = {"name":ballot[i], "bgcolor":"#FFFFFF", "fontcolor":"#000000"}

    with open(schools_fn, 'w') as outfile:
        json.dump(schools, outfile, indent=4, separators=(',', ': '), sort_keys=True)

    return schools

def generate_table_header(num_votes):
    places = ''
    for i in range(1,num_votes+1):
        places += '<th>%s</th>'%(i)
    h = '''
<tr><th>&nbsp;</th><th>Team</th>%s<th>Votes</th><th>Score</th>
'''%(places)
    return h

def generate_vote_data(votes):
    h = ''
    for vote in votes:
        if vote == 0:
            h += '<td align="center"> </td>'
        else:
            h += '<td align="center">%s</td>'%(vote)
    return h


def generate_ranked_table(schools, ranked_schools):
    h = ''
    place = 0
    for rank in ranked_schools:
        place += 1
        name = rank['name']
        short_name = schools[name]['name']
        bgcolor = schools[name]['bgcolor']
        fontcolor = schools[name]['fontcolor']
        votes = generate_vote_data(rank['votes'])
        total_votes = rank['total_votes']
        score = rank['score']
        if score > 0:
            h += '''
<tr><td>%s</td><td align="center" bgcolor="%s"><font color="%s">%s</font></td>%s<td align="center">%s</td><td align="center"> %s</td></tr>
'''%(place, bgcolor, fontcolor, short_name, votes, total_votes, score)

    html = '''
<table border=1>
%s
%s
%s
</table>
'''%(generate_table_header(len(rank['votes'])), h, generate_table_header(len(rank['votes'])))

    return html

def main():

    url = 'http://cbbpoll.com/poll/2018/10?prov=true&detailed=true'

    # scrape the web page for the ballots
    ballots = scrape_page(url)

    # how many places are there?
    #num_places = len(ballots[0])-1
    num_places = 25

    # a config file for schools (automatically updates if new schools are voted for)
    schools = update_schools(ballots)

    # what schools does the config file know?
    school_names = schools.keys()
    
    # how many schools does the config file know?
    num_schools = len(school_names)
    
    # a dictionary of all the schools and their votes per place
    school_scores = {}

    for name in school_names:
        school_scores[name] = [0] * num_places

    # map the school name on the vote to an actual count
    for ballot in ballots:
        # for each place
        #for i in range(1,len(ballot)):
        for i in range(1,26):
            school_scores[ballot[i]][i-1] += 1

    school_summaries = {}

    for school in school_scores.keys():
        summary = {'name':school, 'votes':school_scores[school], 'score':0, 'total_votes':0}
        # 1st place gets num_places points, 2nd place gets num_places-1 points, etc.
        factor = 25
        for i in range(0,len(ballot)-1):
            summary['score'] += school_scores[school][i] * factor
            summary['total_votes'] += school_scores[school][i]
            factor -= 1
        school_summaries[school] = summary 
            
    ranked_schools = []

    num_schools_mentioned = len(school_summaries.keys())
 
    for i in range(0,num_schools_mentioned-1):
        highest = -1 
        highest_school = ""
        for name in school_summaries.keys():
            if school_summaries[name]['score'] > highest:
                highest = school_summaries[name]['score']
                highest_school = name
        ranked_schools.append(school_summaries[highest_school])
        school_summaries.pop(highest_school)

    ranked_html_table = generate_ranked_table(schools, ranked_schools)

    html = """
<html>
<head>
</head>
<body>
%s
</body>
</html>
"""%(ranked_html_table)

    
    with open('ranked.html', 'w') as outfile:
        outfile.write(html)


if __name__ == "__main__":
    main()
