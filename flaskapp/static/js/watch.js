$(".relvid").click(function(){
	data = {
		"clicked_video" : $(this).attr("name"),
		"current_video"	: currentVideo
	};
	$.post(url = "/log/video", data = data);
});

