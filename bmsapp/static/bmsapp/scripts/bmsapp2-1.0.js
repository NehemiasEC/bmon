// Generated by CoffeeScript 1.6.3
(function() {
  window.AN = {};

  AN.update_chart_list = function() {
    var url;
    url = "" + ($("#BaseURL").text()) + "chart_list/" + ($("#select_group").val()) + "/" + ($("#select_bldg").val()) + "/";
    return $("#select_chart").load(url, function() {
      return $("#select_chart").trigger("change");
    });
  };

  AN.update_bldg_list = function() {
    return $("#select_bldg").load("" + ($("#BaseURL").text()) + "bldg_list/" + ($("#select_group").val()) + "/", function() {
      return $("#select_bldg").trigger("change");
    });
  };

  $(function() {
    $("#select_group").change(AN.update_bldg_list);
    return $("#select_bldg").change(AN.update_chart_list);
  });

}).call(this);
