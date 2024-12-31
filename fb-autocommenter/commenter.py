import facebook
import gspread
from google.oauth2.service_account import Credentials
import time
import logging
import json
import requests

access_token = None

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_facebook(page_name):
  # Initialize Facebook Graph API
  try:
    with open('config/facebook/tokens.json', 'r') as file:
      data = json.load(file)
      global access_token
      access_token = data[page_name.lower()]['access_token']
      
      return facebook.GraphAPI(access_token)
  except Exception as e:
    logger.error(f"Failed to initialize Facebook API: {e}")
    return None

def init_gspread():
  # Initialize Google Sheets API
  try:
    scopes = [
      'https://www.googleapis.com/auth/spreadsheets',
      'https://www.googleapis.com/auth/drive'
    ]
    credentials = Credentials.from_service_account_file(
      'config/gspread/service_account.json',
      scopes=scopes
    )
    return gspread.authorize(credentials)
  except Exception as e:
    logger.error(f"Failed to initialize Google Sheets API: {e}")
    return None

def get_spreadsheet_data(gc, spreadsheet_name, worksheet_name):
  # Get data from Google Spreadsheet
  try:
    sheet = gc.open(spreadsheet_name).worksheet(worksheet_name)
    return sheet.get_all_records()
  except Exception as e:
    logger.error(f"Failed to get spreadsheet data: {e}")
    return []

def check_and_respond_to_comments(graph, page_id, post_id, keyword, response, message, button, link):
  # Check comments for keyword and respond if found
  try:
    # Create the comment ID
    id = str(page_id['id']) + '_' + str(post_id)

    # Get comments for the post
    comments = graph.get_connections(id, 'comments')
    for comment in comments['data']:
      if keyword.lower() in comment['message'].lower():
        # Check if we haven't already replied to this comment
        replies = graph.get_connections(comment['id'], 'comments')
        
        # If no replies or our response isn't in the replies
        if not replies['data']:
          try:
            # Using API v21.0 Send a private reply with the message to the comment author
            url = f"https://graph.facebook.com/v21.0/{page_id['id']}/messages?access_token={access_token}"
            data = {
              "recipient": {
                "comment_id": comment['id']
              },
              "message": {
                "attachment":{
                  "type":"template",
                  "payload":{
                    "template_type":"button",
                    "text":message,
                    "buttons":[
                      {
                        "type":"web_url",
                        "url":link,
                        "title":button
                      }
                    ]
                  }
                }
              },
              "messaging_type": "RESPONSE"
            }

            res = requests.post(url, json=data)
            if res.status_code != 200:
              logger.error(res.raise_for_status())
              logger.error(res.json())

            # Post the response as a reply
            graph.put_object(parent_object=comment['id'], 
                    connection_name='comments',
                    message=response)
            logger.info(f"Responded to comment {comment['id']} with keyword '{keyword}'")
          except Exception as e:
            logger.error(f"Failed to post response: {e}")
            
  except Exception as e:
    # If e includes 'Unsupported get request', it means the post was deleted or not yet published so we can ignore it
    if 'Unsupported get request' in str(e):
      pass
    else:
      logger.error(f"Failed to check comments for post {id}: {e}")

def main():
  # Initialize Google Sheets
  gc = init_gspread()
  if not gc:
    return

  SPREADSHEET_NAME = '' # Name of the Google Spreadsheet
  
  while True:
    try:
      sheet = gc.open(SPREADSHEET_NAME)
      worksheets = sheet.worksheets()
      
      for worksheet in worksheets:
        # logger.info(f"Checking worksheet: {worksheet.title}")

        # Initialize the graph API with the page access token
        graph = init_facebook(worksheet.title)
        if not graph:
          return

        page_id = graph.get_object(worksheet.title)
        
        data = get_spreadsheet_data(gc, SPREADSHEET_NAME, worksheet.title)
        
        for row in data:
          post_id = row['post_id']
          keyword = row['keyword']
          response = row['comment_response']
          message = row['message_text']
          button = row['button_text']
          link = row['link']

          # logger.info(f"Checking post {post_id} for keyword '{keyword}'")
          check_and_respond_to_comments(graph, page_id, post_id, keyword, response, message, button, link)
      
      # Wait for some time before checking again
      time.sleep(240)  # Wait 4 minutes between checks
      
    except Exception as e:
      logger.error(f"Main loop error: {e}")
      time.sleep(60)  # Wait 1 minute before retrying if there's an error

if __name__ == "__main__":
  main()