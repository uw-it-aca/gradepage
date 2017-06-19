/*jslint browser: true, plusplus: true */
/*global jQuery, Highcharts */
var GradePage = {};

GradePage.AdminSupport = (function ($) {
    "use strict";
    function toggle_conversion_scale(ev) {
        /*jshint validthis: true */
        ev.preventDefault();
        if ($(this).next().is(":visible")) {
            $(this).text("View").next().hide();
        } else {
            $(this).text("Hide").next().show();
        }
    }

    return {
        toggle_conversion_scale: toggle_conversion_scale
    };
}(jQuery));

(function ($) {
    "use strict";
    $(document).ready(function () {
        $("table.table").dataTable({
            "searching": false,
            "order": [[ 0, "asc" ]],
            "paging": true,
            "pageLength": 25,
            "scrollCollapse": true
        });

        Highcharts.setOptions({
            global: {
                useUTC: false
            }
        });

        $("#submission-chart").highcharts({
            chart: {
                height: 160
            },
            title: { text: null },
            xAxis: {
                type: "datetime",
                zoomType: "x",
                maxZoom: 15 * 60 * 1000,
                title: { text: null },
                allowDecimals: false
            },
            yAxis: {
                title: { text: "Submissions" },
                allowDecimals: false
            },
            tooltip: {
                shared: true
            },
            legend: {
                enabled: false
            },
            credits: {
                enabled: false
            },
            plotOptions: {
                column: {
                    pointStart: Date.parse(window.gradepage.grading_period_open),
                    pointInterval: 12 * 3600 * 1000
                }
            },
            series: [{
                type: "column",
                name: "Submissions",
                data: window.gradepage.chart_data
            }]
        });

        $("a.gp-conv-scale-open").click(GradePage.AdminSupport.toggle_conversion_scale);
    });
}(jQuery));
