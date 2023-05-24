$(function () {
    bindBtnSendApp();
    bindBtnGetApp();
    bindBtnAccept();
    bindBtnReject();
})

function bindBtnSendApp() {
    $("#sendApp").click(function () {
        const csrftoken = $.cookie('csrftoken');
        let err = $("#error-msg");
        err.hide();
        $.ajax({
            url: "/key/createApp/",
            type: "post",
            data: $("#applicationForm").serialize(),
            headers: {'X-CSRFtoken': csrftoken},
            dataType: "JSON",
            success: function (res) {
                console.log(res);
                if (res.status) {
                    alert("申请成功");
                    $("#applicationForm")[0].reset();
                    $("#createNewKey").modal('hide');

                } else {
                    err.text(res.msg);
                    err.show();
                }
            }
        });
    })
}

function bindBtnGetApp() {
    $("#getApp").click(function () {
        $.ajax({
            url: "/key/getApp/",
            type: "GET",
            success: function (res) {
                console.log(res);
                if (res.status) {
                    // 清空 tbody 内容
                    $("#myTableBody").empty();
                    let data = res.data;
                    // 遍历数据并渲染每个元素
                    data.forEach(function (data) {
                        // 创建元素
                        var cardDiv = $('<div>').addClass('card').css({
                            width: '25rem',
                            marginLeft: 'auto',
                            marginTop: '10px',
                            marginRight: 'auto',
                        });
                        var cardBodyDiv = $('<div>').addClass('card-body');
                        var cardTitle = $('<h5>').addClass('card-title').text(data.username);
                        var cardText = $('<p>').addClass('card-text').text(data.remark);
                        var acceptBtn = $('<button>').addClass('btn btn-primary acceptBtn').attr('type', 'button').text('接受');
                        var rejectBtn = $('<button>').addClass('btn btn-secondary rejectBtn').attr('type', 'button').text('拒绝').css('marginLeft', '5px')

                        // 将元素组装起来
                        cardBodyDiv.append(cardTitle, cardText, acceptBtn, rejectBtn);
                        cardDiv.append(cardBodyDiv);
                        var tableRow = $('<tr>').append(cardDiv);

                        // 添加到 tbody 中
                        $('#myTableBody').append(tableRow);
                    });
                }
            }
        });
    })
}

function bindBtnAccept() {
    $("#myTableBody").on('click', '.acceptBtn', function () {
        let tableRow = $(this).closest('tr');
        let userName = tableRow.find('h5').text();
        $.ajax({
            url: "/key/acceptApp/",
            type: "GET",
            data: {'username': userName},
            success: function (res) {
                if (res.status) {
                    alert("接受成功");
                    $("#checkNewKeyApplication").modal('hide');
                    location.reload();
                }
            }
        });
    })
}

function bindBtnReject() {
    $("#myTableBody").on('click', '.rejectBtn', function () {
        let tableRow = $(this).closest('tr');
        let userName = tableRow.find('h5').text();
        $.ajax({
            url: "/key/rejectApp/",
            type: "GET",
            data: {'username': userName},
            success: function (res) {
                if (res.status) {
                    alert("拒绝成功");
                    $("#checkNewKeyApplication").modal('hide');
                }
            }
        })
        ;
    })

}