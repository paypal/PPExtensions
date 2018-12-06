define(["base/js/namespace", "base/js/dialog", "base/js/utils", "jquery"], function (Jupyter, dialog, utils, $) {

  var git_commit = {
    help: "Commit current notebook",
    icon: "fa-github",
    help_index: "",
    handler: function (env) {
      var re = /^\/notebooks(.*?)$/;
      var filepath = window.location.pathname.match(re)[1];
      var repo = filepath.substring(1, filepath.lastIndexOf("/"));
      var filename = filepath.substring(filepath.lastIndexOf("/") + 1, filepath.length);
      var dialog_body = $("<form id='option'/>")
        .append("<label class=\"radio-inline\"><input type=\"radio\" name=\"optradio\" value='single' checked>Commit this notebook only</label>\n" +
        "<label class=\"radio-inline\"><input type=\"radio\" name=\"optradio\" value='multiple' >Commit all notebooks in this folder</label>");

      dialog.modal({
        title: "Commit Notebook",
        body: dialog_body,
        buttons: {
          Commit: {
            class: "btn-primary",
            click: function () {
              var payload = {
                "repo": repo,
                "filename": filename,
                "option": $("input[name=optradio]:checked", "#option").val()
              };
              if (repo === "/"){ alert("Please commit inside local repo!"); return; }
              var spin = dialog.modal({
                title: "Committing...",
                body: $("<div style=\"text-align:center\"><i class=\"fa fa-spinner fa-spin\" style=\"font-size:100px\"></i></div>")
                  .append($("<div style=\"text-align:center\"><strong>Notebook is being committed to local github repository, please wait for a few seconds.</strong></div>"))
              });
              var settings = {
                method: "POST",
                data: payload,
                success: function (res) {
                  spin.modal("hide");
                  dialog.modal({
                    title: "Commit Success!",
                    body: $("<div/>").append(res),
                    button: {
                      OK: { "class": "btn-primary" }
                    }
                  });
                },
                error: function (res) {
                  spin.modal("hide");
                  dialog.modal({
                    title: "Commit Failed",
                    body: $("<div/>").append(res.responseText),
                    button: {
                      OK: { "class": "btn-primary" }
                    }
                  });
                }
              };
              var url = utils.url_path_join(Jupyter.notebook.base_url, "/github/private_github_commit");
              utils.ajax(url, settings);
            }
          },
          Cancel: {}
        },
        keyboard_manager: env.notebook.keyboard_manager
      });
    }
  };

  function _on_load () {
    var action_name = Jupyter.actions.register(git_commit, "commit", "git");
    Jupyter.toolbar.add_buttons_group([action_name]);
  }
  return { load_ipython_extension: _on_load };
});

