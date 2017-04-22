/* Redirect to search page on submitting search input */

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


/* Call suggest() on typing */

$('#searchInput').keyup(function(e){
    if( (e.which>=32 && e.which<=122) || e.which==8 || e.which==127 )
        suggest();
    else if( e.which==27 )
    {
        $('#searchInput').blur();
        $('#searchSuggestions').hide();
    }
});


/* Click event handler for suggestion item */

$('#searchSuggestions').on("mousedown",'.suggestion-item',function(e){
    e.preventDefault();
}).on('click', '.suggestion-item', function() {
    text = $('.suggestion-text',this).html();
    $('#searchInput').val(text);
    $('#searchSuggestions').hide();
    searchInput();
});


/* Call suggest API */

function suggest()
{
    val = $('#searchInput').val();
    if(val!="")
    {
        $.post("/suggest",{
            input_query: val,
        },function(data,status){
            $('#searchSuggestions').html('');
            $('#searchSuggestions').show();
            video_suggestions = data["video_suggestions"];
            channel_suggestions = data["channel_suggestions"];
            displaySuggestions(video_suggestions, channel_suggestions);
        });
    }
    else
        $('#searchSuggestions').html('');
}


/* Display suggestion results */

function displaySuggestions(video_suggestions, channel_suggestions)
{
    for(var i=0;i<video_suggestions.length;i++)
        $('#searchSuggestions').append(suggestionContent(i, video_suggestions[i], ""));
    for(var i=0;i<channel_suggestions.length;i++)
        $('#searchSuggestions').append(suggestionContent(i, channel_suggestions[i], "Channel"));
}

function suggestionContent(index, value, type)
{
    s = '<li class="suggestion-item">';
    s += '<span class="text-muted right">'+type+'</span>';
    s += '<span class="suggestion-text">'+value+'</span>';
    s += '</li>';
    return s;
}
