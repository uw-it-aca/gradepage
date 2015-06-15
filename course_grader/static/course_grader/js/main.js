/*jslint browser: true, plusplus: true */
/*global jQuery, Handlebars, moment */
var GradePage = {};

GradePage.format_long_datetime = function(date_str) {
    return moment(date_str).format("MMMM D[,] YYYY [at] h:mm A");
};

GradePage.format_short_date = function(date_str) {
    return moment(date_str).format("MM/DD/YY");
};

GradePage.format_date = function(date_str) {
    if (window.gradepage.is_desktop) {
        return GradePage.format_long_datetime(date_str);
    } else {
        return GradePage.format_short_date(date_str);
    }
};

Handlebars.registerHelper("format_long_datetime", function(datetime) {
    return GradePage.format_long_datetime(datetime);
});

(function ($) {
    "use strict";
    $(document).ready(function () {
        if ("gradepage" in window) {
            if (window.gradepage.sections_url) {
                GradePage.SectionList.initialize();
            } else if (window.gradepage.graderoster_url) {
                GradePage.GradeRoster.initialize();
            }
        }
    });
}(jQuery));
