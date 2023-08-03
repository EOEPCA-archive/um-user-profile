#!/usr/bin/python3
from flask import Flask, render_template, request, jsonify, redirect, session, url_for
import json
import ast
import logging
import jwt
from handlers.log_handler import LogHandler
import requests
import re
from custom_oauth import OAuthClient
from custom_scim import SCIMClient
from eoepca_scim import *
from custom_smtp import SMTPClient
import generic
import os
log_handler = LogHandler
log_handler.load_config("UP", "./config/log_config.yaml")
logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger("USER_PROFILE")


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
"UP_DEBUG_MODE",
"UP_PDP_URL",
"UP_PDP_PORT"]

dir_path = os.path.dirname(os.path.realpath(__file__))
use_env_var = True

for env_var in env_vars:
    if env_var not in os.environ:
        use_env_var = False

config = {}
# setup config
if use_env_var is False:
    with open(dir_path+"/config/WEB_config.json") as j:
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


auth_client = OAuthClient(config, use_env_var)
# Save new client_id and secret config if any

def refresh_session(refresh_token):
    print("Refreshing session")
    data = auth_client.refresh_token(refresh_token)
    err, code = generic.get_posible_errors(data)
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

@app.route(g_base_uri+"/TC_management/modify",methods=['POST'])
def modify_TC():
    
    data = request.form.to_dict()
    
    keys=request.form.getlist('key')
    values=request.form.getlist('value')
    checks=request.form.getlist('check')
    res={}
    

    #urn:ietf:params:scim:schemas:extension:gluu:2.0:User->apiKeys
    refresh_token = session.get('refresh_token')
    logged_in = session.get('logged_in')
    
    if not logged_in or refresh_token is None or refresh_token is "":
        session["reminder"] = 'modify_TC'
        return redirect(url_for('login'))

    # Refresh session and execute
    session[generic.ERR_MSG], session[generic.ERR_CODE] = refresh_session(refresh_token)
    token = session.get('access_token')
    id_token = session.get('id_token')
    #FORM DATA
    sub=auth_client.verify_uid_headers("http://"+config["sso_url"], id_token, 'sub')
    
    for i in auth_client.get_terms_conditions():
        if i not in keys:
            auth_client.delete_terms(config["pdp_url"]+'/pdp/terms/'+i, id_token)


    if session[generic.ERR_MSG] is "":
        word = request.args
        for i in range(len(keys)):
            data= '{"term_id":"'+str(keys[i])+'", "term_description":"'+str(values[i])+'"}'
            headers = {'Content-Type': 'application/json, Authorization: Bearer '+ token}
            r = requests.post("https://" + config["sso_url"]+'/pdp/terms/', headers=headers, data=data, verify=False)
            headers = {'Content-Type': 'application/json, Authorization: Bearer '+ id_token}
        k = auth_client.set_user(url="http://" + config["sso_url"],idx= sub,token= token,data= str(checks))
    return redirect(url_for("TC_management"))

@app.route(g_base_uri+"/TC_management")
def TC_management():
    err_msg = None
    old_err_msg = session.get(generic.ERR_MSG, "")
    err_code = session.get(generic.ERR_CODE, "")
    # Overwrite them to not let the user lock themselfs in an error
    session[generic.ERR_MSG] = ""
    session[generic.ERR_CODE] = ""
    
    refresh_session(session.get('refresh_token',""))

    token = session.get('access_token')
    id_token = session.get('id_token')
    logged_in = session.get('logged_in')
    if not logged_in or token is None or token is "":
        session["reminder"] = 'TC_management'
        return redirect(url_for('login'))
    data, session[generic.ERR_MSG] = scim_client.getAttributes(session.get('logged_user'))
    found = None
    
    a=''
    headers = {'Content-Type': 'application/json, Authorization: Bearer '+ token}
    s= requests.get(config["pdp_url"]+'/pdp/terms/', headers=headers, verify=False) 
    j = s.json()
    n=auth_client.backup_terms(config["pdp_url"]+'/pdp/terms/', id_token)
    sub=auth_client.verify_uid_headers("http://"+config["sso_url"], id_token, 'sub')
    
    data = auth_client.get_user("http://"+config["sso_url"], sub, token)
    total = str(data).split('\'')
    for k in data[0]:
        if "gluu:2.0:User" in k:
            for n in data[0][k]:
                if "TermsConditions" in n:
                    termList= ast.literal_eval(data[0][k][n])

    return render_template("TC_management.html",
        title = g_title,
        username = session.get('logged_user'),
        logged_in = logged_in,
        color_web_background = g_background_color,
        color_web_header = g_header_color,
        logo_alt_name = g_logo_alt,
        logo_image_path = g_logo_image,
        data = termList,
        terms = j
    )
