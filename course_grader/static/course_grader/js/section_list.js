/*jslint browser: true, plusplus: true */
/*global jQuery, Handlebars, GradePage, gettext, ngettext, interpolate */
GradePage.SectionList = (function ($) {
    "use strict";
    var section_status_queue = [];

    function title_element(section_id) {
        return $("#section-" + section_id).find(".gp-section-link")
                                          .filter(":first");
    }

    function badge_element(section_id) {
        return $("#section-" + section_id).find(".gp-course-grading-link")
                                          .filter(":first")
                                          .find("i");
    }

    function wrapper_element(section_id) {
        return $("#section-" + section_id).find(".gp-section-wrapper");
    }

    function status_element(section_id) {
        return $("#section-" + section_id).find(".gp-course-grading-status")
                                          .filter(":first");
    }

    function sr_status_element(section_id) {
        return $("#section-name-" + section_id).find("span.sr-only")
                                               .filter(":first");
    }

    function draw_section_status(data) {
        var section_id = data.section_id,
            section_name = $("#section-name-" + section_id).html(),
            base,
            text = "",
            len,
            i;

        if (data.hasOwnProperty("error")) {
            base = gettext("error_status %(error)s");
            sr_status_element(section_id).text(gettext("sr-error"));
        } else {
            if (data.unsubmitted_count && data.grading_period_open) {
                sr_status_element(section_id).text(gettext("sr-unsubmitted"));
                title_element(section_id).attr("title",
                    "Submit grades for " + section_name);
                base = ngettext("%(unsubmitted_count)s grade to submit",
                                "%(unsubmitted_count)s grades to submit",
                                data.unsubmitted_count);
            } else {
                if (data.grading_period_open) {
                    badge_element(section_id).addClass("fa-check");
                    wrapper_element(section_id).addClass("gp-section-submitted");
                }
                if (data.submitted_count) {
                    sr_status_element(section_id).text(gettext("sr-submitted"));
                    if (data.submitted_date) {
                        title_element(section_id).attr("title",
                            "View grade receipt for " + section_name);
                        data.submitted_date = GradePage.format_date(data.submitted_date);
                        if (data.accepted_date) {
                            base = ngettext("%(submitted_count)s grade submitted on %(submitted_date)s",
                                            "%(submitted_count)s grades submitted on %(submitted_date)s",
                                            data.submitted_count);
                        } else {
                            sr_status_element(section_id).text(gettext("sr-in-progress"));
                            base = ngettext("%(submitted_count)s grade submission in progress",
                                            "%(submitted_count)s grade submissions in progress",
                                            data.submitted_count);
                        }
                    } else {
                        base = ngettext("%(submitted_count)s grade submitted",
                                        "%(submitted_count)s grades submitted",
                                        data.submitted_count);
                    }
                } else {
                    if (!data.grading_period_open) {
                        sr_status_element(section_id).text(gettext("sr-no-info"));
                        text = gettext("no_submission_information");
                    }
                }
            }
        }

        if (base !== undefined) {
            text = interpolate(base, data, true);
        }
        status_element(section_id).html(text);

        if (data.hasOwnProperty("secondary_sections")) {
            for (i = 0, len = data.secondary_sections.length; i < len; i++) {
                draw_section_status(data.secondary_sections[i]);
            }
        }
    }

    function get_section_status(section_data) {
        var section_id = section_data.section_id,
            data,
            text;

        $.ajax({
            url: section_data.grade_status_url,
            dataType: "json",
            beforeSend: function () {
                badge_element(section_id).addClass("loading-icon");
            },
            success: function (data) {
                badge_element(section_id).removeClass("loading-icon");
                draw_section_status(data.graderoster_status);
            },
            error: function (xhr) {
                badge_element(section_id).removeClass("loading-icon");
                try {
                    data = $.parseJSON(xhr.responseText);
                    if (xhr.status === 404) {
                        text = data.error;
                    } else {
                        text = interpolate(gettext("error_status %(error)s"), data, true);
                    }
                    status_element(section_id).html(text);
                } catch (e) {
                }
            },
            complete: next_section_status,
        });
    }

    function next_section_status() {
        if (section_status_queue.length) {
            var data = section_status_queue.shift();
            if (data.grade_status_url) {
                get_section_status(data);
            } else {
                next_section_status();
            }
        }
    }

    function add_to_queue(data) {
        section_status_queue.push(data);
    }

    function loading_section_list() {
        var template = Handlebars.compile($("#loading-tmpl").html());
        $("#section-list").html(template());
    }

    function draw_section_list(data) {
        var template = Handlebars.compile($("#section-list-tmpl").html()),
            section,
            secondary_section,
            i,
            il,
            j,
            jl;

        Handlebars.registerPartial("section", $("#section-tmpl").html());

        $("#section-list").html(template(data));

        for (i = 0, il = data.sections.length; i < il; i++) {
            section = data.sections[i];
            if (section.grade_status_url !== null) {
                add_to_queue(section);
            }
            if (section.hasOwnProperty("secondary_sections")) {
                for (j = 0, jl = section.secondary_sections.length; j < jl; j++) {
                    secondary_section = section.secondary_sections[j];
                    if (secondary_section.grade_status_url !== null) {
                        add_to_queue(secondary_section);
                    }
                }
            }
        }

        next_section_status();
    }

    function get_section_list(url) {
        $.ajax({
            url: url,
            dataType: "json",
            beforeSend: loading_section_list,
            success: draw_section_list,
            error: function (xhr) {
                console.log(xhr.responseText);
                var data;
                try {
                    data = $.parseJSON(xhr.responseText);
                } catch (e) {
                    data = {error: xhr.responseText};
                }
                $("#section-list").html(data.error);
            }
        });

    }

    function initialize() {
        $("#gp-term-select").change(function () {
            var url = $(this).val();
            if (url) {
                window.location.href = url;
            }
        });
        get_section_list(window.gradepage.sections_url);
    }

    return {
        initialize: initialize,
        add_to_queue: add_to_queue,
        next_section_status: next_section_status
    };
}(jQuery));
