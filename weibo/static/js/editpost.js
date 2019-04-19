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
    $("#editpost-btn").click(function () {
		$("#editpost_alert").hide();
        $("#editpost_alert").empty();
		var editpost_form = {};
		editpost_form.content = $("#editpost-content").val();
		editpost_form.post_id = $("#post-id").val();
        $.ajax({
            type: "POST",
            url: "http://localhost:8888/edit_post",
            dataType: "json",
            data: editpost_form,
            success: function (data) {
                if (data == "success") {
                    $("#editpost_success").text("Update Success!");
                    $("#editpost_success").slideDown(300);
                    setTimeout(function () { location.href = "http://localhost:8888/home"; }, 2000);
                    return;
                }
                else {
					$("#editpost_alert").text(data);
					$("#editpost_alert").slideDown(300);
				}
            }
        });
    });
});
