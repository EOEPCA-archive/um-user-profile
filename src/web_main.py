#!/usr/bin/python3
from flask import Flask, render_template, request, jsonify, redirect, session, url_for
import json
import logging
import re
from custom_oauth import OAuthClient
from custom_scim import SCIMClient
from custom_smtp import SMTPClient
import generic
import os

env_vars = [
"UP_SSO_URL",
"UP_TITLE",
"UP_SCOPES",
"UP_REDIRECT_URI",
"UP_POST_LOGOUT_REDIRECT_URI",
"UP_BASE_URI",
"UP_OAUTH_CALLBACK_PATH",
"UP_LOGOUT_ENDPOINT",
"UP_SERVICE_HOST",
"UP_SERVICE_PORT",
"UP_PROTECTED_ATTRIBUTES",
"UP_BLACKLIST_ATTRIBUTES",
"UP_SEPARATOR_UI_ATTRIBUTES",
"UP_COLOR_WEB_BACKGROUND",
"UP_COLOR_WEB_HEADER",
"UP_LOGO_ALT_NAME",
"UP_LOGO_IMAGE_PATH",
"UP_COLOR_HEADER_TABLE",
"UP_COLOR_TEXT_HEADER_TABLE",
"UP_COLOR_BUTTON_MODIFY",
"UP_USE_THREADS",
"UP_DEBUG_MODE"]

use_env_var = True

for env_var in env_vars:
    if env_var not in os.environ:
        use_env_var = False

config = {}
# setup config
if use_env_var is False:
    with open("config/WEB_config.json") as j:
        config = json.load(j)
else:
    for env_var in env_vars:
        env_var_config = env_var.replace('UP_', '')

        if "true" in os.environ[env_var].replace('"', ''):
            config[env_var_config.lower()] = True
        elif "false" in os.environ[env_var].replace('"', ''):
            config[env_var_config.lower()] = False
        else:
            config[env_var_config.lower()] = os.environ[env_var].replace('"', '')

# We need to pass these on every render, and they are not going to change
g_background_color = config["color_web_background"]
g_header_color = config["color_web_header"]
g_logo_alt = config["logo_alt_name"]
g_logo_image = config["logo_image_path"]
g_header_table_color = config["color_header_table"]
g_text_header_table_color = config["color_text_header_table"]
g_button_modify_color = config["color_button_modify"]
g_base_uri = config["base_uri"]
g_logout_endpoint = config["logout_endpoint"] or "/logout"
g_separator = config["separator_ui_attributes"] or "->"
g_oauth_callback_path = config["oauth_callback_path"]
g_title = config["title"]

# Launch flask
app = Flask(__name__)
app.secret_key = generic.randomString()

# Generate internal clients
scim_client = SCIMClient(config,use_env_var)
smtp_client = SMTPClient(config,app.secret_key)
_user_mail = ''

# Save new client_id and secret config if any
if use_env_var is False:
    with open("config/WEB_config.json", "w") as f:
        json.dump(config, f)
else:
   # os.environ["UP_CLIENT_ID"] = config["client_id"]
   # os.environ["UP_CLIENT_SECRET"] = config["client_secret"]
   # os.environ["UP_CLIENT_ID_SCIM"] = config["client_id_scim"]
   # os.environ["UP_CLIENT_SECRET_SCIM"] = config["client_secret_scim"]
   pass

auth_client = OAuthClient(config, use_env_var)

def refresh_session(refresh_token):
    print("Refreshing session")
    data = auth_client.refresh_token(refresh_token)
    print(data)
    err, code = generic.get_posible_errors(data)
    print(err)
    if err is "":
        print("Ok, writing new session data")
        session["access_token"] = data.get("access_token","")
        session["refresh_token"] = data.get("refresh_token","")
    
    return err, code

@app.route(g_base_uri+g_oauth_callback_path)
def oauth_callback():
    code = request.args.get('code')
    try:
        response = auth_client.get_token(code)
    except Exception as e:
        print(str(e))
        return redirect(url_for('home'))

    session['access_token'] = response["access_token"]
    session['id_token'] = response["id_token"]
    session['refresh_token'] = response["refresh_token"]
    session[generic.ERR_CODE] = ""
    session[generic.ERR_MSG] = ""
    try:
        userinfo = auth_client.get_user_info(response["access_token"])
    except Exception as e:
        print(str(e))
        return redirect(url_for('home'))

    if userinfo != None:
        session['logged_in'] = True
        _user_mail=userinfo["email"]
        session['logged_user'] = userinfo["user_name"]
        smtp_client.set_email(_user_mail)

    if session.get('reminder') != None:
        redirect_url = session.get('reminder')
    else:
        redirect_url = 'home'
    return redirect(url_for(redirect_url))

