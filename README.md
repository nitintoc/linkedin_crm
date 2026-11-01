# linkedin_crm
Tool for linkedin outreach 


How to use the app?

Go to the LinkedIn Developer portal (https://developer.linkedin.com/) and click Create app.
Name it something like outreach_analytics.
In the LinkedIn Page field, choose the Member Data Portability (Member) Default Company instead of Lehrling.
Upload any logo and accept the terms.
In the new app’s Products tab, request Member Data Portability API (Member) and accept the terms.
In the Developer portal, go to Docs and tools → OAuth Token Tools, then click Create token. Select the app that has the product, choose the r_dma_portability_self_serve scope, click Request access token, and consent when LinkedIn asks. Only members located in the EEA or Switzerland can generate this token. 
Put the token in an environment variable rather than in the file: export LINKEDIN_TOKEN="..." on macOS or Linux, or set LINKEDIN_TOKEN=... in Windows cmd.
Run python fetch_linkedin.py.

What it does: it pulls three domains, INVITATIONS, CONNECTIONS and INBOX. The endpoint only accepts the version header 202312, and it pages through results until LinkedIn says no data is left. It saves everything to linkedin_raw.json on your machine and prints only the field names found in each domain

Use a prompt like this to analyze the json to extract insights:
Analyze my LinkedIn cold outreach from linkedin_raw.json in this project. The file is local and gitignored. Read it yourself. Do not invent numbers, and do not print message bodies or email addresses in the summary.

The file has three lists:

INVITATIONS — one invite per row
- Direction: OUTGOING or INCOMING
- Sent At: like "10/31/26, 3:00 PM"
- Message
- From, To
- inviterProfileUrl, inviteeProfileUrl

CONNECTIONS — one current connection per row
- First Name, Last Name, Company, Position, Email Address
- Connected On: like "31 Oct 2026"
- URL

INBOX — one message per row
- CONVERSATION ID, DATE ("2022-07-25 16:48:21 UTC")
- SENDER PROFILE URL, RECIPIENT PROFILE URLS
- FROM, TO, CONTENT, SUBJECT, FOLDER (INBOX, ARCHIVE, SPAM)

My profile URL is https://www.linkedin.com/in/nitinaugustine

Define an outreach person as an INVITATIONS row with Direction OUTGOING and inviterProfileUrl equal to my profile. Join everything on LinkedIn profile URL.

For each outreach person, compute:
- invited_at from Sent At
- accepted if inviteeProfileUrl is in CONNECTIONS.URL; accepted_at is Connected On
- replied if INBOX has a message from their profile URL after invited_at
- last_message_at and last_message_from (me or them), across INBOX, ARCHIVE, and SPAM
- waiting if not accepted and they have not replied after the invite

There is no call-booked field. Do not guess bookings from message text. Add a column call_booked and leave it blank for me to fill in.

There is no location, city, country, or industry. Say that directly. Group profile type only from CONNECTIONS.Position using keyword buckets: Founder/CEO, Director/VP/Head, Engineer, Sales, Recruiter, Other, Unknown. Show the rules you used and the count per bucket.

Report:
1. Totals: outgoing invites, accepted, accept rate, replied, reply rate, still waiting.
2. The same metrics by week and by month of invited_at. Week starts Monday.
3. A person table: name, profile URL, company, position, profile bucket, invited_at, accepted_at, replied, last_message_at, last_message_from, call_booked.
4. State the date range actually present in INVITATIONS versus CONNECTIONS, so older connections are not treated as outreach from this export.

Sort the person table by invited_at, newest first. Give the weekly and monthly tables first, then the person table.
