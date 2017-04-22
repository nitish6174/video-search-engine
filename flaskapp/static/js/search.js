$(document).ready(function(){


    /* Add log of clicked related video */
    $(".video-link").click(function(){
        data = {
            "clicked_video" : $(this).attr("name"),
            "search_query"  : query
        };
        $.post(url = "/log/search", data = data);
    });


});
