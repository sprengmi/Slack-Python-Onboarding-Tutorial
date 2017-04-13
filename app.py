# -*- coding: utf-8 -*-
"""
A routing layer for the onboarding bot tutorial built using
[Slack's Events API](https://api.slack.com/events-api) in Python
"""
import json
import pprint
import bot
from flask import Flask, request, make_response, render_template
import os
from slackclient import SlackClient

from bustracker import getdirections
from bustracker import getstops
from bustracker import predictions

pyBot = bot.Bot()
slack = pyBot.client

app = Flask(__name__)

# Get Slack Token from environment var
# UNIX:	 	export SLACK_TOKEN='xxxXXXxxXXxxX'
# Windows:	setx SLACK_TOKEN "xxxXXXxxXXxxX"
slack_token = os.getenv("SLACK_TOKEN")
sc = SlackClient(slack_token)
# List of valid commands #
_commands = ['/stop','/route','/stoplist', '/ctabothelp']



def _event_handler(event_type, slack_event):
	"""
    A helper function that routes events from Slack to our Bot
    by event type and subtype.

    Parameters
    ----------
    event_type : str
        type of event recieved from Slack
    slack_event : dict
        JSON response from a Slack reaction event

    Returns
    ----------
    obj
        Response object with 200 - ok or 500 - No Event Handler error

    """
	
	team_id = slack_event["team_id"]
	chan_id = slack_event["event"].get("channel")
		
	# ================ TEST =============== #
    #	test event that fires only if message include "test" string.
	#	prints slack_event json to the command line
	if (event_type == "message" and 
			"test" in slack_event["event"].get("text") and 
			not "bot_id" in slack_event["event"]):
		#user_id = slack_event["event"].get("user")
		
		print("test")
		print slack_token
		print sc
		print event_type
		pp = pprint.PrettyPrinter(indent=4)
		pp.pprint(slack_event)
		
		sc.api_call("chat.postMessage",
			as_user="true:", 
			channel = chan_id, 
			text = "Hello from Python! app.py")
		
		return make_response("Test run", 200,)
		
		#channel_id = slack_event["event"].get("channel")
        #pyBot.onboarding_message(team_id, user_id)
		
	# # ============= Event Type Not Found! ============= #
	# If the event_type does not have a handler
	message = "You have not added an event handler for the %s" % event_type
	# Return a helpful error message
	return make_response(message, 200, {"X-Slack-No-Retry": 1}) 


def _command_handler(slack_command, command_text, chan_id):

	# # ============= /help ============= #
	# lists available commands for the CTA_Bot
	if (slack_command == "/ctabothelp" ):
		msg = (
			"Welcome to the CTA_Bot. This bot connects to the CTA Bustracker API to provide an interface "+
			"where you can find your Stop ID and get the upcoming arrival time predictions. Available commands include: "+ "\n\n"+
			"\n"+
			">*/stop [stop_id]*	if you know your stop id enter here to get predictions" + "\n\n"
			">*/route [route_id]*	enter your route id and the app will respond with the valid route directions" + "\n\n"+
			">*/stoplist [route_id] [direction]*	enter route id and a valid direction to get list of stops on that route"		
			)
		
		sc.api_call("chat.postMessage",
			as_user="true:", 
			channel = chan_id, 
			text = msg)
		
		return make_response("Command run", 200,)
	
	
	# # ============= /stop ============= #
	# If user knows stop id and enters </stop [stop_id]>
	# return upcoming bustracker predictions from bustracker.py - predictions(stop_id)
	if (slack_command == "/stop" ):
		msg = predictions(str(command_text))
		
		print msg
		sc.api_call("chat.postMessage",
			as_user="true:", 
			channel = chan_id, 
			text = msg)
	
		return make_response("Command run", 200,)
		
	# # ============= /route ============= #
	# If user knows route </route [route_id]>
	# return valid route directions from bustracker.py - predictions(stop_id)
	if (slack_command == "/route" ):
		
		directions = getdirections(str(command_text))
		dirs = ""
		for d in directions:
			dirs = dirs + ">*"+d["dir"] +"*"+"\n"
					
		msg = ("These are the valid directions for *Route: "+command_text+ ":*\n"+
				dirs +
				"Use </stoplist [route#] [direction]> to see all valid stops for this route & direction." )
		
		sc.api_call("chat.postMessage",
			as_user="true:", 
			channel = chan_id, 
			text = msg)
		return make_response("Command run", 200,)
	
	# # ============= /stoplist ============= #
	# If user knows route & direction </stoplist [route_id] [direction]>
	# return all stops from bustracker.py - getstops(rt, direction)
	if (slack_command == "/stoplist" ):
		cmd = command_text.split()
		rt = str(cmd[0])
		dir = str(cmd[1]).title()
		
		stops = getstops(rt,dir)
		
		stoptxt = ""
		
		for s in stops:
			stpid = s["stpid"].strip()
			stpnm = s["stpnm"].strip()
			pad = 30 - len(stpid)
			
			stoptxt = (stoptxt + ">*" + (stpid+"*").ljust(pad) + stpnm + "\n")
			
			
			
			#stoptxt = (stoptxt + ">* "+ "{:<30}".format(s["stpid"]+": ") +s["stpnm"] +"* \n")
			#stoptxt = (stoptxt + ">* {0:30} {1}".format(s["stpid"],s["stpnm"]) +"* \n")
			#stoptxt = (stoptxt + (s["stpid"]+": \t" + s["stpnm"]).expandtabs(30) + "\n")
		msg = ("Stops for *Route: "+rt+" "+dir+ "* \n"+
				"*Stop ID*".ljust(30) + "*Stop Name*" + "\n" +
				stoptxt +
				"Use command </stop [stop_id]> to see predictions for your stop!")
		
		sc.api_call("chat.postMessage",
			as_user="true:", 
			channel = chan_id, 
			text = msg)
		return make_response("Command run", 200,)
		
	
	
	
	
	
	
	
	
		
	   

   


