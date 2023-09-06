// currently displaying a faceted navigation?
function has_faceted() {
  return Boolean($("div#faceted-form").length);
}

// Function that allows to generate a document aware of table listing documents in a faceted navigation.
function generatePodDocument(template_uid, output_format, tag) {
    theForm = $(tag).parents('form')[0];
    theForm.template_uid.value = template_uid;
    theForm.output_format.value = output_format;
    // manage the facetedquery
    theForm.facetedQuery.value = JSON.stringify(Faceted.Query);
    var hasCheckBoxes = $('input[name="select_item"]');
    // if there are checkboxes on a faceted, get uids
    if (hasCheckBoxes.length != 0) {
        // if not on a faceted, do not manage uids, we have no table
        if ($('div#faceted-results').length) {
            var uids = selectedCheckBoxes('select_item');
            if (!uids.length) {
                alert(no_selected_items);
                return;
            }
            else {
                // if we unselected some checkboxes, we pass uids
                // else, we pass nothing, it is as if we did selected everything
                // take care that the select/unselect all has also the name "select_item"
                if ($('input[name="select_item"]:not(#select_unselect_items)').length === uids.length) {
                    uids = [];
                }
                theForm.uids.value = uids;
            }
        }
    }
    theForm.submit();
}

function update_collections_count() {
    var url = $("link[rel='canonical']").attr('href') + '/@@json_collections_count';
    $.getJSON(url, function (info) {
        if (info.criterionId) {
            var criterionId = info.criterionId;
            var countByCollection = info.countByCollection;
            countByCollection.forEach(function (item) {
                $('li#' + criterionId + item.uid + ' .term-count').html(item.count);
            });
        }
    });
}

function update_tabs_count() {
    $.getJSON($("body").data("portalUrl") + "/@@json_list_countable_tabs", function (data) {
        data.urls.forEach(function(url) {
            $.get(url + '/@@json_collections_count', function (response) {
                var info = JSON.parse(response);
                var element = $("#portal-globalnav a[href='" + url + "']");
                var itemTotal = 0;
                info.countByCollection.forEach(function (item) {
                    itemTotal += parseInt(item.count);
                });

                var title = element.html();
                var existing_count_title = title.match(/^(.+) \(\d+\)$/);
                if (existing_count_title) {
                    title = existing_count_title[1];
                }

                var new_text = title + " (" + itemTotal + ")";
                element.html(new_text);
            });
        });
        /*  Only manual now
        if (sessionStorage.getItem('tabs_count_timeout') != '0') {
            clearInterval(parseInt(sessionStorage.getItem('tabs_count_timeout')));
            sessionStorage.setItem('tabs_count_timeout', '0');
        }
        if (data.urls.length > 0) {  // to avoid setting timeout when no countable tabs
            var interval = 60 * 60 * 1000;
            setInterval is reset at each page load. Have to create a function called every sec to store timer in session
            sessionStorage.setItem('tabs_count_timeout', setInterval(update_tabs_count, interval));
        }
        */
    });
}

$(document).ready(function () {
  if ($('div[class*="faceted-tagscloud-collection-widget"').length > 0) {
    if (!has_faceted()) {
        update_collections_count();
    }
    $(Faceted.Events).bind(Faceted.Events.AJAX_QUERY_SUCCESS, function() {
        update_collections_count();
    });
  }

  if (sessionStorage.getItem('tabs_count_timeout') === null) {
      sessionStorage.setItem('tabs_count_timeout', '0');
      update_tabs_count();
  }
  $('body').on('click', '#collections-count-refresh', function() {
      update_tabs_count();
  });

  Faceted.Options.FADE_SPEED=0;
  //Faceted.Options.SHOW_SPINNER=false;
});
