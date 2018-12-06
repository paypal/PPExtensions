define(["base/js/namespace", "base/js/dialog", "tree/js/notebooklist", "base/js/utils", "jquery"], function (Jupyter, dialog, notebooklist, utils, $) {
  var ScheduleOperation = function () {
    this.base_url = Jupyter.notebook_list.base_url;
    this.bind_events();
  };

  ScheduleOperation.prototype = Object.create(notebooklist.NotebookList.prototype);

  ScheduleOperation.prototype.bind_events = function () {
    var that = this;
    $(".schedule-button").click($.proxy(that.schedule_selected, this));
  };

  ScheduleOperation.prototype.schedule_selected = function () {
    var that = this;
    var selected = Jupyter.notebook_list.selected;
    if (selected.length > 1) {
      alert("Cannot schedule more than one notebook at the same time!");
      return false;
    }

    // Part1 Schedule
    var lst = Array(20).fill(0).map((i, j) => j + 1);
    var every_num = $("<select id= \"num\"></select>");
    $.each(lst, function (i, el) { every_num.append(new Option(el, el)); });
    var every_unit = $("<select id=\"unit\"></select>");
    var unit_list = ["hours", "days", "weeks"];
    $.each(unit_list, function (i, el) { every_unit.append(new Option(el, el)); });

    every_unit.change(function () {
      switch (every_unit.val()) {
        case "hours":
          lst = Array(20).fill(0).map((i, j) => j + 1);
          break;
        case "days":
          lst = Array(30).fill(0).map((i, j) => j + 1);
          break;
        case "weeks":
          lst = Array(52).fill(0).map((i, j) => j + 1);
      }
      every_num.empty();
      $.each(lst, function (i, el) { every_num.append(new Option(el, el)); });
    });

    var start_time = $("<input type=\"time\" id=\"time\">").val("00:00");
    var start_date = $("<input type=\"date\" id=\"date\">").val(new Date().toISOString().split("T")[0]);
    var runs = $("<select id= \"runs\"></select>");
    var runs_list = ["None", "1 time", "2 times", "3 times", "4 times", "5 times", "10 times", "50 times", "100 times"];
    $.each(runs_list, function (i, el) { runs.append(new Option(el, el)); });

    var schedule_part = $("<div/>")
      .append("<label for=\"num\">Every:</label>")
      .append(every_num)
      .append(every_unit)
      .append("<br>")
      .append("<label for=\"time\">Start at:</label>")
      .append(start_time)
      .append("<br>")
      .append("<label for=\"date\">Start on:</label>")
      .append(start_date)
      .append("<br>")
      .append("<label for=\"end\">End after</lable>")
      .append(runs);

    // Part2 Notification
    var notification = $("<p>Please check the box and input the emails (separate by comma) that you want us to send email alert to</p>");
    var notify_on_failure = $("<input type='checkbox'  name='checkbox1' checked='checked'/>").css("margin-right", "5px");
    var notify_on_success = $("<input type='checkbox'  name='checkbox2'/>").css("margin-right", "5px");
    var email_list_for_failure = $("<input type='text' name='text'/>").css("margin-left", "12px");
    var email_list_for_success = $("<input type='text' name='text'/>");

    var notification_part = $("<div/>")
      .append(notification)
      .append(notify_on_failure)
      .append($("<label for='checkbox1'>Notify on Failure</label>"))
      .append(email_list_for_failure)
      .append("<br/>")
      .append(notify_on_success)
      .append($("<label for='checkbox2'>Notify on Success</label>"))
      .append(email_list_for_success);

    // Integrate
    var dialog_body = $("<div/>").css("display", "block").css("overflow", "auto")
      .append($("<b>Schedule</b>"))
      .append(schedule_part)
      .append($("<hr>").css("border-top", "1px dotted"))
      .append($("<b>Email Notification</b>"))
      .append(notification_part);

    dialog.modal({
      title: "Create Schedule",
      body: dialog_body,
      default_button: "Cancel",
      buttons: {
        Cancel: {},
        Schedule: {
          class: "btn-primary",
          click: function () {
            var emails_failure = "";
            if (notify_on_failure.is(":checked")) {
              emails_failure = email_list_for_failure.val();
            }
            var emails_success = "";
            if (notify_on_success.is(":checked")) {
              emails_success = email_list_for_success.val();
            }
            if (start_date.val() === undefined || start_time.val() === undefined) {
              alert("Please specify the start date and time");
              return false;
            }
            var num_of_run = "None";
            if ($("#runs").val() !== "None") {
                num_of_run = $("#runs").val().split(" ")[0];
            }
            var start = start_date.val() + " " + start_time.val() + ":00";
            var interval = every_num.val() + " " + every_unit.val();
            var notebook_path = selected[0].path;
            var notebook_name = selected[0].name.substr(0, selected[0].name.lastIndexOf("."))
              .replace(new RegExp(/[`~!@#$%^&*()|+=?;:'",<>\{\}\[\]\\\/ ]/gi, "g"), "_");
            var now = new Date();
            var scheduled_time = new Date(start.replace(new RegExp("-", "g"), "/"));
            if (scheduled_time < now) {
              alert("Cannot schedule in the past!");
              return false;
            }
            function schedule () {
                var spin = dialog.modal({
                  title: "Scheduling...",
                  body: $("<div style=\"text-align:center\"><i class=\"fa fa-spinner fa-spin\" style=\"font-size:100px\"></i></div>")
                    .append($("<div style=\"text-align:center\">" +
                                            "<strong>Your notebook will be scheduled in a few seconds." +
                                            "\nNote: If you do not see your notebook in scheduled jobs, " +
                                            "please wait and refresh because scheduler is working on picking up your job." +
                                            "</strong></div>"))
                                            });
                var settings = {
                  data: {
                    "notebook_name": notebook_name,
                    "notebook_path": notebook_path,
                    "emails_failure": emails_failure,
                    "emails_success": emails_success,
                    "start": start,
                    "runs": num_of_run,
                    "interval": interval
                  },
                  method: "POST",
                  success: function () {
                    $(".scheduled_jobs").click().tab("show");
                  spin.modal("hide");
                  },
                  error: function () {
                    spin.modal("hide");
                    dialog.modal({
                      title: "Schedule Failed!",
                      body: $("<div/>").text("Error: something wrong in scheduling, please check your notebook and try again!"),
                      buttons: {
                        OK: { class: "btn-primary" }
                      }
                    });
                  }
                };
                var url = utils.url_path_join(that.base_url, "/scheduler/create_dag");
                utils.ajax(url, settings);
            }
            var url = utils.url_path_join(that.base_url, "/scheduler/check_dag");
            $.get(url + "?notebook_name=" + notebook_name, function (res) {
              if (res === "True") {
                dialog.modal({
                  title: "Please confirm ...",
                  body: "You have already scheduled this notebook, are you sure you want to override it?",
                  buttons: {
                    Cancel: {
                      click: function () {

                      } },
                    Override: {
                      class: "btn-primary",
                      click: function () {
                        var url = utils.url_path_join(that.base_url, "/scheduler/delete_dag");
                        var settings = {
                          data: {
                            "notebook_name": notebook_name
                          },
                          method: "POST"

                        };
                        utils.ajax(url, settings).done(
                          function () { schedule(); }
                        );
                      } }
                  }
                });
              } else {
                schedule();
              }
            });
          }
        }
      }
    });
  };

  return { ScheduleOperation: ScheduleOperation };
});

