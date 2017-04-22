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


    /* Add log of clicked related video */
    $(".related-video").click(function(){
        data = {
            "clicked_video" : $(this).attr("name"),
            "current_video" : currentVideo
        };
        $.post(url = "/log/video", data = data);
    });
    
    
});
