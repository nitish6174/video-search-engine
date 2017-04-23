$(document).ready(function(){
    

    /* Toggle description */
    $("#descriptionToggle").click(function(){
        if($(this).hasClass('active'))
        {
            $(this).removeClass('active');
            $("#description").css("height","100%");
            $("#descriptionOverlay").hide();
            $("#expandDescriptionMsg").hide();
            $("#collapseDescriptionMsg").show();
        }
        else
        {
            $(this).addClass('active');
            $("#description").css("height","100px");
            $("#descriptionOverlay").show();
            $("#expandDescriptionMsg").show();
            $("#collapseDescriptionMsg").hide();
        }
    });


    /* Check interaction */
    $.post("/check-interaction/like",{
        videoId: currentVideo
    }, function(data, status){
        if(data["success"]==1 && data["val"]==1)
        {
            $("#likeVideo").addClass('active');
        }
    });
    $.post("/check-interaction/dislike",{
        videoId: currentVideo
    }, function(data, status){
        if(data["success"]==1 && data["val"]==1)
        {
            $("#dislikeVideo").addClass('active');
        }
    });
    $.post("/check-interaction/subscribe",{
        channelId: channelId
    }, function(data, status){
        if(data["success"]==1 && data["val"]==1)
        {
            $("#subscribeBtn").html("Unsubscribe");
            $("#subscribeBtn").removeClass("btn-primary");
            $("#subscribeBtn").addClass("btn-default");
        }
    });


    /* Like button */
    $("#likeVideo").click(function(){
        var elem = $(this);
        if($(elem).hasClass("active"))
        {
            $.post("/clear-like",{
                videoId: currentVideo
            }, function(data, status){
                $(elem).removeClass("active");
            });
        }
        else
        {
            $.post("/like-video",{
                videoId: currentVideo
            }, function(data, status){
                $(elem).addClass("active");
                $("#dislikeVideo").removeClass("active");
            });
        }
    });


    /* Dislike button */
    $("#dislikeVideo").click(function(){
        var elem = $(this);
        if($(elem).hasClass("active"))
        {
            $.post("/clear-like",{
                videoId: currentVideo
            }, function(data, status){
                $(elem).removeClass("active");
            });
        }
        else
        {
            $.post("/dislike-video",{
                videoId: currentVideo
            }, function(data, status){
                $(elem).addClass("active");
                $("#likeVideo").removeClass("active");
            });
        }
    });


    /* Subscribe button */
    $("#subscribeBtn").click(function(){
        var elem = $(this);
        if($(elem).hasClass("active"))
        {
            $.post("/unsubscribe-channel",{
                channelId: channelId
            }, function(data, status){
                $(elem).removeClass("active");
                $(elem).html("Subscribe");
                $(elem).removeClass("btn-default");
                $(elem).addClass("btn-primary");
            });
        }
        else
        {
            $.post("/subscribe-channel",{
                channelId: channelId
            }, function(data, status){
                $(elem).addClass("active");
                $(elem).html("Unsubscribe");
                $(elem).removeClass("btn-primary");
                $(elem).addClass("btn-default");
            });
        }
    });


    /* Watch later button */
    $("#watchLater").click(function(){
        var elem = $(this);
        if($(elem).hasClass("active"))
        {
            $.post("/remove-watch-later",{
                doc_id: doc_id
            }, function(data, status){
                $(elem).removeClass("active");
                $("i", $(elem)).attr("title", "Add to watch later");
            });
        }
        else
        {
            $.post("/add-watch-later",{
                doc_id: doc_id
            }, function(data, status){
                $(elem).addClass("active");
                $("i", $(elem)).attr("title", "Remove from watch later");
            });
        }
    });


    /* Add log of clicked related video */
    $(".related-video").click(function(){
        data = {
            "clicked_video" : $(this).attr("name"),
            "current_video" : currentVideo
        };
        $.post(url = "/log/video", data = data);
    });
    
    
});
