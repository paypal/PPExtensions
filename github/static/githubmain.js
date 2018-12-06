define(["jquery",
  "base/js/namespace",
  "base/js/utils",
  "./github"
], function ($, Jupyter, utils, githuboperation) {
  function load_ipython_extension () {
    var github_html = $("<div id=\"github\" class=\"btn-group\">\n" +
            "                  <button class=\"dropdown-toggle btn btn-default btn-xs\" data-toggle=\"dropdown\">\n" +
            "                  <span>Sharing</span>\n" +
            "                  <span class=\"caret\"></span>\n" +
            "                  </button>\n" +
            "                  <ul id=\"new-menu\" class=\"dropdown-menu\">\n" +
            "                      <li role=\"presentation\" id=\"privategithubpush\">\n" +
            "                         <a role=\"menuitem\" tabindex=\"-1\" class=\"private-github-push\">Push to Github</a>\n" +
            "                      </li>\n" +
            "                      <li role=\"presentation\" id=\"privategithubpull\">\n" +
            "                         <a role=\"menuitem\" tabindex=\"-1\" class=\"private-github-pull\">Pull from Github</a>\n" +
            "                      </li>\n" +
            "                  </ul>\n" +
            "                </div>");

    $(".tree-buttons > .pull-right").prepend(github_html);

    var _selection_changed = Jupyter.notebook_list.__proto__._selection_changed;

    var gitoperation = new githuboperation.GithubOperation();

    Jupyter.notebook_list.__proto__._selection_changed = function () {
      _selection_changed.apply(this);
      var selected = this.selected;
      if (selected.length === 1) {
        $(".private-github-push").css("display", "block");
      } else {
        $(".private-github-push").css("display", "none");
      }
    };
    Jupyter.notebook_list._selection_changed();
  }

  return {
    load_ipython_extension: load_ipython_extension
  };
});

