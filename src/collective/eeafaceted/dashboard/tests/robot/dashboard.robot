*** Settings ***
Documentation  collective.eeafaceted.dashboard keywords, built on the ui_plone${PLONE_MAJOR}.robot keywords.
...            Robot Framework 3.1 syntax (FOR ... END; shared with the Plone 4.3 environment, RF 3.2.2).
...            Fixture (demo profile): faceted folder "Dashboard" (/dashboard) with the collections
...            "Every elements" (default), "My elements", "Elements to review" and "Expired elements"
...            (the last two show their number of items), widget c1. Paths are relative to the site.
...            Selectors: eea.facetednavigation, collective.eeafaceted.* and this package.
Resource  ui_plone${PLONE_MAJOR}.robot


*** Variables ***
${WIDGET}  css=#c1_widget
${RESULTS}  css=#faceted-results
${PORTLET}  css=.portletWidgetCollection
${GENERATION_LINKS}  css=#doc-generation-view


*** Keywords ***
Open a manager browser
    Open test browser
    Set window size  1280  2000
    Enable autologin as  Manager

Create a collection
    [Documentation]  DashboardCollection of the pages, with the columns ${columns} (python list of view field ids).
    ...              sort_on: Plone 4 dexterity doesn't fall back to the behavior defaults. The list type
    ...              evaluates the value (Bool, list): Create content doesn't set them on Plone 4.
    [Arguments]  ${path}  ${title}  ${columns}
    ${uid}=  Create content  type=DashboardCollection  container=/${PLONE_SITE_ID}/${path}  title=${title}
    ...  sort_on=
    Set field value  ${uid}  sort_reversed  False  list
    Set field value  ${uid}  showNumberOfItems  False  list
    Set field value  ${uid}  query
    ...  [{'i': 'portal_type', 'o': 'plone.app.querystring.operation.selection.is', 'v': ['Document']}]  list
    Set field value  ${uid}  customViewFields  ${columns}  list

Create a page
    [Arguments]  ${path}  ${title}
    ${uid}=  Create content  type=Document  container=/${PLONE_SITE_ID}/${path}  title=${title}
    [Return]  ${uid}

Create an expired page
    [Arguments]  ${path}  ${title}
    ${uid}=  Create a page  ${path}  ${title}
    Set field value  ${uid}  expiration_date  200001010000  datetime

Open the dashboard
    Go to  ${PLONE_URL}/dashboard
    The faceted results are loaded

The faceted results are loaded
    Wait until page contains element  ${RESULTS}
    Wait until element is not visible  css=.faceted-lock-overlay

Select the collection
    [Arguments]  ${title}
    Click element  ${WIDGET} li[title="${title}"]
    The faceted results are loaded

The collection is selected
    [Arguments]  ${title}
    Wait until page contains element  ${WIDGET} li.faceted-tag-selected[title="${title}"]
    The page title is  ${title}

The page title is
    [Arguments]  ${title}
    Wait until keyword succeeds  10s  0.5s  Element text should be  ${HEADING}  ${title}

The page URL is
    [Documentation]  Location without its query string and hash (the faceted query is written in the hash)
    [Arguments]  ${url}
    ${location}=  Execute javascript  return window.location.origin + window.location.pathname;
    Should be equal  ${location}  ${url}

The results list
    [Arguments]  @{titles}
    FOR  ${title}  IN  @{titles}
        Wait until element contains  ${RESULTS}  ${title}
    END

The results do not list
    [Arguments]  ${title}
    Element should not contain  ${RESULTS}  ${title}

Table column labels
    [Documentation]  Labels of the z3c.table header cells (the select-all checkbox column has none)
    ${headers}=  Get WebElements  xpath=//table[@id="faceted_table"]/thead//th/span
    ${labels}=  Create list
    FOR  ${header}  IN  @{headers}
        ${label}=  Get text  ${header}
        ${labels}=  Create list  @{labels}  ${label}
    END
    [Return]  ${labels}

The table columns are
    [Arguments]  @{expected}
    ${labels}=  Table column labels
    Should be equal  ${labels}  ${expected}