@app.route(g_base_uri)
def home():
    logged_in = session.get('logged_in')
    refresh_token = session.get('refresh_token',"")
    if refresh_token is not "":
        refresh_session(refresh_token)

    return render_template("home.html",
    title = g_title,
    username = session.get('logged_user'),
    logged_in = logged_in,
    color_web_background = g_background_color,
    color_web_header = g_header_color,
    logo_alt_name = g_logo_alt,
    logo_image_path = g_logo_image)

@app.route(g_base_uri+"/login")
def login():
    url = auth_client.get_login_url()
    return redirect(url)

@app.route(g_base_uri+g_logout_endpoint)
def logout():
    session['logged_in'] = False
    session['logged_user'] = None
    session[generic.ERR_CODE] = ""
    session[generic.ERR_MSG] = ""
    token = session.get('id_token')
    if token:
        return redirect(auth_client.end_session_url(token))
    else:
        return redirect(url_for("home"))


@app.route(g_base_uri+"/apis_management/modify",methods=['POST'])
def modify_apis():
    
    logging.info('!!!!!!!!!!!!!!!!0!!!!!!!!!!!!!!!!!!')
    data = request.form.to_dict()
    logging.info(request.form)
    logging.info(request.form.getlist('key'))
    keys=request.form.getlist('key')
    values=request.form.getlist('value')
    res=[]
    for i in range(len(keys)):
        res.append(str(keys[i])+':'+str(values[i]))
    logging.info('!!!!!!!!!!!!!!!!1!!!!!!!!!!!!!!!!!!')
    try:
        found = str(res).replace('\'', '')
        found = found.replace(' ', '')
    except:
        pass
    logging.info(res)
    logging.info(found)

    #urn:ietf:params:scim:schemas:extension:gluu:2.0:User->apiKeys
    refresh_token = session.get('refresh_token')
    logged_in = session.get('logged_in')
    if not logged_in or refresh_token is None or refresh_token is "":
        session["reminder"] = 'modify_apis'
        return redirect(url_for('login'))

    # Refresh session and execute
    session[generic.ERR_MSG], session[generic.ERR_CODE] = refresh_session(refresh_token)

    #FORM DATA
    if session[generic.ERR_MSG] is "":
        logging.info('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        word = request.args
        logging.info(request.form)
        logging.info(word)
        logging.info(scim_client.getAttributes(session.get('logged_user')))
        logging.info(request.form)
        logging.info('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        session[generic.ERR_MSG], session[generic.ERR_CODE] = scim_client.editApiKeys(session.get('logged_user'), found)
    return redirect(url_for("apis_management"))

@app.route(g_base_uri+"/apis_management")
def apis_management():
    err_msg = None
    old_err_msg = session.get(generic.ERR_MSG, "")
    err_code = session.get(generic.ERR_CODE, "")
    # Overwrite them to not let the user lock themselfs in an error
    session[generic.ERR_MSG] = ""
    session[generic.ERR_CODE] = ""
    
    refresh_session(session.get('refresh_token',""))

    token = session.get('access_token')
    logged_in = session.get('logged_in')
    if not logged_in or token is None or token is "":
        session["reminder"] = 'apis_management'
        return redirect(url_for('login'))
    data, session[generic.ERR_MSG] = scim_client.getAttributes(session.get('logged_user'))
    found = None
    
    logging.info('-------------------')
    logging.info(data)
    logging.info('---------------------')

    for v in str(data).split('\''):
        logging.info(str(v))
        if '[' in str(v):
            logging.info(str(v))
            m = re.search('\[(.+?)\]', str(v))
            if m:
                found = m.group(1)
    try:
        found = found.replace('\'', '')
    except:
        pass
    try:
        a = found.split(',')
    except:
        pass

    logging.info(a)
    return render_template("apis_management.html",
        title = g_title,
        username = session.get('logged_user'),
        logged_in = logged_in,
        color_web_background = g_background_color,
        color_web_header = g_header_color,
        logo_alt_name = g_logo_alt,
        logo_image_path = g_logo_image,
        data = a
    )





@app.route(g_base_uri+"/profile_management/modify",methods=['POST'])
def modify_management():
    refresh_token = session.get('refresh_token')
    logged_in = session.get('logged_in')
    if not logged_in or refresh_token is None or refresh_token is "":
        session["reminder"] = 'modify_management'
        return redirect(url_for('login'))

    # Refresh session and execute
    session[generic.ERR_MSG], session[generic.ERR_CODE] = refresh_session(refresh_token)

    #FORM DATA
    if session[generic.ERR_MSG] is "" and request.form:
        logging.info('UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUU')
        logging.info(request.form)
        session[generic.ERR_MSG], session[generic.ERR_CODE] = scim_client.changeAttributes(session.get('logged_user'), request.form)

    return redirect(url_for("profile_management"))

@app.route(g_base_uri+"/profile_management")
def profile_management():
    err_msg = None
    old_err_msg = session.get(generic.ERR_MSG, "")
    err_code = session.get(generic.ERR_CODE, "")
    # Overwrite them to not let the user lock themselfs in an error
    session[generic.ERR_MSG] = ""
    session[generic.ERR_CODE] = ""
    
    refresh_session(session.get('refresh_token',""))

    token = session.get('access_token')
    logged_in = session.get('logged_in')
    if not logged_in or token is None or token is "":
        session["reminder"] = 'profile_management'
        return redirect(url_for('login'))

    data, session[generic.ERR_MSG] = scim_client.getAttributes(session.get('logged_user'))

    return render_template("profile_management.html",
        title = g_title,
        username = session.get('logged_user'),
        logged_in = logged_in,
        color_web_background = g_background_color,
        color_web_header = g_header_color,
        logo_alt_name = g_logo_alt,
        logo_image_path = g_logo_image,
        data = data
    )


@app.route(g_base_uri+"/confirmation_mail",methods=['POST','GET'])
def confirmation_mail():
    err_msg = None
    old_err_msg = session.get(generic.ERR_MSG, "")
    err_code = session.get(generic.ERR_CODE, "")
    refresh_token = session.get('refresh_token')
    #custom_smtp client usage for sending mail.
    smtp_client.send_confirmation()
    #return info webPage for confirmation of the sent
    token = session.get('access_token')
    logged_in = session.get('logged_in')
    return render_template("confirmation_mail.html",
        title = g_title,
        username = session.get('logged_user'),
        logged_in = logged_in,
        color_web_background = g_background_color,
        color_web_header = g_header_color,
        logo_alt_name = g_logo_alt,
        logo_image_path = g_logo_image
        )

@app.route(g_base_uri+"/confirmation/<token>")
def confirmation(token):
    #custom_scim client delete usage.
    try:
        email = smtp_client.getConfirmation(token)
        #user ID as parameter in order to delete it:
        scim_client.deleteUser(email)
        #here to delete wiht scim client the user with the email
    except:
        print('The confirmation link is invalid or has expired.', 'error')

    return render_template("confirmation_removal.html",
        title = g_title,
        color_web_background = g_background_color,
        color_web_header = g_header_color,
        logo_alt_name = g_logo_alt,
        logo_image_path = g_logo_image)


@app.route(g_base_uri+"/profile_removal")
def profile_removal():
    err_msg = None
    old_err_msg = session.get(generic.ERR_MSG, "")
    err_code = session.get(generic.ERR_CODE, "")
    # Overwrite them to not let the user lock themselfs in an error
    session[generic.ERR_MSG] = ""
    session[generic.ERR_CODE] = ""
    #refresh_session(session.get('refresh_token',""))

    token = session.get('access_token')
    logged_in = session.get('logged_in')
    if logged_in is True and token:
        #data, session[generic.ERR_MSG] = scim_client.getAttributes(session.get('logged_user'))
        return render_template("profile_removal.html",
        title = g_title,
        username = session.get('logged_user'),
        logged_in = logged_in,
        color_web_background = g_background_color,
        color_web_header = g_header_color,
        logo_alt_name = g_logo_alt,
        logo_image_path = g_logo_image
        )
    else:
        print('The confirmation link is invalid or has expired.', 'error')
        return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(
        debug=config["debug_mode"],
        threaded=config["use_threads"],
        port=int(config["service_port"]),
        host=config["service_host"]
    )
