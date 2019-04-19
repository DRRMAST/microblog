$(document).ready(function() {
  $('body').particleground({
    dotColor: '#5cbdaa',
    lineColor: '#5cbdaa'
  });
});

$(function () {
    $("#registration_tab").click(function () {
        $("#login_tab").removeClass("is-active");
        $("#login_tab a").removeAttr("aria-selected");
        $("#login_panel").removeClass("is-active");
        $("#registration_tab").addClass("is-active");
        $("#registration_tab a").attr("aria-selected", "true");
        $("#registration_panel").addClass("is-active");
        $("#login_alert").hide();
        $("#login_alert").empty();
    });
    $("#login_tab").click(function () {
        $("#registration_tab").removeClass("is-active");
        $("#registration_tab a").removeAttr("aria-selected");
        $("#registration_panel").removeClass("is-active");
        $("#login_tab").addClass("is-active");
        $("#login_tab a").attr("aria-selected", "true");
        $("#login_panel").addClass("is-active");
        $("#registration_alert").hide();
        $("#registration_alert").empty();
    });
    $("#login_submit").click(function () {
        $("#login_alert").hide();
        $("#login_alert").empty();
        var login_form = {};
        login_form.email = $("#login_email").val();
        login_form.password = $("#login_password").val();
        result = check_login(login_form);
        if (result != "success") {
            $("#login_alert").text(result);
            $("#login_alert").slideDown(300);
            return;
        }
        $.ajax({
            type: "POST",
            url: "http://localhost:8888/login",
            dataType: "json",
            data: login_form,
            success: function (data) {
                if (data == "success") {
                    location.href = "http://localhost:8888/home";
                }
                else {
                    $("#login_alert").text("Your Email or Password is incorrect");
                    $("#login_alert").slideDown(300);
                }
            }
        });
    });
    $("#registration_submit").click(function () {
        $("#registration_alert").hide();
        $("#registration_alert").empty();
        var registration_form = {};
        registration_form.email = $("#registration_email").val();
        registration_form.password = $("#registration_password").val();
        registration_form.confirm = $("#registration_confirm").val();
        var result = check_registration(registration_form);
        if (result != "success") {
            $("#registration_alert").text(result);
            $("#registration_alert").slideDown(300);
            return;
        }
        $.ajax({
            type: "POST",
            url: "http://localhost:8888/registration",
            dataType: "json",
            data: registration_form,
            success: function (data) {
                if (data == "success") {
                    $("#registration_success").text("Registration Success!");
                    $("#registration_success").slideDown(300);
                    setTimeout(function () { location.href = "http://localhost:8888"; }, 2000);
                    return;
                }
                $("#registration_alert").text("Email already exist");
                $("#registration_alert").slideDown(300);
            }
        });
    });
});

function check_login(login_form) {
    var reg = /^\s*([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+@([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+\.[a-zA-Z]{2,3}\s*$/;
    if (!reg.test(login_form.email)) {
        return "Invalid e-mail address";
    }
    else if (login_form.password.length == 0) {
        return "Password shouldn't be null"
    }
    else if (login_form.password.length < 6) {
        return "Password should at least 6 characters"
    }
    else {
        return "success";
    }
}

function check_registration(registration_form) {
    var reg = /^\s*([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+@([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+\.[a-zA-Z]{2,3}\s*$/;
    if (!reg.test(registration_form.email)) {
        return "Invalid e-mail address";
    }
    else if (registration_form.password.length == 0 || registration_form.confirm.length == 0) {
        return "Password shouldn't be null";
    }
    else if (registration_form.password.length < 6 || registration_form.confirm.length < 6) {
        return "Password should at least 6 characters";
    }
    else if (registration_form.password != registration_form.confirm) {
        return "Your password can't be confirmed";
    }
    else {
        return "success";
    }
}
