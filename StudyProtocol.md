STUDY PROTOCOL FOR TWITTER (X) FEED CAPTURE

This protocol ensures consistent, unbiased, and replicable data collection for analysing personalised recommendation feeds on Twitter (X).

1. Account Creation

Two separate Twitter accounts are used to evaluate potential differences in recommendation behaviour under controlled conditions.

Accounts:
* 'girluser112'
* 'boyuser112'

Controlled Setup:
To minimise initial algorithmic divergence, both accounts are configured identically.

Initial Interests Selected for BOTH accounts:
News
Movies & TV
Technology
Business & Finance
Career
Gaming
Health & Fitness
Memes
Education
Science
Religion

This ensures the only meaningful variable between accounts is the account username (A vs. B), not their expressed interest

2. Data Collection Environment

To avoid external bias:
* Same physical device is used for both accounts
* Same browser (Chrome)
* Same network connection
* No browser extensions or ad-blockers
* No manual interaction before or after scrolling outside the defined protocol

3. Image Capturing Procedure

For each weekly capture session:
1. Log in to the designated account (User A or User B) immediately before the screenshot task is scheduled.
2. Navigate to the For You feed.
3. Perform a smooth, continuous downward scroll at a consistent pace.
4. No likes, no clicks, no interactions.
5. No hovering over UI elements that might trigger hover-based tracking.
6. The screenshot script automatically captures the feed for 1 minute.
7. Immediately log out after the automated capture is complete.
8. Repeat the procedure for the second account under identical conditions.

This maintains consistency and avoids introducing behavioural signals into the recommendation model.

4. Avoiding Algorithmic Bias

To prevent contaminating the recommendation algorithm:
* No liking, retweeting, or following on either account
* No DMs or manual exploration
* Never stay logged into an account unless capturing data
* Each session is done in the same order (A then B)

This avoids asymmetric behavioural drift between the two accounts.

5. Frequency
* Data is captured once per week at a consistent time
* Duration of each capture: 1 minute per account
* Screenshots are saved and timestamped automatically

