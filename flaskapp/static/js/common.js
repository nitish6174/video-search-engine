$("#searchForm").submit(function(e){
    e.preventDefault();
    searchInput();
    return false;
});

function searchInput()
{
    val = $("#searchInput").val();
    console.log(val);
    window.location.href = "/search/"+val;
}
