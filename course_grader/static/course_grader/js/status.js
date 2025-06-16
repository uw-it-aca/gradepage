/*jslint browser: true, plusplus: true */
/*global jQuery, Highcharts */
var AdminSupport = {};

(function ($) {
    "use strict";
    $(document).ready(function () {
        Highcharts.setOptions({
            global: {
                useUTC: true
            }
        });

        $("#submission-chart").highcharts({
            chart: {
                zoomType: 'x'
            },
            title: { text: null },
            xAxis: {
                type: "datetime",
                min: window.gradepage.charts.submissions.grading_period_open,
                minRange: 15 * 60 * 1000,
                title: { text: null },
                allowDecimals: false,
                plotLines: window.gradepage.charts.submissions.plot_lines
            },
            yAxis: {
                title: { text: "Submissions" },
                allowDecimals: false,
                min: 0
            },
            legend: {
                enabled: false
            },
            credits: {
                enabled: false
            },
            plotOptions: {
                area: {
                    fillColor: {
                        linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1},
                        stops: [
                            [0, Highcharts.getOptions().colors[0]],
                            [1, new Highcharts.Color(Highcharts.getOptions().colors[0]).setOpacity(0).get('rgba')]
                        ]
                    },
                    marker: {
                        radius: 2
                    },
                    lineWidth: 1,
                    states: {
                        hover: {
                            lineWidth: 1
                        }
                    },
                    threshold: null
                },
                line: {
                    marker: {
                        radius: 2
                    },
                    lineWidth: 1,
                    states: {
                        hover: {
                            lineWidth: 1
                        }
                    }
                }
            },
            series: [{
                type: "area",
                name: "Submitted Sections",
                data: window.gradepage.charts.submissions.data
            },{
                type: "line",
                name: "Resubmitted Sections",
                data: window.gradepage.charts.resubmissions.data
            },{
                type: "line",
                name: "Canvas Gradebook Imports",
                data: window.gradepage.charts.grade_imports.canvas
            },{
                type: "line",
                name: "CSV File Imports",
                data: window.gradepage.charts.grade_imports.csv
            }]
        });
    });
}(jQuery));
