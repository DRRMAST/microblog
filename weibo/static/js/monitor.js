
$(function () {

    $("#leave-btn").click(function () {
        $.ajax({
            type: "POST",
            url: "http://localhost:8888/logout",
            dataType: "json",
            success: function (data) {
                if (data == "success") {
                    location.href = "http://localhost:8888";
                }
            }
        });
    });
    $("#changepwd-btn").click(function () {
        $.ajax({
            type: "GET",
            url: "http://localhost:8888/changepwd",
            success: function (data) {
                 location.href = "http://localhost:8888/changepwd";
            }
        });
    });
    $("#post-btn").click(function () {
		$("#post_alert").hide();
        $("#post_alert").empty();
		var post_form = {};
		post_form.content = $("#content").val();
        $.ajax({
            type: "POST",
            url: "http://localhost:8888/home",
            dataType: "json",
            data: post_form,
            success: function (data) {
                if (data == "success") {
                    $("#post_success").text("Post Success!");
                    $("#post_success").slideDown(300);
                    setTimeout(function () { location.href = "http://localhost:8888/home"; }, 2000);
                    return;
                }
                $("#post_alert").text("You must type some letters in content");
                $("#post_alert").slideDown(300);
            }
        });
    });
});

