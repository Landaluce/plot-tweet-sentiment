# plot-tweet-sentiment
# Summary
Performs sentiment analysis on the tweets' content and plots them in Google maps

# Dependencies
Required Python 3 packages: pip, tweepy, and bokeh

# Installation

### 1. Install Anaconda
Follow step 1 in https://github.com/Landaluce/get-Tweets/blob/master/README.md

### 2. Installing Additional Python Packages

   2.1 Begin my making sure that your package installer (pip) is up to date. In your terminal type ```pip install -U pip``` (capital u) and hit the ```Enter``` key. Your terminal window will display some information showing you the update process. Once that is completed, you can now use 'pip' (python package installer) in the next step.
   
   2.2 In your terminal type ```pip install tweepy``` and hit the ```Enter``` key.
   
   2.3 In your terminal type ```pip install bokeh``` and hit the ```Enter``` key.
   
### 3. Downloading and Extracting plot-tweet-sentiment

3.1 Download plot-tweet-sentiment: Got to https://github.com/Landaluce/plot-tweet-sentiment, click on the green ```clone or download``` button, and cick on ```Download ZIP```.

3.2 Once the plot-tweet-sentiment zip archive has downloaded, right-click on the zip icon (in your Downloads), and select Extract. Choose where you would like to install plot-tweet-sentiment and click Extract. If you wish, you may change the name of the extracted folder from plot-tweet-sentiment-master to plot-tweet-sentiment. In the instructions below, we will assume that you did this and that you extracted the plot-tweet-sentiment folder to the Desktop.

### 4. Setting up API credentials:

#### 4.1 Twitter: 

4.1.1 Follow the [twitter startup directions](twitter_startup_directions.pdf)

4.1.2 Save your keys in plot-tweet-sentiment/api_credentials.py in a dictionary:
 
    KEY1 = {"consumer_key": "XXXXXXXXXX",
            "consumer_secret": "XXXXXXXXXX",
            "access_token": "XXXXXXXXXX-XXXXXXXXXX",
            "access_token_secret": "XXXXXXXXXX"}

4.1.3 Add this dictionary to TWITTER_API_KEYS TWITTER_API_KEYS:

```TWITTER_API_KEYS = [KEY1]```

4.1.4 (optional but recommended) create multiple twitter accounts and repeat steps 4.1.1 to 4.1.3 with each new account to increase the number of requests you can do. Each account has a request limit, that when reached, the program has to wait for 15 minutes before resuming. If you choose to add more accounts, your list of keys should look something like this:

```TWITTER_API_KEYS = [KEY1, KEY2, KEY3, ...]```

#### 4.2 Google maps:

4.2.1 Go to [Google maps APIs](https://developers.google.com/maps/documentation/javascript/get-api-key)

4.2.2 Save the key in plot-tweet-sentiment/api_credentials.py:

```GOOGLE_API_KEY = "XXXXXXXXXX"```


### 5. Starting and Launching plot-tweet-sentiment
#### Important: Close your current terminal window and open a new one.

5.1 Navigate to the plot-tweet-sentiment folder by typing ```cd Desktop/plot-tweet-sentiment``` and hit the ```Enter``` key.
    
5.2 Type ```python plot-tweet-sentiment.py``` and hit the ```Enter``` key. 

You are all set.
