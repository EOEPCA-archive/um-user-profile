#!/usr/bin/python3
from flask import Flask, render_template, request, jsonify, redirect, session, url_for
from itsdangerous import URLSafeTimedSerializer
from smtp_email import SMTPEmail
app = Flask(__name__)
smtp_client = SMTPEmail()
class SMTPClient():
    sso_url=''
    def __init__(self, config,secret_key):
        app.secret_key = secret_key
        self.email=''
   
    def _get_valid_https_url(self, url):
        if "http" not in url:
            return "https://" + url

    def set_email(self, email):
        self.email=email
    # @users_blueprint.route('/confirm/<token>')
    #@app.route( '/confirmation/<token>')
    def getConfirmation(self,token):
        try:
            confirm_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
            mail = confirm_serializer.loads(token, salt='email-confirmation-salt', max_age=3600)
            return mail
        except:
            print('The confirmation link is invalid or has expired.', 'error')
            
 

    #@app.route('/confirmation_mail', methods=['GET', 'POST'])
    def send_confirmation(self):

        confirm_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        confirm_url = url_for('confirmation', token=confirm_serializer.dumps(self.email, salt='email-confirmation-salt'), _external=True)
        html = render_template('activate.html',confirm_url=confirm_url)
        subject = 'Delete Account Confirmation'
        smtp_client.send_email(self.email, subject, html) # Here is to use the smtp client for sending the mail to the user
        print('A new confirmation email has been sent.', 'success')
        #here there is no need for a return I think