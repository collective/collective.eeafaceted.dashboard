*** Settings ***
Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/selenium.robot

Library  Remote  ${PLONE_URL}/RobotRemote
Library  plone.app.robotframework.keywords.Debugging
Library  Selenium2Screenshots

Suite Setup  Suite Setup
Suite Teardown  Close all browsers

*** Variables ***

#${BROWSER} =  Firefox
${SELENIUM_RUN_ON_FAILURE} =  Debug

*** Test cases ***

Dashboard homepage
    Go to  ${PLONE_URL}/dashboard
    Set Window Size  1280  2880
    Wait until element is visible  css=.faceted-table-results  10
    Capture and crop page screenshot  doc/screenshots/application.png  css=.site-plone  id=portal-footer-wrapper
    Wait until element is visible  css=.gna


*** Keywords ***
Suite Setup
    Open test browser
#    Set Window Size  1024  768
    Set Window Size  1280  1200
    Set Window Size  1280  2880
    Set Suite Variable  ${CROP_MARGIN}  5
    Set Selenium Implicit Wait  2
    Set Selenium Speed  0.2
    Enable autologin as  Manager