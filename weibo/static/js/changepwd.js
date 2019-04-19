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
    $("#changepwd_submit").click(function () {
        $("#changepwd_alert").hide();
        $("#changepwd_alert").empty();
        var changepwd_form = {};
        changepwd_form.oldpwd = $("#changepwd_oldpwd").val();
        changepwd_form.newpwd = $("#changepwd_newpwd").val();
        changepwd_form.confirm = $("#changepwd_confirm").val();
        var result = check_passwd(changepwd_form);
        if (result != "success") {
            $("#changepwd_alert").text(result);
            $("#changepwd_alert").slideDown(300);
            return;
        }
        $.ajax({
            type: "POST",
            url: "http://localhost:8888/changepwd",
            dataType: "json",
            data: changepwd_form,
            success: function (data) {
                if (data == "success") {
					$("#changepwd_success").text("Change Password Success!");
                    $("#changepwd_success").slideDown(300);
                    setTimeout(function () { location.href = "http://localhost:8888/home"; }, 2000);
                    return;
                }
                else {
                    $("#changepwd_alert").text("Your Old Password is Wrong");
                    $("#changepwd_alert").slideDown(300);
                }
            }
        });
    });
});

function check_passwd(changepwd_form) {
    if (changepwd_form.oldpwd.length == 0 || changepwd_form.newpwd.length == 0 || changepwd_form.confirm.length == 0) {
        return "Password shouldn't be null";
    }
    else if (changepwd_form.oldpwd.length < 6 || changepwd_form.newpwd.length < 6 || changepwd_form.confirm.length < 6) {
        return "Password should at least 6 characters";
    }
    else if (changepwd_form.newpwd != changepwd_form.confirm) {
        return "Your password can't be confirmed";
    }
    else {
        return "success";
    }
}
