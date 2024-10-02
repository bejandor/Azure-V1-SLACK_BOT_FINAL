import azure.functions as func
import logging
import json
from slack_sdk import WebClient
import os
import datetime

# Define the lock and password keywords duo
lock_keywords = ['locked', 'unlock', 'blocked','locking','lock','login', 'connect','vpn']
password_keywords = ['password', 'expired','credentials']
duo_kewords = ['duo','2fa']

def is_weekend():
    # Get the current day of the week (0=Monday, 6=Sunday)
    today = datetime.datetime.today().weekday()
    # Check if it's Saturday (5) or Sunday (6)
    return today >= 5  # True or False depending on the day

def main(req: func.HttpRequest) -> func.HttpResponse:

    try:
        req_body = req.get_json()
        event_type = req_body.get('event', {}).get('type')
    except ValueError:
        return func.HttpResponse("Invalid JSON in request body", status_code=400)

    slack_token = os.environ.get("SLACK_BOT_TOKEN")  # Slack token
    client = WebClient(slack_token)  # Create a WebClient object
    bot_id = client.api_call("auth.test")['user_id']  # Get the ID of our bot


    if event_type == 'url_verification':
        # Respond to the URL verification challenge
        challenge = req_body.get('challenge')
        if challenge:
            response_data = {"challenge": challenge}
            logging.info(f"Challenge passed! Challenge: {challenge}")
            return func.HttpResponse(json.dumps(response_data), status_code=200, mimetype="application/json")

    elif event_type == 'message':
        # Extract message details from the event we are listening to
        channel_id = req_body.get('event', {}).get('channel')
        user_id = req_body.get('event', {}).get('user')
        ts = req_body.get('event', {}).get('ts')
        thread_ts = req_body.get('event', {}).get('thread_ts')
        message_text = req_body.get('event', {}).get('text')

        # This code is sending the message and reacting only to the user message
        if  user_id:  # If user id field is not empty
            if bot_id == user_id:  # If bot id is equal to bot id
                logging.info("Ignoring message from bot itself.")
                return func.HttpResponse(json.dumps({}), status_code=200, mimetype='application/json')

            elif not thread_ts:  # If it is not a thread message, avoiding repeated messages in the thread
                if not is_weekend():  # If it is not the weekend
                    # Keyword check for lock and password issues
                    if any(keyword in message_text.lower() for keyword in lock_keywords):
                        # Construct the unlock message payload
                        message_payload = {
                            "channel": channel_id,
                            "thread_ts": ts,
                           "blocks": [
                                {
                                    "type": "divider"
                                },
                                {
                                    "type": "section",
                                    "text": {
                                        "type": "mrkdwn",
                                        "text": "Hi, note that you can unlock yourself with SSPR"
                                    },
                                    "accessory": {
                                        "type": "button",
                                        "text": {
                                            "type": "plain_text",
                                            "text": "Unlock account",
                                            "emoji": True
                                        },
                                        "value": "click_me_123",
                                        "url": "https://confluence.infobip.com/display/CWT/Self+service+password+reset+-+how+to+unlock+your+account",
                                        "action_id": "button-action"
                                    }
                                },
                                {
                                    "type": "divider"
                                },
                                {
                                    "type": "section",
                                    "text": {
                                        "type": "mrkdwn",
                                        "text": "To access the SSPR you must be enrolled"
                                    },
                                    "accessory": {
                                        "type": "button",
                                        "text": {
                                            "type": "plain_text",
                                            "text": "Enroll to SSPR",
                                            "emoji": True
                                        },
                                        "value": "click_me_123",
                                        "url": "https://confluence.infobip.com/display/CWT/Self+service+password+reset+-+add+additional+sign-in+method",
                                        "action_id": "button-action"
                                    }
                                },
                                {
                                    "type": "divider"
                                },
                                {
                                    "type": "rich_text",
                                    "elements": [
                                        {
                                            "type": "rich_text_section",
                                            "elements": [
                                                {
                                                    "type": "text",
                                                    "text": "Write "
                                                },
                                                {
                                                    "type": "text",
                                                    "text": "THX ",
                                                    "style": {
                                                        "bold": True
                                                    }
                                                },
                                                {
                                                    "type": "text",
                                                    "text": "if you resolved the issue.\nWrite "
                                                },
                                                {
                                                    "type": "text",
                                                    "text": "HELP",
                                                    "style": {
                                                        "bold": True
                                                    }
                                                },
                                                {
                                                    "type": "text",
                                                    "text": " if you require additional assistance."
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                        
                        # Send the unlock message
                        client.chat_postMessage(**message_payload)
                        return func.HttpResponse(json.dumps({}), status_code=200, mimetype='application/json')

                    elif any(keyword in message_text.lower() for keyword in password_keywords):
                        # Construct the password expired message payload
                        message_payload = {
                            "channel": channel_id,
                            "thread_ts": ts,
                            "blocks": [
                                    {
                                        "type": "divider"
                                    },
                                    {
                                        "type": "section",
                                        "text": {
                                            "type": "mrkdwn",
                                            "text": "Password has expired ?"
                                        },
                                        "accessory": {
                                            "type": "button",
                                            "text": {
                                                "type": "plain_text",
                                                "text": "Reset password",
                                                "emoji": True
                                            },
                                            "value": "click_me_123",
                                            "url": "https://account.activedirectory.windowsazure.com/ChangePassword.aspx",
                                            "action_id": "button-action"
                                        }
                                    },
                                    {
                                        "type": "divider"
                                    },
                                    {
                                        "type": "rich_text",
                                        "elements": [
                                            {
                                                "type": "rich_text_section",
                                                "elements": [
                                                    {
                                                        "type": "text",
                                                        "text": "Write "
                                                    },
                                                    {
                                                        "type": "text",
                                                        "text": "THX ",
                                                        "style": {
                                                            "bold": True
                                                        }
                                                    },
                                                    {
                                                        "type": "text",
                                                        "text": "if you resolved the issue.\nWrite "
                                                    },
                                                    {
                                                        "type": "text",
                                                        "text": "HELP",
                                                        "style": {
                                                            "bold": True
                                                        }
                                                    },
                                                    {
                                                        "type": "text",
                                                        "text": " if you require additional assistance."
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            
                        }
                        # Send the password expired message
                        client.chat_postMessage(**message_payload)
                        return func.HttpResponse(json.dumps({}), status_code=200, mimetype='application/json')
                    
                    elif any(keyword in message_text.lower() for keyword in duo_kewords):
                        # Construct the password expired message payload
                        message_payload = {
                            "channel": channel_id,
                            "thread_ts": ts,
                            "blocks": [
                                            {
                                                "type": "divider"
                                            },
                                            {
                                                "type": "section",
                                                "text": {
                                                    "type": "mrkdwn",
                                                    "text": "If you need to re-enroll to DUO 2FA raise the ticket "
                                                },
                                                "accessory": {
                                                    "type": "button",
                                                    "text": {
                                                        "type": "plain_text",
                                                        "text": "Here",
                                                        "emoji": True
                                                    },
                                                    "value": "click_me_123",
                                                    "url": "https://jira.infobip.com/plugins/servlet/theme/portal/3/create/114",
                                                    "action_id": "button-action"
                                                }
                                            },
                                            {
                                                "type": "divider"
                                            },
                                            {
                                                "type": "rich_text",
                                                "elements": [
                                                    {
                                                        "type": "rich_text_section",
                                                        "elements": [
                                                            {
                                                                "type": "text",
                                                                "text": "Write "
                                                            },
                                                            {
                                                                "type": "text",
                                                                "text": "THX ",
                                                                "style": {
                                                                    "bold": True
                                                                }
                                                            },
                                                            {
                                                                "type": "text",
                                                                "text": "if you resolved the issue.\nWrite "
                                                            },
                                                            {
                                                                "type": "text",
                                                                "text": "HELP",
                                                                "style": {
                                                                    "bold": True
                                                                }
                                                            },
                                                            {
                                                                "type": "text",
                                                                "text": " if you require additional assistance."
                                                            }
                                                        ]
                                                    }
                                                ]
                                            }
                                        ]
                            
                        }
                        client.chat_postMessage(**message_payload)
                        return func.HttpResponse(json.dumps({}), status_code=200, mimetype='application/json')
                    
                else:
                    # Send message to the Slack channel/thread during weekends
                    message_payload = {
                        "channel": channel_id,
                        "thread_ts": ts,
                        	  "blocks": [
                                        {
                                            "type": "divider"
                                        },
                                        {
                                            "type": "section",
                                            "text": {
                                                "type": "mrkdwn",
                                                "text": "Password expired?"
                                            },
                                            "accessory": {
                                                "type": "button",
                                                "text": {
                                                    "type": "plain_text",
                                                    "text": "Reset password",
                                                    "emoji": True
                                                },
                                                "value": "click_me_123",
                                                "url": "https://account.activedirectory.windowsazure.com/ChangePassword.aspx",
                                                "action_id": "button-action"
                                            }
                                        },
                                        {
                                            "type": "divider"
                                        },
                                        {
                                            "type": "section",
                                            "text": {
                                                "type": "mrkdwn",
                                                "text": "Unlock yourself with SSPR"
                                            },
                                            "accessory": {
                                                "type": "button",
                                                "text": {
                                                    "type": "plain_text",
                                                    "text": "Unlock account",
                                                    "emoji": True
                                                },
                                                "value": "click_me_123",
                                                "url": "https://confluence.infobip.com/display/CWT/Self+service+password+reset+-+how+to+unlock+your+account",
                                                "action_id": "button-action"
                                            }
                                        },
                                        {
                                            "type": "divider"
                                        },
                                        {
                                            "type": "section",
                                            "text": {
                                                "type": "mrkdwn",
                                                "text": "For non-urgent problems, please open a ticket on our Corporate IT Service Desk"
                                            },
                                            "accessory": {
                                                "type": "button",
                                                "text": {
                                                    "type": "plain_text",
                                                    "text": "Service desk",
                                                    "emoji": True
                                                },
                                                "value": "click_me_123",
                                                "url": "https://jira.infobip.com/servicedesk/customer/portal/3",
                                                "action_id": "button-action"
                                            }
                                        },
                                        {
                                            "type": "divider"
                                        },
                                        {
                                            "type": "section",
                                            "text": {
                                                "type": "plain_text",
                                                "text": "If this is urgent, please write 'urgent' in this thread",
                                                "emoji": True
                                            }
                                        },
                                        {
                                            "type": "divider"
                                        }
                                    ]
                    }
                    # Send message to the Slack channel/thread
                    client.chat_postMessage(**message_payload)
                    return func.HttpResponse(json.dumps({}), status_code=200, mimetype='application/json')
                
            else:# If it is the weekend 
                if is_weekend() and 'urgent' in message_text.lower():  # Check if someone typed 'urgent' regardless of case
                    # Construct the urgent text payload
                    urgent_text_payload = {
                        "channel": channel_id,
                        "thread_ts": ts,
                        "blocks": [
                            {
                                "type": "rich_text",
                                "elements": [
                                    {
                                        "type": "rich_text_section",
                                        "elements": [
                                            {
                                                "type": "text",
                                                "text": "What is an emergency?",
                                                "style": {
                                                    "bold": True
                                                }
                                            },
                                            {
                                                "type": "text",
                                                "text": "\n"
                                            }
                                        ]
                                    },
                                    {
                                        "type": "rich_text_list",
                                        "style": "bullet",
                                        "indent": 0,
                                        "border": 0,
                                        "elements": [
                                            {
                                                "type": "rich_text_section",
                                                "elements": [
                                                    {
                                                        "type": "text",
                                                        "text": "Urgent domain account problem (locked, expired, password reset)"
                                                    }
                                                ]
                                            },
                                            {
                                                "type": "rich_text_section",
                                                "elements": [
                                                    {
                                                        "type": "text",
                                                        "text": "The device is stolen (mobile phone, laptop)"
                                                    }
                                                ]
                                            },
                                            {
                                                "type": "rich_text_section",
                                                "elements": [
                                                    {
                                                        "type": "text",
                                                        "text": "BitLocker encryption problems"
                                                    }
                                                ]
                                            },
                                            {
                                                "type": "rich_text_section",
                                                "elements": [
                                                    {
                                                        "type": "text",
                                                        "text": "DUO problem"
                                                    }
                                                ]
                                            }
                                        ]
                                    },
                                    {
                                        "type": "rich_text_section",
                                        "elements": [
                                            {
                                                "type": "text",
                                                "text": "On-Call Schedule information can be found "
                                            },
                                            {
                                                "type": "link",
                                                "url": "https://confluence.infobip.com/display/RCIS/RA+CIS+-+Weekend+On-Call+duty",
                                                "text": "HERE"
                                            },
                                            {
                                                "type": "text",
                                                "text": "\nOn-Duty phone number:\n"
                                            },
                                            {
                                                "type": "link",
                                                "url": "tel:+385993038199",
                                                "text": "+385 99 3038 199"
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                    # Send the urgent text payload
                    client.chat_postMessage(**urgent_text_payload)
                    
                    
                    
                    
                    
                elif message_text.lower() == 'thx':
                    try:
                        client.reactions_add(channel=channel_id, timestamp=thread_ts, name="checkgreens")
                        thx_response = {
						"channel": channel_id,
						"thread_ts": ts,
						"text": "Resolved"}
                        client.chat_postMessage(**thx_response)
                        return func.HttpResponse(json.dumps({}), status_code=200, mimetype='application/json')
                    except Exception as e:
                        if 'already_reacted' in str(e):  # Check if the error is 'already_reacted'
                            return func.HttpResponse("The reaction has already been added to this message.", status_code=200)
                        else:
                            logging.error(f"Error occurred while processing 'thx' message: {e}")
                            return func.HttpResponse("Error occurred while processing 'thx' message", status_code=500)
  
                
                elif message_text.lower() == 'help':
                     # Respond to the user
                    help_response = {
                            "channel": channel_id,
                            "thread_ts": ts,
                            "text": "Soon an IT agent will assist you. Thank you for your patience."
                        }
                    client.chat_postMessage(**help_response)
                    return func.HttpResponse(json.dumps({}), status_code=200, mimetype='application/json')    
            
        

        else:
            logging.warning("User ID is not provided in the message event.")
            return func.HttpResponse("User ID is not provided in the message event.", status_code=400)

    else:
        logging.info(f"Received unrecognized event type: '{event_type}'")
        # Implement logic for other event types if necessary
        pass

    # If the event type is not recognized or no action is taken
    return func.HttpResponse("Event handled successfully", status_code=200)