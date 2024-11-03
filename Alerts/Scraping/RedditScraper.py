import requests
from datetime import datetime , timezone , timedelta
import re

## nase url for apis endpoints ##
Base_URL = 'https://oauth.reddit.com'

## account to be scraped ##
RedditAccounts =["r/wallstreetbets", "r/shortsqueeze"]

## method to calculate each time for each post ## 
def calcu_time(time):
    time_now_utc = datetime.now(timezone.utc)
    limit_time = time_now_utc - timedelta(hours=6)
    if time > limit_time:
        return True
    else:
        return False

## method to get access token to authenticate access for apis ##
def get_token_headers():
    ### credintial data ##
    secret_key = 'AlS-Qu-N3NHs7VOab3WjuRrsQ1PuMw'
    client_id = 'SpTAmN8g_NE1BBBWdikaPw'
    ## creates an authentication object for making HTTP requests ##
    auth = requests.auth.HTTPBasicAuth(client_id,secret_key)
    ## login data ##
    data = {
        'grant_type':'password',
        'username':'Maleficent-Pen8391',
        'password':'ASMB2011asmb@',
    }
    ## specify api version ##
    headers = {'User-Agent':'streetsuiteAPI/1.0.0'}
    # REQUEST to get access token ##
    response = requests.post('https://www.reddit.com/api/v1/access_token/', auth=auth,data=data,headers=headers)
    ## response in json formate ##
    response = response.json()
    ## access token ##
    token = response['access_token']
    ## put token (in bearer key) on headers ## 
    headers['Authorization'] = f'bearer {token}'
    return headers

## main Reddit method to get data ##
def Reddit_API_Response(returned_dict , our_symbol):
    ## initialize pattern consists of ticker ##
    # pattern = re.compile('|'.join(map(re.escape, our_symbol)), re.IGNORECASE)
    pattern = re.compile(r'\b(' + '|'.join(map(re.escape, our_symbol)) + r')\b', re.IGNORECASE)
    ## get access token and headers ##
    headers = get_token_headers()
    ## looping on each account ##
    for account in RedditAccounts:
        ## request on each account ##
        posts_new = requests.get(f'{Base_URL}/{account}/new/',headers=headers).json()
        ## looping on new posts ##
        for post in posts_new['data']['children']:
            ## get time that post published at ##
            post_time = post['data']['created_utc']
            ## edit time for suitable formate ##
            post_time = datetime.fromtimestamp(post_time,timezone.utc)
            ## check if time of post is in last 6 hours or not ##
            if calcu_time(time=post_time):
                # # # Make sure that post is not meme # # # 
                text_meme = (post['data']['link_flair_richtext'][0]['t']).upper()
                if text_meme != "MEME":
                    ## get the href url of the post to request on it ##
                    post_url = post['data']['permalink']
                    ## request on each post to get its data ##
                    post_page_content = requests.get(f'{Base_URL}/{post_url}',headers=headers)
                    # ## post page content ##
                    post_page_content_json = post_page_content.json()
                    # Extract the title and selftext
                    title = post_page_content_json[0]['data']['children'][0]['data'].get('title', 'No Title')
                    selftext = post_page_content_json[0]['data']['children'][0]['data'].get('selftext', 'No Text')
                    title_and_selftext = title + " " + selftext
                    ## start check if title or text contain any symbol of out tickers ##
                    # Find all matches in the text (title and selftext)
                    matches_title = pattern.findall(title_and_selftext.upper())
                    ### get mentions number of each symbol ###
                    for match in matches_title:
                        if match in returned_dict.keys():
                            returned_dict[f"{match}"] += 1
                        else:
                            returned_dict[f"{match}"] = 1
            else:
                break
    return returned_dict
