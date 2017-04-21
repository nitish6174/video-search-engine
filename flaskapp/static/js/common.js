/* Search bar */

$("#searchForm").submit(function(e){
    e.preventDefault();
    searchInput();
    return false;
});

$("#searchSubmit").click(function() {
    searchInput();
});

function searchInput()
{
    val = $("#searchInput").val();
    console.log(val);
    window.location.href = "/search/"+val;
}


/* Tabbed content */

$(".tab").click(function(){
    if(!$(this).hasClass('active'))
    {
        var group = $(this).attr("data-tab-group");
        $(".tab[data-tab-group='"+group+"']").removeClass('active');
        $(this).addClass('active');
        $(".tab-content[data-tab-group='"+group+"']").hide();
        target_id = $(this).attr("data-target");
        document.getElementById(target_id).style.display = 'block';
    }
});

$(document).ready(function(){
    $(".tab.active").each(function(){
        target_id = $(this).attr("data-target");
        document.getElementById(target_id).style.display = 'block';
    });
});
