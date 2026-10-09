*** Settings ***
Documentation  The collection widget portlet, displayed on the sub-elements of the dashboard (demo profile).
...            Version-independent: Plone selectors are in ui_plone*.robot.
Resource  dashboard.robot
Test Setup  Open a manager browser
Test Teardown  Close all browsers


*** Test Cases ***
The portlet of a sub-element lists the collections with their counts
    Add the collection widget portlet
    Create an expired page  dashboard  Sub page
    Go to  ${PLONE_URL}/dashboard/sub-page
    The portlet lists the collections  Every elements  My elements  Elements to review  Expired elements
    The collection shows its number of items  Expired elements  1  in=${PORTLET}

A collection of the portlet opens the dashboard with that collection
    Add the collection widget portlet
    Create a page  dashboard  Sub page
    Go to  ${PLONE_URL}/dashboard/sub-page
    Click the collection in the portlet  My elements
    The page URL is  ${PLONE_URL}/dashboard
    The collection is selected  My elements
