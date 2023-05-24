$(function () {
    bindBtnListGroupItem()
})

function socketConnect(objId) {
    $.ajax({
        url: "/session/id/",
        type: "GET",
        success: function (res) {
            if (res.status) {
                let socket = new WebSocket(`ws://localhost:8000/chat/${res.data}&${objId}/`)
                socket.onmessage = function (event) {
                    console.log(event.data);
                    let message = event.data;
                    addOneMessage(JSON.parse(message));
                }
                bindBtnSendMsg(socket);
            }
        }
    })

}

function bindBtnSendMsg(socket) {
    $("#send-button").click(function () {
        let msg = $("#message-input").val();
        if (msg) {
            socket.send(msg);
            $("#message-input").val('');
        }
    })
}

function bindBtnListGroupItem() {
    $.ajax({})
    $('.list-group-item').click(function () {
        $("#checkSecretKey").modal('show');
        const objId = $(this).attr('id');
        bindBtnCheckSecretKey(objId);
    })
}

function bindBtnCheckSecretKey(objId) {
    $("#sendCheck").click(function () {
        const csrftoken = $.cookie('csrftoken');
        const key = $("#secretKey").val();
        let err = $("#error-msg");
        err.hide();
        $.ajax({
            url: "/chat/checkKey/",
            type: "GET",
            data: {'userid': objId, 'key': key},
            headers: {'X-CSRFtoken': csrftoken},
            dataType: "JSON",
            success: function (res) {
                console.log(res);
                if (res.status) {
                    $("#checkSecretKeyForm")[0].reset();
                    $("#checkSecretKey").modal('hide');
                    reloadMessage(objId);

                } else {
                    err.text(res.msg);
                    err.show();
                }
            }
        });
    })
}

function reloadMessage(objId) {
    $('#chat-messages').empty();
    $.ajax({
        url: "/chat/loadMsg/",
        type: "GET",
        data: {'obj_id': objId},
        dataType: "JSON",
        success: function (res) {
            console.log(res);
            if (res.status) {
                let data = res.data;
                data.forEach(message => {
                    addOneMessage(message);
                })
                socketConnect(objId);
            }
        }
    })

}

function formatDate(date) {
    let year = date.getFullYear();
    let month = ("0" + (date.getMonth() + 1)).slice(-2);
    let day = ("0" + date.getDate()).slice(-2);
    let hours = ("0" + date.getHours()).slice(-2);
    let minutes = ("0" + date.getMinutes()).slice(-2);
    let seconds = ("0" + date.getSeconds()).slice(-2);

    return hours + ":" + minutes + ":" + seconds + " " + month + "-" + day + "-" + year;
}

function addOneMessage(message) {
    const newMessage = $('<div>').addClass('message user-message');
    const avatar = $('<div>').addClass('avatar').append($('<span>').addClass('initial').text(message.sender[0]));
    const content = $('<div>').addClass('content');
    const userDetails = $('<div>').addClass('user-details');
    const name = $('<span>').addClass('name').text(message.sender);
    const time = $('<span>').addClass('time').text(formatDate(new Date(message.time)));
    const messageText = $('<p>').text(message.content);
    const hr = $('<hr>').addClass('message-divider');

    userDetails.append(name, time);
    content.append(userDetails, messageText);
    newMessage.append(avatar, content);

    $('#chat-messages').append(newMessage).append(hr);
}