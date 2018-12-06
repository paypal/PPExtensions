define(["jquery",
  "base/js/namespace",
  "base/js/utils",
  "./scheduler"
], function ($, Jupyter, utils, scheduleoperation) {
  function load_ipython_extension () {
    var scheduler_html = $("<button title=\"Schedule selected\" class=\"schedule-button btn btn-default btn-xs\">Schedule</button>");
    var scheduler_tab_html = $.parseHTML("<li><a href=\"#scheduledjobs\" class=\"scheduled_jobs\" data-toggle=\"tab\">Scheduled Jobs</a></li>");
    var scheduler_tab_content_html = $.parseHTML("         <div id=\"scheduledjobs\" class=\"tab-pane\">\n" +
            "           <div id=\"schedule_toolbar\" class=\"row\" style=\"margin-top:10px; margin-bottom:10px\">\n" +
            "            <div class=\"col-sm-8 no-padding\">\n" +
            "              <span id=\"schedule_list_info\">Currently scheduled airflow jobs</span>\n" +
            "            </div>\n" +
            "            <div class=\"col-sm-4 no-padding tree-buttons\">\n" +
            "              <span id=\"schedule_buttons\" class=\"pull-right\">\n" +
            "              <button id=\"refresh_schedule_list\" title=\"Refresh schedule list\" class=\"btn btn-default btn-xs\"><i class=\"fa fa-refresh\"></i></button>\n" +
            "              </span>\n" +
            "            </div>\n" +
            "           </div>\n" +
            "           <div class=\"panel-group\" id=\"scheduled\" >\n" +
            "            <div class=\"panel panel-default\">\n" +
            "              <div class=\"panel-heading\">\n" +
            "                <a data-toggle=\"collapse\" data-target=\"#collapseThree\" href=\"#\">\n" +
            "                  Airflow Jobs:\n" +
            "                </a>\n" +
            "              </div>\n" +
            "              <div id=\"collapseThree\" class=\"collapse in\">\n" +
            "                <div class=\"panel-body\">\n" +
            "                  <div id=\"schedule_list\">\n" +
            "                    <div id=\"schedule_list_placeholder\" class=\"row list_placeholder\">\n" +
            "                    </div>\n" +
            "                  </div>\n" +
            "                </div>\n" +
            "              </div>\n" +
            "            </div>\n" +
            "          </div>\n" +
            "        </div>");

    scheduler_html.insertAfter($("button[title|='Edit selected']"));
    $(".tab-content").append(scheduler_tab_content_html);
    $("#tab_content > #tabs").append(scheduler_tab_html);

    var schedule = new scheduleoperation.ScheduleOperation();
    var url_get_dag = utils.url_path_join(Jupyter.notebook_list.base_url, "/scheduler/get_dag?base_url=" + Jupyter.notebook_list.base_url);

    $("#refresh_schedule_list, .scheduled_jobs").click(function () {
      window.history.pushState(null, null, "#scheduledjobs");
      $("#schedule_list_placeholder").load(url_get_dag);
    });

    if (window.location.hash == "#scheduledjobs") {
        $(".scheduled_jobs").click();
    }

    var _selection_changed = Jupyter.notebook_list.__proto__._selection_changed;

    Jupyter.notebook_list.__proto__._selection_changed = function () {
      _selection_changed.apply(this);
      var selected = this.selected;
      if (selected.length === 1 && selected[0].type !== "directory") {
        $(".schedule-button").css("display", "inline-block");
      } else {
        $(".schedule-button").css("display", "none");
      }
    };
    Jupyter.notebook_list._selection_changed();
  }

  return {
    load_ipython_extension: load_ipython_extension
  };
});

