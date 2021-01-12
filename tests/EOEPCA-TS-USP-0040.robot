*** Settings ***

Library  SeleniumLibrary
Library  Process
Library  OperatingSystem
Library  Collections

*** Variables ***
${USER}=  admin
${PWD}=  admin_Abcd1234#
${URL}=  https://test.10.0.2.15.nip.io/web_ui

*** Test Cases ***


Attributes Edition
  Set Chrome
  Set Browser Implicit Wait  5
  ${title}=  Get Title
  BuiltIn.Run Keyword If  "${title}"=="EOEPCA User Profile"  LoginService Call Log in Button
  LoginService Fill Credentials
  ${title}=  Get Title
  BuiltIn.Run Keyword If  "${title}"=="oxAuth"  LoginService Allow User
  BuiltIn.Run Keyword If  "${title}"=="oxAuth - Passport Login"  LoginService Fill Credentials
  Go to Attributes


*** Keywords ***
Set Chrome
  ${chrome_options} =  Evaluate  sys.modules['selenium.webdriver'].ChromeOptions()  sys, selenium.webdriver
  Call Method  ${chrome_options}  add_argument  headless
  Call Method  ${chrome_options}  add_argument  disable-gpu
  Call Method  ${chrome_options}  add_argument  disable-dev-shm-usage
  Call Method  ${chrome_options}  add_argument  no-startup-window
  Call Method  ${chrome_options}  add_argument  no-sandbox
  Call Method  ${chrome_options}  add_argument  ignore-certificate-errors
  ${options}=  Call Method  ${chrome_options}  to_capabilities      
  Open Browser  ${URL}  browser=chrome  desired_capabilities=${options}
 
Configuration Error
  Log to Console  !
  Log to Console  [WARNING] The service is up, but the attributes are not accesible due to lack of configuration on the login service.
  Log to Console  Make sure SMTP server is enabled, and configured. SCIM service must be enabled also.

Delete User
  
  Click Link  xpath=//a[@href="/web_ui/profile_removal"]
  Click Element  xpath=//button[@type="submit"]
  ${a}=  Get Text  xpath=//html
  ${match}  ${value}  Run Keyword And Ignore Error  Should Contain  ${a}  confirmation mail sent succesfully
  ${RETURNVALUE}  Set Variable If  '${match}' == 'PASS'  ${True}  ${False}
  Should Be True  ${RETURNVALUE}


Profile Management
  Click Element  xpath=//input[@type="submit"]
  ${a}=  Get Text  xpath=//html
  ${match}  ${value}  Run Keyword And Ignore Error  Should Contain  ${a}  User Attributes
  ${RETURNVALUE}  Set Variable If  '${match}' == 'PASS'  ${True}  ${False}
  Should Be True  ${RETURNVALUE}

API Keys Management
  Click Element  xpath=//input[@type="submit"]
  ${a}=  Get Text  xpath=//html
  ${match}  ${value}  Run Keyword And Ignore Error  Should Contain  ${a}  API Keys List
  ${RETURNVALUE}  Set Variable If  '${match}' == 'PASS'  ${True}  ${False}
  Should Be True  ${RETURNVALUE}

Licenses Management
  Click Element  xpath=//input[@type="submit"]
  ${a}=  Get Text  xpath=//html
  ${match}  ${value}  Run Keyword And Ignore Error  Should Contain  ${a}  Licenses List
  ${RETURNVALUE}  Set Variable If  '${match}' == 'PASS'  ${True}  ${False}
  Should Be True  ${RETURNVALUE}

Terms and Conditions
  Click Element  xpath=//input[@type="submit"]  
  ${a}=  Get Text  xpath=//html
  ${match}  ${value}  Run Keyword And Ignore Error  Should Contain  ${a}  Terms and Conditions
  ${RETURNVALUE}  Set Variable If  '${match}' == 'PASS'  ${True}  ${False}
  Should Be True  ${RETURNVALUE}


Profile Edition
  Profile Management
  Click Link  xpath=//a[@href="/web_ui/apis_management"]
  API Keys Management
  Click Link  xpath=//a[@href="/web_ui/licenses_management"]
  Licenses Management
  Click Link  xpath=//a[@href="/web_ui/TC_management"]
  Terms and Conditions


Go to Attributes
  #Click Element  xpath=//a[@class="logo"]
  Click Link  xpath=//a[@href="/web_ui/profile_management"]
  ${a}=  Get Text  xpath=//html
  ${match}  ${value}  Run Keyword And Ignore Error  Should Contain  ${a}  AttributeError
  ${RETURNVALUE}  Set Variable If  '${match}' == 'PASS'  ${True}  ${False}
  BuiltIn.Run Keyword If  "${RETURNVALUE}"=="True"  Configuration Error
  Profile Edition


LoginService Allow User
  Title Should Be  oxAuth
  Click Link  xpath=//a[@id="authorizeForm:allowButton"]
  Set Browser Implicit Wait  5

LoginService Call Log in Button
  Title Should Be  EOEPCA User Profile
  Click Link  xpath=//a[@href="/web_ui/login"]
  Set Browser Implicit Wait  5

LoginService Fill Credentials
  Title Should Be  oxAuth - Passport Login
  Input Text  id=loginForm:username  admin
  Input Password  id=loginForm:password  admin_Abcd1234#
  Click Button  id=loginForm:loginButton
  Set Browser Implicit Wait  10


