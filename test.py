
import requests
import json
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.patches as mpatches
import matplotlib as mpl
from matplotlib.colors import Normalize
import numpy as np
import time

N = 1000

def makeQuery(size=25, sub='floridaman', date=''):

	url = 'https://api.pushshift.io/reddit/search/submission'
	url += '/?size=' + str(size)
	url += '&sort=desc&subreddit=' + sub

	date_format = "%Y-%m-%d"
	tm_before, tm_after = None, None
	date_today = time.strftime(date_format, time.localtime())

	if date == '':
		date = date_today

	if date == date_today:
		tm_before = time.localtime()
		tm_after = time.strptime(time.strftime(date_format, tm_before), date_format)
	else:
		tm_after = time.strptime(date, date_format)
		tm_before = time.localtime(time.mktime(tm_after) + 24 * 60 * 60)

	q = { 
		"url": url, 
		"size": size, 
		"before": int(time.mktime(tm_before)), 
		"after": int(time.mktime(tm_after)),
		"t0d2mfy2ekwjkln0u93d" : True
	}

	print('Contructed Query')

	return q

def getPushshiftData(query, filename=''):

	orig_url = query["url"]
	headers={'User-Agent': "Post downloader by /u/Hura_Italian"}
	if "t0d2mfy2ekwjkln0u93d" not in query:
		print("Please use makeQuery()")
		return

	print("Fetching all posts rfom " + 
		time.strftime("%Y/%m/%d-%H:%M:%S to ", time.localtime(query["after"])) +
		time.strftime("%Y/%m/%d-%H:%M:%S.", time.localtime(query["before"]))
	)

	orig_url += '&after=' + str(query["after"])

	new_url = ''
	response = ''
	count = 0
	all_data = []
	while True:
		new_url = orig_url + '&before=' + str(query["before"])
		response = requests.get(new_url, headers=headers)
		try:
			text = response.text
			json_data = json.loads(text)
		except:
			print("Invalid json: ")
			print(text)
			break
		
		if 'data' not in json_data or len(json_data['data']) == 0:
			break

		all_data = all_data + json_data['data']
		print("Fetched " + str(len(all_data)) + " posts.")
		query["before"] = json_data['data'][-1]['created_utc'] - 1
		count += len(json_data['data'])

	# r = requests.get(query["url"])
	print('Content Fetched.')
	if filename != '':
		with open(filename, 'w') as outfile:
			json.dump(all_data, outfile)
	print('Content Written.')
	return all_data


def readText(file):
	text = ''
	with open(file, 'r') as f:
		text = f.read()
	json_data = json.loads(text)
	return json_data


def plotStrengthTime(content, date, sub):

	created_on = [ int(post['created_utc']) for post in content ]
	upvotes = [ int(post['score']) for post in content ]
	color = cm.gnuplot2

	NBins = 100
	num, bins, patches = plt.hist(created_on, bins=NBins)

	votes_arr, post_idx = [], 0

	for i in num:
		votes = sum(upvotes[post_idx : post_idx + int(i)])
		post_idx += int(i)
		votes_arr.append(int(votes/i))

	max_votes, min_votes = max(votes_arr), min(votes_arr)
	avg_votes = (min_votes + max_votes)/2
	norm = Normalize(vmin=min_votes, vmax=max_votes)
	getColor = lambda x: color(norm(x))

	for i in range(NBins):
		patches[i].set_facecolor(getColor(votes_arr[i]))

	bin_w = 15 * (max(bins) - min(bins)) / (NBins - 1)
	ticks = np.arange(min(bins)+bin_w/2, max(bins), bin_w)
	timestamps = map(lambda x: time.strftime('%H:%m\nIST', time.localtime(x)), ticks)
	
	plt.legend(handles=[
		mpatches.Patch(color=getColor(max_votes), label='Avg score ' + str(max_votes)),
		mpatches.Patch(color=getColor(avg_votes), label='Avg score ' + str(int(avg_votes))),
		mpatches.Patch(color=getColor(min_votes), label='Avg score ' + str(min_votes)),
		mpatches.Patch(color=(0,0,0,0), label=str(len(content)) + ' posts.'),
		mpatches.Patch(color=(0,0,0,0), label=str(sum(upvotes)) + ' upvotes.')
	], framealpha=0.0)

	plt.title('r/'+sub+'\nAvg Post Score vs Local Time on ' + date)
	plt.gcf().set_facecolor((0.47, 0.47, 0.42))
	plt.gca().set_facecolor((0.47, 0.47, 0.42))
	plt.ylabel('Number of Posts', fontsize=18)
	plt.xticks(ticks, list(timestamps))
	plt.savefig(sub + ':' + date, dpi=300, facecolor=(0.47, 0.47, 0.42))
	plt.show()

date='2020-05-20'
sub='prequelmemes'
# query = makeQuery(size=1000, sub=sub, date=date)
# content = getPushshiftData(query, '')

content = readText('data.txt')
plotStrengthTime(content, date, sub)