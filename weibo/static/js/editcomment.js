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
    $("#editcomment-btn").click(function () {
		$("#editcomment_alert").hide();
        $("#editcomment_alert").empty();
		var editpost_form = {};
		editpost_form.content = $("#editcomment-content").val();
		editpost_form.comment_id = $("#comment-id").val();
        $.ajax({
            type: "POST",
            url: "http://localhost:8888/edit_comment",
            dataType: "json",
            data: editpost_form,
            success: function (data) {
                if (data == "success") {
                    $("#editcomment_success").text("Update Success!");
                    $("#editcomment_success").slideDown(300);
                    setTimeout(function () { location.href = "http://localhost:8888/home"; }, 2000);
                    return;
                }
                else {
					$("#editcomment_alert").text(data);
					$("#editcomment_alert").slideDown(300);
				}
            }
        });
    });
});