@app.route("/install", methods=["GET"])
def pre_install():
    """This route renders the installation page with 'Add to Slack' button."""
    # Since we've set the client ID and scope on our Bot object, we can change
    # them more easily while we're developing our app.
    client_id = pyBot.oauth["client_id"]
    scope = pyBot.oauth["scope"]
    # Our template is using the Jinja templating language to dynamically pass
    # our client id and scope
    return render_template("install.html", client_id=client_id, scope=scope)


@app.route("/thanks", methods=["GET", "POST"])
def thanks():
    """
    This route is called by Slack after the user installs our app. It will
    exchange the temporary authorization code Slack sends for an OAuth token
    which we'll save on the bot object to use later.
    To let the user know what's happened it will also render a thank you page.
    """
    # Let's grab that temporary authorization code Slack's sent us from
    # the request's parameters.
    code_arg = request.args.get('code')
    # The bot's auth method to handles exchanging the code for an OAuth token
    pyBot.auth(code_arg)
    return render_template("thanks.html")

#	======== listens for and pass Slack Slash Commands =========	#
#																	#
@app.route("/command", methods=["POST"])
def commands():
	token = request.form.get('token',None)
	slack_command = request.form.get('command', None)
	command_text = request.form.get('text', None)
	chan_id = request.form.get('channel_id', None)

	print slack_command
	print command_text
	
	if slack_command in _commands:
		return _command_handler(slack_command, command_text, chan_id)
	
	
	return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})

@app.route("/listening", methods=["GET", "POST"])
def hears():
    """
    This route listens for incoming events from Slack and uses the event
    handler helper function to route events to our Bot.
    """
    slack_event = json.loads(request.data)
	
    # ============= Slack URL Verification ============ #
    # In order to verify the url of our endpoint, Slack will send a challenge
    # token in a request and check for this token in the response our endpoint
    # sends back.
    #       For more info: https://api.slack.com/events/url_verification
    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                             "application/json"
                                                             })

    # ============ Slack Token Verification =========== #
    # We can verify the request is coming from Slack by checking that the
    # verification token in the request matches our app's settings
    if pyBot.verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s \npyBot has: \
                   %s\n\n" % (slack_event["token"], pyBot.verification)
        # By adding "X-Slack-No-Retry" : 1 to our response headers, we turn off
        # Slack's automatic retries during development.
        make_response(message, 403, {"X-Slack-No-Retry": 1})

    # ====== Process Incoming Events from Slack ======= #
    # If the incoming request is an Event we've subcribed to
    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
		
        # Then handle the event by event_type and have your bot respond
        return _event_handler(event_type, slack_event)
    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})


if __name__ == '__main__':
    app.run(debug=True)
