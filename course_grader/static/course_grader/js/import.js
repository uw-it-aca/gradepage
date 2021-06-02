/*jslint browser: true, plusplus: true */
/*global jQuery, Handlebars, GradePage, GradeConversionCalculator, gettext, interpolate */
GradePage.Import = (function ($) {
    "use strict";

    var import_data,
        conversion_scale_data = {};

    function valid_grade(data) {
        var grade = data.imported_grade,
            grade_choices = $("#grade-" + data.item_id).data("grade_choices");

        if (grade_choices === null) {
            return true;
        }

        grade = GradePage.GradeRoster.normalize_grade(grade);

        // Trim decimal precision from 4.0 grades
        grade = grade.replace(/^([0-4])\.(\d)\d+?$/, "$1.$2");

        if (grade === "" || grade_choices.contains(grade)) {
            return true;
        }
        return false;
    }

    function valid_percentage(data) {
        return !isNaN(data.imported_grade);
    }

    function import_in_progress() {
        $(".gp-import-selector select").val("");
        $("#gp-import-modal-body").html(gettext("import_in_progress"));
        $("#gp-import-modal").modal({backdrop: "static"});
    }

    function save_in_progress() {
        $("#gp-import-modal-body").html(gettext("import_save_in_progress"));
        $("#gp-import-modal").modal({backdrop: "static"});
    }

    function update_graderoster() {
        $("#gp-import-modal").on("hidden.bs.modal", GradePage.GradeRoster.initialize);
        $("#gp-import-modal").modal("hide");
    }

    function remove_auto_import() {
        if (window.gradepage.hasOwnProperty("auto_import")) {
            delete window.gradepage.auto_import;
        }
    }

    function save_grades(ev) {
        var url = window.gradepage.import_url + "/" + import_data.grade_import.id,
            converted_grade_data = {},
            conversion_data = ev.data,
            student,
            len,
            i;

        for (i = 0, len = import_data.grade_import.students.length; i < len; i++) {
            student = import_data.grade_import.students[i];
            converted_grade_data[student.student_reg_id] = student.converted_grade;
        }

        $.ajax({
            url: url,
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify({"converted_grades": converted_grade_data,
                                  "conversion_scale": conversion_data}),
            type: "PUT",
            headers: {
                "X-CSRFToken": window.gradepage.csrftoken
            },
            beforeSend: save_in_progress,
            success: update_graderoster,
            error: function (xhr) {
                var data;
                try {
                    data = $.parseJSON(xhr.responseText);
                } catch (e) {
                    data = {error: xhr.responseText};
                }
                $("#gp-import-modal-body").html(data.error);
            }
        });
    }

    function update_prior_scale_selector(data) {
        var template = Handlebars.compile($("#convert-optgroup-tmpl").html());

        $("#select-previous-scale optgroup").remove();
        if (data.terms.length) {
            $("#gp-select-previous").show();
            $("#select-previous-scale").append(template(data));
        } else {
            $("#gp-select-previous").hide();
        }
        conversion_scale_data[data.scale] = data;
    }

    function load_prior_scales(ev, data) {
        if (conversion_scale_data.hasOwnProperty(data.scale)) {
            update_prior_scale_selector(conversion_scale_data[data.scale]);
        } else {
            $.ajax({
                url: "/api/v1/conversion_scales/" + data.scale,
                dataType: "json",
                contentType: "application/json",
                type: "GET",
                headers: {
                    "X-CSRFToken": window.gradepage.csrftoken
                },
                success: update_prior_scale_selector
            });
        }
    }

    function initialize_calculator(opts) {
        return $("#grade-calculator-container").off()
            .on("saveGradeConversion", draw_review_grades)
            .on("cancelGradeConversion", GradePage.GradeRoster.initialize)
            .on("updateGradeScale", load_prior_scales)
            .grade_conversion_calculator(opts);
    }

    function select_previous_scale() {
        /*jshint validthis: true */
        var selected = $(this).val(),
            selected_data,
            i,
            j;

        // Digging through the cached scale data to find a match,
        // this is ugly because the cached data is optimized for easy
        // template rendering..
        $.each(conversion_scale_data, function (scale) {
            var data = conversion_scale_data[scale];
            for (i = 0; i < data.terms.length; i++) {
                for (j = 0; j < data.terms[i].conversion_scales.length; j++) {
                    if (selected === data.terms[i].conversion_scales[j].id.toString()) {
                        selected_data = data.terms[i].conversion_scales[j];
                        return false;
                    }
                }
            }
            return true;
        });

        if (selected_data !== undefined) {
            initialize_calculator({
                "default_scale": selected_data.scale,
                "default_scale_values": selected_data.grade_scale,
                "default_calculator_values": selected_data.calculator_values
            }).find("input:first").focus();
        }
        $("#select-previous-scale").val("0");
    }

    function select_course_scale() {
        /*jshint validthis: true */
        var selected = $(this).val(),
            data,
            i;

        for (i = 0; i < import_data.grade_import.course_grading_schemes.length; i++) {
            data = import_data.grade_import.course_grading_schemes[i];
            if (selected === data.grading_scheme_id.toString()) {
                initialize_calculator({
                    "default_scale": data.scale,
                    "default_scale_values": data.grade_scale,
                    "default_calculator_values": data.calculator_values
                }).find("input:first").focus();
                break;
            }
        }
        $("#select-course-scale").val("0");
    }

    function draw_conversion_calculator(opts) {
        var template = Handlebars.compile($("#convert-tmpl").html());

        $(".gp-grade-roster-state").text(gettext("convert_grades"));
        $("#graderoster-content").html(template(import_data.grade_import));

        conversion_scale_data = {};
        initialize_calculator(opts);
        $("#select-previous-scale").change(select_previous_scale);

        $("#select-course-scale").change(select_course_scale);
        if (import_data.grade_import.course_grading_schemes.length) {
            $("#gp-select-course").show();
        } else {
            $("#gp-select-course").hide();
        }
    }

    function draw_review_grades(ev, data) {
        var template = Handlebars.compile($("#confirm-tmpl").html()),
            students = import_data.grade_import.students,
            grade_scale = data.grade_scale,
            lowest_grade = data.lowest_valid_grade,
            imported_grade,
            converted_grade,
            i,
            j;

        grade_scale.sort(function (a, b) {
            return b.min_percentage - a.min_percentage;
        });

        for (i = 0; i < students.length; i++) {
            converted_grade = lowest_grade;
            imported_grade = students[i].imported_grade;
            for (j = 0; j < grade_scale.length; j++) {
                if (imported_grade >= grade_scale[j].min_percentage) {
                    converted_grade = grade_scale[j].grade;
                    break;
                }
            }
            students[i].converted_grade = converted_grade;
        }

        $(".gp-grade-roster-state").text(gettext("review_import_grades"));
        $("#graderoster-content").html(template(import_data.grade_import));
        $("button.gp-btn-convert-back").click(function (ev) {
            ev.preventDefault();
            draw_conversion_calculator({
                "default_scale": data.scale,
                "default_scale_values": grade_scale,
                "default_calculator_values": data.calculator_values
            });
        });
        $("button.gp-btn-convert-save").click(data, save_grades);
    }

    function initialize_conversion() {
        /*jshint validthis: true */
        var scale = $(this).attr("id").replace(/^gp-convert-scale-/, "");

        $("#gp-import-modal").on("hidden.bs.modal", function () {
            draw_conversion_calculator({
                "default_scale": scale,
                "default_scale_values": [],
                "default_calculator_values": []
            });
        });
        $("#gp-import-modal").modal("hide");
    }

    function update_upload_form() {
        var filename = $("#gp-import-file").val();
        if (filename) {
            $("button.gp-btn-upload").removeAttr("disabled");
        } else {
            $("button.gp-btn-upload").attr("disabled", "disabled");
        }
    }

    function draw_upload_prompt(data) {
        var template = Handlebars.compile($("#upload-tmpl").html());

        // Add context from the graderoster
        data.section_name = window.gradepage.section_name;
        data.expected_grade_count = $(".gp-roster-list").find(
            GradePage.GradeRoster.grade_input_selector()).length;

        $(".gp-import-selector select").val("");
        $("#gp-import-modal-body").html(template(data));
        $("#gp-import-modal").modal({backdrop: "static"});

        $("#gp-import-file").change(update_upload_form);
        $("button.gp-btn-upload").click(create_upload);
        update_upload_form();
    }

    function draw_import_success(data) {
        var template = Handlebars.compile($("#import-tmpl").html()),
            students = data.grade_import.students,
            grade_count = 0,
            valid_grade_count = 0,
            valid_percentage_count = 0,
            override_grade_count = 0,
            unposted_grade_count = 0,
            unposted_with_override_grade_count = 0,
            min_valid = 0.5,
            student,
            len,
            i;

        for (i = 0, len = students.length; i < len; i++) {
            student = students[i];
            if (!student.is_auditor && !student.is_withdrawn &&
                    student.imported_grade !== null &&
                    student.imported_grade !== "") {
                grade_count += 1;

                if (valid_grade(student)) {
                    valid_grade_count += 1;
                } else if (valid_percentage(student)) {
                    valid_percentage_count += 1;
                }

                if (student.is_override_grade) {
                    override_grade_count += 1;
                }

                if (student.has_unposted_grade) {
                    unposted_grade_count += 1;
                    if (student.is_override_grade) {
                        unposted_with_override_grade_count += 1;
                    }
                }
            }
        }

        data.grade_import.grade_count = grade_count;
        data.grade_import.has_valid_grades = false;
        data.grade_import.has_valid_percentages = false;
        data.grade_import.override_grade_count = override_grade_count;
        data.grade_import.unposted_grade_count = unposted_grade_count;
        data.grade_import.unposted_with_override_grade_count = unposted_with_override_grade_count;

        if (grade_count > 0) {
            if (valid_grade_count / grade_count >= min_valid) {
                data.grade_import.has_valid_grades = true;
            } else if (valid_percentage_count / grade_count >= min_valid) {
                data.grade_import.has_valid_percentages = true;
            }
        } else if (data.grade_import.source === "csv") {
            return draw_upload_prompt(data.grade_import);
        }
        data.grade_import.expected_grade_count = $(".gp-roster-list").find(
            GradePage.GradeRoster.grade_input_selector()).length;

        import_data = data;
        $("#gp-import-modal-body").html(template(data.grade_import));

        if (data.grade_import.has_valid_percentages) {
            $("#gp-import-modal-body").find("button")
                                      .click(initialize_conversion);
        } else {
            $("#gp-import-modal-body").find(".gp-import-save-import")
                                      .click(save_grades);
        }
        //$("#gp-import-modal").modal("show");
    }

    function create_upload(ev) {
        var formData = new FormData(),
            filename = $("#gp-import-file").val().split('\\').pop();

        formData.append("file", $("#gp-import-file")[0].files[0]);

        $.ajax({
            url: window.gradepage.upload_url,
            contentType: false,
            processData: false,
            data: formData,
            type: "POST",
            headers: {
                "X-CSRFToken": window.gradepage.csrftoken
            },
            beforeSend: import_in_progress,
            success: draw_import_success,
            error: function (xhr) {
                var data = {};
                try {
                    data = $.parseJSON(xhr.responseText);
                } catch (e) {
                    if (xhr.responseText.indexOf("Request Entity Too Large") !== -1) {
                        data.file_too_large = true;
                    }
                    data.error = xhr.responseText;
                }
                data.file_name = filename;
                draw_upload_prompt(data);
            }
        });
    }

    function create_import(source, source_id) {
        var post_data = {"source": source};
        if (source_id) {
            post_data.source_id = source_id;
        }
        $.ajax({
            url: window.gradepage.import_url,
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify(post_data),
            type: "POST",
            headers: {
                "X-CSRFToken": window.gradepage.csrftoken
            },
            beforeSend: import_in_progress,
            success: draw_import_success,
            error: function (xhr) {
                var data;
                try {
                    data = $.parseJSON(xhr.responseText);
                } catch (e) {
                    data = {error: xhr.responseText};
                }
                $("#gp-import-modal-body").html(data.error);
            },
            complete: remove_auto_import
        });
    }

    function select_import() {
        /*jshint validthis: true */
        var source = $(this).val(),
            data;
        if (source !== "") {
            if (source === "csv") {
                data = {};
                draw_upload_prompt(data);
            } else {
                create_import(source);
            }
        }
    }

    function auto_import() {
        if (window.gradepage.hasOwnProperty("auto_import")) {
            create_import(window.gradepage.auto_import.source,
                          window.gradepage.auto_import.id);
        }
    }

    return {
        auto_import: auto_import,
        select_import: select_import,
        draw_review_grades: draw_review_grades
    };
}(jQuery));
