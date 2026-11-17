*** Settings ***
Documentation  Document generation on the dashboard (demo profile): DashboardPODTemplate and its generation links.
...            Version-independent: Plone selectors are in ui_plone*.robot.
Resource  dashboard.robot
Test Setup  Open a manager browser
Test Teardown  Close all browsers


*** Test Cases ***
A dashboard template added through the UI shows a generation link on its collection
    Add a dashboard template  Dashboard report  Every elements  10
    Open the dashboard
    The generation link is shown  Dashboard report  ODT  Only the first 10 items will be generated
    Select the collection  My elements
    The generation link is not shown

A generation link posts the faceted query and the selected items
    Add a dashboard template  Dashboard report  Every elements  10
    ${template_uid}=  Path to uid  /${PLONE_SITE_ID}/dashboard-report
    ${collection_uid}=  Path to uid  /${PLONE_SITE_ID}/dashboard/every-elements
    ${folder_uid}=  Path to uid  /${PLONE_SITE_ID}/folder
    Open the dashboard
    Select only the result  ${folder_uid}
    Record the submitted form
    Click the generation link  Dashboard report  ODT
    The generation form was submitted to  ${PLONE_URL}/dashboard/document-generation
    The submitted form field is  template_uid  ${template_uid}
    The submitted form field is  output_format  odt
    The submitted form field is  uids  ${folder_uid}
    The faceted query of the submitted form selects  c1  ${collection_uid}
