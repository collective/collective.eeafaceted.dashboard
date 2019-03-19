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
                if ($('input[name="select_item"]').length === uids.length) {
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
  $.get(url, async=true, function (response) {
      var info = JSON.parse(response);
      if (info.criterionId) {
      var criterionId = info.criterionId;
      var countByCollection = info.countByCollection;
      countByCollection.forEach(function (item) {
        $('li#' + criterionId + item.uid + ' .term-count').html(item.count);
      });
    }
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
  Faceted.Options.FADE_SPEED=0;
  //Faceted.Options.SHOW_SPINNER=false;
});
