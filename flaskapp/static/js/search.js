$(".video-link").click(function(){
	data = {
		"clicked_video" : $(this).attr("name"),
		"query"	: query
	};
	$.post(url = "/log/search", data = data);
});