def get_user(idx,token):
    headers = {
        'Authorization': "Bearer "+token
    }
    
    endpoint="/identity/restv1/scim/v2/Users/"+str(idx)
    r = requests.get("http://"+config["sso_url"]+endpoint, headers=headers, verify=False)
    try:
        return r.json(), r.status_code
        
    except JSONDecodeError:
        return jsonify(message=r.text), r.status_code

@app.route(g_base_uri+"/licenses_management/modify",methods=['POST'])
def modify_licenses():
    
    data = request.form.to_dict()
    keys=request.form.getlist('key')
    values=request.form.getlist('value')
    res={}
    for i in range(len(keys)):
        res[str(keys[i])] = str(values[i])
    try:
        found = str(res).replace('\'', '')
        found = found.replace(' ', '')
    except:
        pass

    #urn:ietf:params:scim:schemas:extension:gluu:2.0:User->apiKeys
    refresh_token = session.get('refresh_token')
    logged_in = session.get('logged_in')
    if not logged_in or refresh_token is None or refresh_token is "":
        session["reminder"] = 'modify_licenses'
        return redirect(url_for('login'))

    # Refresh session and execute
    session[generic.ERR_MSG], session[generic.ERR_CODE] = refresh_session(refresh_token)

    #FORM DATA
    if session[generic.ERR_MSG] is "":
        word = request.args
        session[generic.ERR_MSG], session[generic.ERR_CODE] = scim_client.editLicenses(session.get('logged_user'), found)
    return redirect(url_for("licenses_management"))

@app.route(g_base_uri+"/licenses_management")
def licenses_management():
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
        session["reminder"] = 'licenses_management'
        return redirect(url_for('login'))
    data, session[generic.ERR_MSG] = scim_client.getAttributes(session.get('logged_user'))
    found = None
    total = str(data).split('\'')
    for v in range(len(total)):
        if 'Licenses' in str(total[v]):
            for i in range(4):
                m = re.search('\{(.+?)\}', str(total[v+i]))
                if m:
                    found = m.group(1)
                    break
    a=''
    try:
        found = found.replace('\'', '')
    except:
        pass
    try:
        a = found.split(',')
    except:
        pass

    return render_template("licenses_management.html",
        title = g_title,
        username = session.get('logged_user'),
        logged_in = logged_in,
        color_web_background = g_background_color,
        color_web_header = g_header_color,
        logo_alt_name = g_logo_alt,
        logo_image_path = g_logo_image,
        data = a
    )

@app.route(g_base_uri+"/apis_management/modify",methods=['POST'])
def modify_apis():
    
    data = request.form.to_dict()
    keys=request.form.getlist('key')
    values=request.form.getlist('value')
    res={}
    for i in range(len(keys)):
        res[str(keys[i])] = str(values[i])
    try:
        found = str(res).replace('\'', '')
        found = found.replace(' ', '')
    except:
        pass

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
        word = request.args
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
    total = str(data).split('\'')
    for v in range(len(total)):
        if 'apiKeys' in str(total[v]):
            for i in range(4):
                m = re.search('\{(.+?)\}', str(total[v+i]))
                if m:
                    found = m.group(1)
                    break
    a=''
    try:
        found = found.replace('\'', '')
    except:
        pass
    try:
        a = found.split(',')
    except:
        pass

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








@app.route(g_base_uri+"/storage_details/modify",methods=['POST'])
def modify_details():
    refresh_token = session.get('refresh_token')
    logged_in = session.get('logged_in')
    if not logged_in or refresh_token is None or refresh_token is "":
        session["reminder"] = 'modify_details'
        return redirect(url_for('login'))

    # Refresh session and execute
    session[generic.ERR_MSG], session[generic.ERR_CODE] = refresh_session(refresh_token)

    #FORM DATA
    flat_list = [item for sublist in list(request.form.listvalues()) for item in sublist]
    if session[generic.ERR_MSG] is "" and request.form:
        session[generic.ERR_MSG], session[generic.ERR_CODE] = scim_client.editStorageDetails(session.get('logged_user'), flat_list)

    return redirect(url_for("storage_details"))

@app.route(g_base_uri+"/storage_details")
def storage_details():
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
        session["reminder"] = 'storage_details'
        return redirect(url_for('login'))

    data, session[generic.ERR_MSG] = scim_client.getAttributes(session.get('logged_user'))
    myDetails= []
    for k, v in data['editable'].items(): 
        if "StorageDetails" in str(k):
            myDetails = data['editable'][k]
    return render_template("storage_details.html",
        title = g_title,
        username = session.get('logged_user'),
        logged_in = logged_in,
        color_web_background = g_background_color,
        color_web_header = g_header_color,
        logo_alt_name = g_logo_alt,
        logo_image_path = g_logo_image,
        data = myDetails,
        isOper = auth_client.isOperator
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
    if 'editable' in data:
        for k, v in data['editable'].items(): 
            if "StorageDetails" in str(k):
                del data['editable'][k]
                break
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
