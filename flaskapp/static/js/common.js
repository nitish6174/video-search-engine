$(document).ready(function(){


    /* Show content corresponding to active tab */
    $(".tab.active").each(function(){
        target_id = $(this).attr("data-target");
        document.getElementById(target_id).style.display = 'block';
    });


    /* Toggle visible content on tab click */
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


    /* Add commas in number displays */
    $(".comma").each(function(){
        text = $(this).html();
        $(this).html(indian_format(text));
    });


});

function international_format(x) {
    return x.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function indian_format(x) {
    return x.replace(/(\d)(?=(\d\d)+\d$)/g, "$1,");
}
