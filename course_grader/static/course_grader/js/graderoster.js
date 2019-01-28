/*jslint browser: true, plusplus: true */
/*global jQuery, Handlebars, GradePage, gettext, ngettext, interpolate */
GradePage.GradeRoster = (function ($) {
    "use strict";

    // Grades that are incompatible with incomplete
    var incomplete_blacklist,
        inprogress_save_grade_id,
        remaining_template,
        import_scale_template;

    // Override the default autocomplete filter function to search only from
    // the beginning of the string
    $.ui.autocomplete.filter = function (array, term) {
        var item_id, is_incomplete, matcher;

        item_id = $(document.activeElement).attr("id").replace(/^grade-/, "");
        is_incomplete = $("#incomplete-" + item_id).is(":checked");

        if ($.inArray(term, array) > -1) {
            matcher = new RegExp(".*");
        } else {
            matcher = new RegExp("^" + $.ui.autocomplete.escapeRegex(term), "i");
        }

        return $.grep(array, function (value) {
            if (is_incomplete && incomplete_blacklist.contains(value)) {
                return false;
            }
            return matcher.test(value);
        });
    };

    /*jslint nomen: true*/
    // Override the default _resizeMenu function to resize the menu to the
    // input width
    $.ui.autocomplete.prototype._resizeMenu = function () {
        var ul = this.menu.element;
        ul.outerWidth(this.element.outerWidth());
    };
    /*jslint nomen: false*/

    // Extend Array with a useful method
    Array.prototype.contains = function (val) {
        var i, len;
        for (i = 0, len = this.length; i < len; i++) {
            if (this[i] === val) {
                return true;
            }
        }
        return false;
    };

    function grade_input_selector() {
        return (window.gradepage.is_desktop) ? "input.gp-grade-input"
                                             : "select.gp-grade-select";
    }

    function show_fixed_header() {
        var static_header = $(".gp-global-header"),
            static_header_bottom = static_header.offset().top + static_header.height(),
            page_top = $(window).scrollTop(),
            fixed_header = $(".gp-global-header-fixed");

        // check to see if the header_bottom is offscreen,
        // if so.. slide the fixed_header down -- 0 is top
        if (page_top > static_header_bottom) {
            fixed_header.addClass("slide-down");
        } else {
            fixed_header.removeClass("slide-down");
        }
    }

    function valid_grade(input) {
        input.closest(".form-group").removeClass("has-error");
        input.removeAttr("aria-invalid");
        var status_id = input.attr("id").replace(/^grade-/, "status-");
        $("#" + status_id).children(".gp-invalid-grade").empty();
    }

    function invalid_grade(input, txt) {
        input.closest(".form-group").addClass("has-error");
        input.attr("aria-invalid", "true");
        var status_id = input.attr("id").replace(/^grade-/, "status-");
        $("#" + status_id).children(".gp-invalid-grade").text(txt);
    }

    function normalize_grade(grade) {
        grade = $.trim(grade);
        if (grade.match(/^(?:n|nc|p|h|hw|f|hp|i|cr)$/i)) {
            grade = grade.toUpperCase();
        } else if (grade.match(/^x/i)) {
            grade = gettext("x_no_grade_now");
        } else {
            grade = grade.replace(/^([0-4])?\.([0-9])0+$/, "$1.$2");
            grade = grade.replace(/^\.([0-9])$/, "0.$1");
            grade = grade.replace(/^([0-4])\.?$/, "$1.0");
        }
        return grade;
    }

    function validate_grade(input) {
        var is_incomplete, is_valid, is_hypenated, is_cnc, is_hhppf,
            is_undergrad_numeric, is_grad_numeric, text,
            grade = normalize_grade(input.val()),
            grade_choices = input.data("grade_choices"),
            item_id = input.attr("id").replace(/^grade-/, "");

        input.val(grade);
        if (grade_choices.contains(grade)) {
            is_incomplete = $("#incomplete-" + item_id).is(":checked");
            if (is_incomplete && incomplete_blacklist.contains(grade)) {
                invalid_grade(input, gettext("grade_invalid_incomplete"));
                is_valid = false;
            } else {
                valid_grade(input);
                is_valid = true;
            }
        } else if (grade === "") {
            valid_grade(input);
        } else {
            is_valid = false;
            is_hypenated = grade_choices.contains("N");
            is_cnc = grade_choices.contains("NC");
            is_hhppf = grade_choices.contains("HP");
            is_undergrad_numeric = grade_choices.contains("0.9");
            is_grad_numeric = (grade_choices.contains("1.9") && !is_undergrad_numeric);

            if (is_hypenated && is_cnc && is_undergrad_numeric) {
                // Hyphenated, C/NC, Undergrad 4.0 scale
                if (grade === parseFloat(grade).toString() && grade < 0.7) {
                    text = gettext("grade_invalid_undergrad_lowest_passing");
                } else {
                    text = gettext("grade_invalid_hyphenated_CR_NC_undergrad");
                }
            } else if (is_hypenated && is_cnc && is_grad_numeric) {
                // Hyphenated, C/NC, Graduate 4.0 scale
                if (grade === parseFloat(grade).toString() && grade < 1.7) {
                    text = gettext("grade_invalid_grad_lowest_passing");
                } else {
                    text = gettext("grade_invalid_hyphenated_CR_NC_grad");
                }
            } else if (is_hypenated && is_undergrad_numeric) {
                // Hyphenated, Undergrad 4.0 scale
                if (grade === parseFloat(grade).toString() && grade < 0.7) {
                    text = gettext("grade_invalid_undergrad_lowest_passing");
                } else {
                    text = gettext("grade_invalid_hyphenated_undergrad");
                }
            } else if (is_hypenated && is_grad_numeric) {
                // Hyphenated, Graduate 4.0 scale
                if (grade === parseFloat(grade).toString() && grade < 1.7) {
                    text = gettext("grade_invalid_grad_lowest_passing");
                } else {
                    text = gettext("grade_invalid_hyphenated_grad");
                }
            } else if (is_hhppf && is_grad_numeric) {
                // H/HP/P/F, Graduate 4.0 scale
                if (grade === parseFloat(grade).toString() && grade < 1.7) {
                    text = gettext("grade_invalid_grad_lowest_passing");
                } else {
                    text = gettext("grade_invalid_H_HP_P_F_grad");
                }
            } else if (is_undergrad_numeric) {
                // Undergrad 4.0 scale
                text = gettext("grade_invalid_undergrad_lowest_passing");
            } else if (is_grad_numeric) {
                // Graduate 4.0 scale
                text = gettext("grade_invalid_grad_lowest_passing");
            } else if (is_hypenated && is_cnc) {
                // Hyphenated, C/NC
                text = gettext("grade_invalid_hyphenated_CR_NC");
            } else if (is_cnc) {
                // C/NC
                text = gettext("grade_invalid_CR_NC");
            } else if (is_hypenated && is_hhppf) {
                // Hyphenated, H/HP/P/F
                text = gettext("grade_invalid_hyphenated_H_HP_P_F");
            } else if (is_hhppf) {
                // H/HP/P/F
                text = gettext("grade_invalid_H_HP_P_F");
            }

            invalid_grade(input, (window.gradepage.is_desktop) ? text
                : gettext("grade_invalid_short"));
        }
        return is_valid;
    }

    function validate_all_grades() {
        /*jshint validthis: true */
        var counts = { missing_count: 0, invalid_count: 0 };

        $(".gp-roster-list").find(grade_input_selector())
                            .not(":disabled").each(function () {
                var ret = validate_grade($(this));
                if (ret === undefined) {
                    counts.missing_count += 1;
                } else if (ret === false) {
                    counts.invalid_count += 1;
                }
            });

        if (counts.missing_count || counts.invalid_count) {
            $("button.gp-btn-review").attr("disabled", "disabled");
        } else {
            $("button.gp-btn-review").removeAttr("disabled");
        }
        $("span.gp-roster-grades-left").html(remaining_template(counts));
    }

    function save_grade() {
        /*jshint validthis: true */
        var input_id = $(this).attr("id"), item_id, student_id,
            is_incomplete, is_writing, grade, no_grade_now, grade_choices,
            grade_url, put_data = {};

        // Prevent duplicate PATCH requests
        if (input_id === inprogress_save_grade_id) {
            return;
        }
        inprogress_save_grade_id = input_id;
        item_id = input_id.replace(/^(incomplete|writing|grade)-/, "");
        is_incomplete = $("#incomplete-" + item_id).is(":checked");
        is_writing = $("#writing-" + item_id).is(":checked");
        grade = $.trim($("#grade-" + item_id).val());
        grade_choices = $("#grade-" + item_id).data("grade_choices");
        grade_url = $("#grade-" + item_id).data("grade_url");
        student_id = $("#grade-" + item_id).data("student_id");

        if (is_incomplete && (grade === "" ||
                              incomplete_blacklist.contains(grade))) {
            grade = (grade_choices.contains("0.0")) ? "0.0" :
                    (grade_choices.contains("NC")) ? "NC" : "";
            $("#grade-" + item_id).val(grade);
        }
        no_grade_now = grade.match(/^x/i) ? true : false;

        validate_all_grades();

        if (grade_url) {
            put_data = {
                student_id: student_id,
                grade: grade,
                is_incomplete: is_incomplete,
                is_writing: is_writing,
                no_grade_now: no_grade_now
            };

            $.ajax({
                url: grade_url,
                dataType: "json",
                contentType: "application/json",
                data: JSON.stringify(put_data),
                type: "PATCH",
                headers: {
                    "X-CSRFToken": window.gradepage.csrftoken
                },
                beforeSend: function () {
                    $(".gp-save-status").removeClass("gp-saved")
                                        .addClass("gp-saving")
                                        .text(gettext("grade_save_inprogress"));
                },
                success: function () {
                    $(".gp-save-status").removeClass("gp-saving")
                                        .addClass("gp-saved")
                                        .text(gettext("grade_save_complete"));
                },
                error: function (xhr) {
                    var data;
                    try {
                        data = $.parseJSON(xhr.responseText);
                    } catch (e) {
                        data = {error: xhr.responseText};
                    }
                    $("#status-" + item_id).html(data.error);
                },
                complete: function () {
                    inprogress_save_grade_id = null;
                }
            });
        }
    }

    function decorate_writing_input(el) {
        var title_base;
        if (el.is(":checked")) {
            title_base = gettext("writing_checked_title");
        } else {
            title_base = gettext("writing_unchecked_title");
        }
        el.parent().attr("title", interpolate(title_base, el.data(), true));
    }

    function update_writing() {
        /*jshint validthis: true */
        decorate_writing_input($(this));
        save_grade.call($(this));
    }

    function decorate_incomplete_input(el) {
        /*jshint validthis: true */
        var wrapper = el.closest(".gp-inc-wrapper"),
            is_incomplete_checked = el.is(":checked"),
            title_base,
            label_base;
        if (is_incomplete_checked) {
            wrapper.addClass("gp-inc-checked");
            wrapper.find(".gp-default-grade-overlay").css("display", "inline");
            label_base = gettext("grade_label_incomplete");
            title_base = gettext("incomplete_checked_title");
        } else {
            wrapper.removeClass("gp-inc-checked");
            wrapper.find(".gp-default-grade-overlay").css("display", "none");
            label_base = gettext("grade_label");
            title_base = gettext("incomplete_unchecked_title");
        }
        el.parent().attr("title", interpolate(title_base, el.data(), true));
        wrapper.find(grade_input_selector())
               .attr("aria-label", interpolate(label_base, el.data(), true));

        if (!window.gradepage.is_desktop) {
            wrapper.find(grade_input_selector() + " option").each(function () {
                if (incomplete_blacklist.contains($(this).val())) {
                    if (is_incomplete_checked) {
                        $(this).attr("disabled", "disabled");
                    } else {
                        $(this).removeAttr("disabled");
                    }
                }
            });
        }
    }

    function update_incomplete() {
        /*jshint validthis: true */
        decorate_incomplete_input($(this));
        save_grade.call($(this));
    }

    function select_grade(ev, ui) {
        /*jshint validthis: true */
        $(this).val(ui.item.value);
        save_grade.call($(this));
    }

    function loading_graderoster() {
        $(".gp-save-status").empty();
        var template = Handlebars.compile($("#loading-tmpl").html());
        $("#graderoster-content").html(template());
    }

    function submit_in_progress() {
        var template = Handlebars.compile($("#submitting-tmpl").html());
        $("#graderoster-content").html(template());
    }

    function open_autocomplete() {
        /*jshint validthis: true */
        $(this).attr("ac_state", "open");
    }

    function close_autocomplete() {
        /*jshint validthis: true */
        $(this).attr("ac_state", "closed");
    }

    function create_autocomplete() {
        /*jshint validthis: true */
        if ($(this).attr("ac_state") === undefined) {
            $(this).autocomplete({
                minLength: 0,
                delay: 0,
                source: $(this).data("grade_choices"),
                change: save_grade,
                select: select_grade,
                open: open_autocomplete,
                close: close_autocomplete,
            });
        }
        if ($(this).attr("ac_state") !== "open") {
            $(this).autocomplete("search");
        }
    }

    function toggle_header_position(ev) {
        $(".gp-global-header-fixed.gp-grade-roster-header-global-fixed")
            .css("position", (ev.type === "focus") ? "absolute" : "");
    }

    function create_grade_select() {
        /*jshint validthis: true */
        var i,
            len,
            val = normalize_grade($(this).val()),
            choices = $(this).data("grade_choices");

        if (choices.contains(val)) {
            $(this).empty();
        } else {
            $(this).find("option").attr("disabled", "disabled");
        }
        for (i = 0, len = choices.length; i < len; i++) {
            $(this).append($("<option>", {
                value: choices[i],
                text: choices[i],
                selected: (val === choices[i]) ? true : false
            }));
        }
        $(this).change(save_grade);
    }

    function toggle_view_scale(ev) {
        /*jshint validthis: true */
        var submissions = $(this).data("submissions"),
            container = $("#gp-import-scale-display"),
            i,
            len;
        ev.preventDefault();

        if (container.is(":visible")) {
            $(this).attr("title", gettext("conversion_scale_view_title"))
                   .text(gettext("conversion_scale_view"));
            container.hide();
        } else {
            $(this).attr("title", gettext("conversion_scale_hide_title"))
                   .text(gettext("conversion_scale_hide"));

            for (i = 0, len = submissions.length; i < len; i++) {
                if (submissions[i].grade_import !== null) {
                    container.html(import_scale_template(submissions[i].grade_import))
                             .show();
                    break;
                }
            }
        }
    }

    function select_view_scale() {
        /*jshint validthis: true */
        var submissions = $(this).data("submissions"),
            container = $("#gp-import-scale-display");
        container.html(import_scale_template(submissions[$(this).val()].grade_import))
                 .show();
    }

    function draw_submitted_graderoster(data) {
        /*jshint validthis: true */
        var template = Handlebars.compile($("#confirmation-tmpl").html());
        Handlebars.registerPartial("student", $("#student-tmpl").html());
        Handlebars.registerPartial("grade", $("#grade-tmpl").html());
        Handlebars.registerHelper("multiple_grade_imports", function (count, options) {
            return (count > 1) ? options.fn(this) : options.inverse(this);
        });

        $(".gp-grade-roster-state").text(gettext("submitted_grades"));
        $(".gp-btn-print-container").show();  // Print button
        $("#graderoster-content").html(template(data.graderoster));
        $(".gp-submitted-grade").empty();

        // View grade import scales
        if (data.graderoster.has_grade_imports) {
            import_scale_template = Handlebars.compile($("#import-scale-tmpl").html());
            $("#gp-view-scale").data("submissions", data.graderoster.submissions)
                               .click(toggle_view_scale);
            $("#gp-select-scale").data("submissions", data.graderoster.submissions)
                                 .change(select_view_scale);
        }
        $(window).on("scroll", show_fixed_header);
    }

    function draw_editable_graderoster(data) {
        var graderoster = data.graderoster,
            template = Handlebars.compile($("#edit-tmpl").html()),
            i,
            len,
            sdata,
            grade_choices;

        graderoster.is_desktop = window.gradepage.is_desktop;

        Handlebars.registerPartial("student", $("#student-tmpl").html());
        Handlebars.registerPartial("grade", $("#grade-tmpl").html());
        Handlebars.registerPartial("import_modal", $("#import-modal-tmpl").html());
        $(".gp-grade-roster-state").text(gettext("enter_grades"));
        remaining_template = Handlebars.compile($("#remaining-tmpl").html());
        $("#graderoster-content").html(template(graderoster));

        if (!window.gradepage.is_desktop) {
            // Fix mobile floating toolbar when input is focused
            $("#graderoster-content").on("focus blur", "input,select", toggle_header_position);
        }

        for (i = 0, len = graderoster.grade_choices.length; i < len; i++) {
            if (graderoster.grade_choices[i][0] === "") {
                graderoster.grade_choices[i][0] = gettext("x_no_grade_now");
            }
        }

        for (i = 0, len = graderoster.students.length; i < len; i++) {
            sdata = graderoster.students[i];
            grade_choices = graderoster.grade_choices[sdata.grade_choices_index];

            $("#grade-" + sdata.item_id).data("grade_choices", grade_choices)
                                        .data("grade_url", sdata.grade_url)
                                        .data("student_id", sdata.student_id);

            if (sdata.grade_url) {
                if (window.gradepage.is_desktop) {
                    $("#grade-" + sdata.item_id).focus(create_autocomplete)
                                                .click(create_autocomplete);
                } else {
                    create_grade_select.call($("#grade-" + sdata.item_id));
                }
                if (sdata.allows_incomplete) {
                    $("#incomplete-" + sdata.item_id)
                        .data("student_firstname", sdata.student_firstname)
                        .data("student_lastname", sdata.student_lastname)
                        .click(update_incomplete);
                    decorate_incomplete_input($("#incomplete-" + sdata.item_id));
                }
                if (sdata.allows_writing_credit) {
                    $("#writing-" + sdata.item_id)
                        .data("student_firstname", sdata.student_firstname)
                        .data("student_lastname", sdata.student_lastname)
                        .click(update_writing);
                    decorate_writing_input($("#writing-" + sdata.item_id));
                }

                // If grade is null and grade "N" is allowed, pre-set it
                if (sdata.grade === null && !sdata.has_incomplete &&
                        grade_choices.contains("N")) {
                    $("#grade-" + sdata.item_id).val("N");
                }
            } else {
                $("#incomplete-" + sdata.item_id).attr("disabled", "disabled");
                $("#writing-" + sdata.item_id).attr("disabled", "disabled");
                $("#grade-" + sdata.item_id).attr("disabled", "disabled");
            }
        }

        $(".gp-import-selector select").change(GradePage.Import.select_import);
        $("button.gp-btn-review").click(review_grades);
        $(window).on("scroll", show_fixed_header);
        validate_all_grades();

        GradePage.Import.auto_import();
    }

    function draw_graderoster(data) {
        var unsubmitted = $.grep(data.graderoster.students, function (e) {
            return e.grade_url !== null;
        });

        if (unsubmitted.length) {
            draw_editable_graderoster(data);
        } else {
            draw_submitted_graderoster(data);
        }
    }

    function draw_graderoster_error(xhr) {
        var data, template, source;
        try {
            data = $.parseJSON(xhr.responseText);
        } catch (e) {
            data = {error: xhr.responseText};
        }
        if (xhr.status === 409) {
            draw_graderoster(data);
        } else {
            source = $("#" + xhr.status + "-tmpl").html();
            if (source) {
                template = Handlebars.compile(source);
                $("#graderoster-content").html(template(data));
            }
        }
    }

    function initialize() {
        if (window.gradepage.graderoster_url) {
            incomplete_blacklist = [gettext("x_no_grade_now"), "N", "CR"];
            $.ajax({
                url: window.gradepage.graderoster_url,
                dataType: "json",
                beforeSend: loading_graderoster,
                success: draw_graderoster,
                error: draw_graderoster_error
            });
        }
    }

    function submit_grades() {
        $.ajax({
            url: window.gradepage.graderoster_url,
            dataType: "json",
            contentType: "application/json",
            type: "POST",
            headers: {
                "X-CSRFToken": window.gradepage.csrftoken
            },
            beforeSend: submit_in_progress,
            success: draw_submitted_graderoster,
            error: draw_graderoster_error
        });
    }

    function draw_review_graderoster(data) {
        var template = Handlebars.compile($("#review-tmpl").html());
        Handlebars.registerPartial("student", $("#student-tmpl").html());
        Handlebars.registerPartial("grade", $("#grade-tmpl").html());

        $(".gp-grade-roster-state").text(gettext("review_submit_grades"));
        $("#graderoster-content").html(template(data.graderoster));

        $("button.gp-btn-back").click(initialize);
        $("button.gp-btn-submit").click(submit_grades);
        $(window).on("scroll", show_fixed_header);
    }

    function review_grades() {
        /*jshint validthis: true */
        var put_data = [];
        $(".gp-roster-list").find(grade_input_selector())
                            .not(":disabled").each(function () {
                var item_id = $(this).attr("id").replace(/^grade-/, ""),
                    grade = $.trim($(this).val()),
                    no_grade_now = grade.match(/^x/i) ? true : false;

                put_data.push({
                    student_id: $(this).data("student_id"),
                    grade: grade,
                    is_incomplete: $("#incomplete-" + item_id).is(":checked"),
                    is_writing: $("#writing-" + item_id).is(":checked"),
                    no_grade_now: no_grade_now
                });
            });

        $.ajax({
            url: window.gradepage.graderoster_url,
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify(put_data),
            type: "PUT",
            headers: {
                "X-CSRFToken": window.gradepage.csrftoken
            },
            beforeSend: loading_graderoster,
            success: draw_review_graderoster,
            error: draw_graderoster_error
        });
    }

    return {
        initialize: initialize,
        normalize_grade: normalize_grade
    };
}(jQuery));