The collection shows its number of items
    [Documentation]  Number of items next to the collection, in the faceted widget or in the portlet
    [Arguments]  ${title}  ${number}  ${in}=${WIDGET}
    Wait until keyword succeeds  10s  0.5s  Element text should be  ${in} li[title="${title}"] .term-count  ${number}

Add the collection widget portlet
    [Documentation]  "Collection widget portlet" in the left column of the dashboard
    Add the portlet  dashboard  Collection widget portlet

The portlet lists the collections
    [Arguments]  @{titles}
    Wait until element is visible  ${PORTLET}
    FOR  ${title}  IN  @{titles}
        Element should be visible  ${PORTLET} li[title="${title}"] a
    END

Click the collection in the portlet
    [Arguments]  ${title}
    Click link  ${PORTLET} li[title="${title}"] a
    The faceted results are loaded

Add a dashboard template
    [Documentation]  DashboardPODTemplate added to the site through the Add menu (ODT of the documentgenerator demo), available on the collection
    ...              ${collection} (labelled "<dashboard> - <collection>" by the dashboard collections vocabulary)
    [Arguments]  ${title}  ${collection}  ${max_objects}
    Go to  ${PLONE_URL}
    Open the add menu
    Click the add menu item  dashboardpodtemplate
    Wait until element is visible  css=#form-widgets-IBasic-title
    Input text  css=#form-widgets-IBasic-title  ${title}
    ${odt}=  Evaluate  os.path.join(os.path.dirname(__import__('collective.documentgenerator', fromlist=['']).__file__), 'profiles', 'demo', 'templates', 'modele_general.odt')  modules=os
    Choose file  css=#form-widgets-odt_file-input  ${odt}
    Click element  xpath=//label[normalize-space()="Dashboard - ${collection}"]
    Input text  css=#form-widgets-max_objects  ${max_objects}
    Save the add form
    The status message contains  Item created

The generation link is shown
    [Arguments]  ${title}  ${format}  ${description}
    Wait until element is visible  ${GENERATION_LINKS} .template-link
    Element text should be  ${GENERATION_LINKS} .template-link-title  ${title}
    Element should be visible  ${GENERATION_LINKS} a[title="${description}"] img[alt="${title} ${format}"]

The generation link is not shown
    Page should not contain element  ${GENERATION_LINKS}

Record the submitted form
    [Documentation]  The browser keeps the form instead of posting it (no document generation by LibreOffice)
    Execute javascript  HTMLFormElement.prototype.submit = function () { window.submittedForm = this; };

Click the generation link
    [Arguments]  ${title}  ${format}
    Click element  ${GENERATION_LINKS} img[alt="${title} ${format}"]

The submitted form field is
    [Arguments]  ${name}  ${value}
    ${submitted}=  Execute javascript  return window.submittedForm.elements['${name}'].value;
    Should be equal  ${submitted}  ${value}

The faceted query of the submitted form selects
    [Documentation]  JSON of the faceted query (Faceted.Query), with the criterion ${criterion} = ${value}
    [Arguments]  ${criterion}  ${value}
    ${query}=  Execute javascript  return JSON.parse(window.submittedForm.elements['facetedQuery'].value)['${criterion}'].toString();
    Should be equal  ${query}  ${value}

The generation form was submitted to
    [Arguments]  ${url}
    ${name}=  Execute javascript  return window.submittedForm ? window.submittedForm.name : '';
    Should be equal  ${name}  podTemplateForm
    ${action}=  Execute javascript  return window.submittedForm.action;
    Should be equal  ${action}  ${url}
    ${target}=  Execute javascript  return window.submittedForm.target;
    Should be equal  ${target}  _blank

Select only the result
    [Documentation]  Unselects every row of the table, then selects the row of ${uid}
    [Arguments]  ${uid}
    Unselect checkbox  css=#select_unselect_items
    Checkbox should not be selected  css=input[name="select_item"][value="${uid}"]
    Select checkbox  css=input[name="select_item"][value="${uid}"]
