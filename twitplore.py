import tweepy
import urllib2
import sys
import json
import time
import traceback
import csv

# tweepy authentications
consumer_key="your_key"
consumer_secret="your_key"

access_token="your_key"
access_token_secret="your_key"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

def format_output(targets):
  my_json = json.dumps(targets)
  f = open("analysis.json","w")
  f.write(my_json + "\n")
  f.close()
  
  print "Your json file has been created"

def csv_output(targets):
  f = csv.writer(open("analysis.csv","wb+"),quoting=csv.QUOTE_NONNUMERIC)
  
  f.writerow(["name","twitter_url","name","description","location","url","wordpress","followers","following"])
  
  for entry in targets:
    # CSV Writer extremely unforgiving of missing data, so create temp variable
    temp = {}
    temp['screen_name'] = entry['screen_name'].encode('unicode-escape') if 'screen_name' in entry and entry['screen_name'] else ''
    temp['twitter_url'] = "https://twitter.com/#!/"+entry['screen_name'].encode('unicode-escape') if 'screen_name' in entry and entry['screen_name'] else ''
    temp['name'] = entry['name'].encode('unicode-escape') if 'name' in entry and entry['name'] else ''
    temp['description'] = entry['description'].encode('unicode-escape') if 'description' in entry and entry['description'] else ''
    temp['location'] = entry['location'].encode('unicode-escape') if 'location' in entry and entry['location'] else ''
    temp['url'] = entry['url'] if 'url' in entry and entry['url'] else ''
    temp['wp_url'] = entry['wp_url'] if 'wp_url' in entry and entry['wp_url'] else ''
    temp['followers'] = entry['followers']
    temp['following'] = entry['following']
    
    f.writerow([temp['screen_name'], temp['twitter_url'], temp['name'], temp['description'], temp['location'], temp['url'], temp['wp_url'], temp['followers'],temp['following']])
  
  print "Your csv file has been created"    


api = tweepy.API(auth)

# Step 1:
# Get usernames and test that valid
def get_usernames():
  username_text = raw_input("Enter the Twitter usernames you want to explore. Comma-separated: ")
  
  usernames_raw = username_text.split(',')
  
  usernames = []
  for username in usernames_raw:
    if username.strip() not in usernames:
      usernames.append(username.strip())
  
  for username in usernames:
    try:
      target = api.get_user(screen_name=username)
    except tweepy.error.TweepError:
      print "The user %s doesn't exist", username
      usernames = []
      break
  
  return usernames

usernames = []
while len(usernames) == 0:
  usernames = get_usernames()


print"\nYou entered:"
for username in usernames:
  print username
print ""

# Step 2:
# Get keywords
keywords= []
def get_keywords():
  raw_keywords = raw_input("Give us some keywords to explore. Separate keywords with commas: ")
  
  raw_keys = raw_keywords.split(',')
  keywords = []
  
  for key in raw_keys:
    if len(key.strip()) > 0 and key.strip().lower() not in keywords:
      keywords.append(key.strip().lower())
  
  return keywords

while len(keywords) == 0:
  keywords = get_keywords()  


print "\nYou entered the keyword(s):"
for word in keywords:
  print word
print ""

# Step 3:
# Get followers or following
follow = True
def get_relationship():
  relationship = True
  valid_entry = False
  while valid_entry == False:
    entry = raw_input("\nDo you want to analyze followers (type 1) or following (type 2):")
    if entry == "1":
      valid_entry = True
      relationship = True
    elif entry == "2":
      valid_entry = True
      relationship = False
  
  return relationship

follow = get_relationship()

if follow == True:
  print "You're analyzing followers"
else:
  print "You're analyzing following"

names = []
targets = []
for username in usernames:
  if follow == True:
    cursor = tweepy.Cursor(api.followers, id=username)
  else:
    cursor = tweepy.Cursor(api.friends, id=username)
  
  # Can never be 100% sure when API calls going to be used up, so wrap in error block
  # Get 350 per hour
  try:
    counter = 0
    for user in cursor.items():
      #if api.rate_limit_status()['remaining_hits'] < 10:
      #  print "Running out of API calls so going to sleep temporarily"
      #  time.sleep(11)
    
      # Only add if not already in targets and keyword match
      keyword_match = False
      for word in keywords:
        if user.description and word in user.description.lower():
          keyword_match = True
          break
    
      if keyword_match and user.screen_name not in names:
        names.append(user.screen_name)
        target = {}
        target['screen_name'] = user.screen_name
        target['description'] = user.description
        target['name'] = user.name
        target['url'] = user.url
        target['location'] = user.location
        target['followers'] = user.followers_count
        target['following'] = user.friends_count
        
        # UNCOMMENT IF YOU WANT TO PING EVERY URL AND SEE IF IT'S WORDPRESS
        #if user.url:
          # All sorts of invalid crap in Twitter URLs; wrap them tight
        #  try:
        #    response = urllib2.urlopen(user.url)
        #    if response.code == 200:
        #      page_source = response.read()
        #      if 'wp-content' in page_source:
        #        target['wp_url'] = True
        #      else:
        #        target['wp_url'] = False
        #  except:
        #    target['url'] = ''
        
        targets.append(target)
      counter += 1
      if counter % 10 == 0:
        print "Analyzed " + str(counter) + " people"
  except:
    print "Entercountered an error so stopping"
    print traceback.format_exc()

format_output(targets)
csv_output(targets)