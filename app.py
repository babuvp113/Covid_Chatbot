from flask import Flask, request, make_response
import json
import os
from flask_cors import cross_origin
from SendEmail.sendEmail import EmailSender
from logger import logger
from email_templates import template_reader
import re
from DataScrap.dataScrap import CoronaDataScrap

app = Flask(__name__)

# geting and sending response to dialogflow
@app.route('/webhook', methods=['POST'])
@cross_origin()
def webhook():

    req = request.get_json(silent=True, force=True)

    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

# processing the request from dialogflow

def processRequest(req):
    log = logger.Log()

    sessionID=req.get('responseId')
    result = req.get("queryResult")
    user_says=result.get("queryText")
    log.write_log(sessionID, "User Says: "+user_says)
  #  log.write_mongodb(sessionID, "User Says: " + user_says)
    parameters = result.get("parameters")
    cust_name=parameters.get("user_name")
    #print(cust_name)
    cust_contact = parameters.get("user_phone")
    cust_email=parameters.get("user_email")
    cust_pincode= parameters.get("user_pincode")
    cust_pincode = re.sub(' ','',str(cust_pincode))
    intent = result.get("intent").get('displayName')

    if (intent=='ZipcodeSelection'):

    #    covid19 = CoronaDataScrap()
     #   data = covid19.scrap_data()
        #data = pd.read_csv('/DataScrap/Corona_reports.csv')
        email_sender=EmailSender()
        template= template_reader.TemplateReader()
        email_message=template.read_course_template('covid_19_template.html')
        email_sender.send_email_to_student(cust_email,email_message)
       # email_file_support = open("email_templates/support_team_Template.html", "r")
       # #email_message_support = email_file_support.read()
        #email_sender.send_email_to_support(cust_name=cust_name,cust_contact=cust_contact,cust_email=cust_email,course_name=course_name,body=email_message_support)
        fulfillmentText="We have sent the Precautionary Measures and India's covid details to you via email. Stay safe and take care."
        log.write_log(sessionID, "Bot Says: " + fulfillmentText)
        #log.write_mongodb(sessionID, "Bot Says: " + fulfillmentText)
        return {
            "fulfillmentText": fulfillmentText
        }
    else:
        log.write_log(sessionID, "Bot Says: " + result.fulfillmentText)
        #log.write_mongodb(sessionID, "Bot Says: " + result.fulfillmentText)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5009))
    print("Starting app on port %d" % port)
    app.run(debug=True, port=port, host='0.0.0.0')
