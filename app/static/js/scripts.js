//
//                    _)         |             _)
//    __|   __|   __|  |   __ \  __|   __|      |   __|
//  \__ \  (     |     |  |   |  |   \__ \      | \__ \
//  ____/ \___| _|    _|  .__/  \__| ____/ _|   | ____/
//                       _|                 ___/
//

// included in templates/admin/base.html
// Find and parse all forms within parent element...
function constructUrlParams(parentElement) {
    let urlParams = new URLSearchParams(window.location.search);
    let forms = jQuery(parentElement).find('form');
    jQuery(forms).each(function (index, el) {
        let formData = jQuery(el).serializeArray();
        jQuery(formData).each(function (_, field) {
            urlParams.set(field.name, field.value);
        });
    });

    return urlParams;
}