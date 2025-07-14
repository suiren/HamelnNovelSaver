// 白背景・黒背景切り替え
$(function() {
	if (typeof localStorage !== 'undefined') {
		try {
			var stateNightmode = localStorage.getItem('NIGHT_MODE');
			
			if (stateNightmode == 1) {
			    $("#nightmode_check").prop("checked", true);
			}
		} catch(e) {
			$("label.toggle_lbl").hide();
			$("#nightmode_check").after("設定不可");
		}
	}
	
	$('#nightmode_check').click(function(){
		try {
			var state = localStorage.getItem('NIGHT_MODE');
			if (state == 1) {
				localStorage.setItem('NIGHT_MODE', 2);
				$("body").removeClass("night");
			} else {
				localStorage.setItem('NIGHT_MODE', 1);
				$("body").addClass("night");
			} 
		}catch(e) {
		}
	});
});
