function SetRelay(obj) {
  obj_jq = $(obj);
  relay_url = '/relay/'+obj_jq.val()
	$.ajax({
	  url: relay_url,
	  async: true,
	  type: "GET",
		success: function (json) {
			var onoff = json.state	
			var startdt = json.last_start_dt
            var stopdt = json.last_stop_dt
			var rundur = json.last_run_duration			
			if (onoff == 0) {
				obj_jq.prop('checked', false)
				$(obj+'_start').html(startdt);
				$(obj+'_stop').html(stopdt);
				$(obj+'_duration').html(rundur);
			}
			else if (onoff == 1) {
				obj_jq.prop('checked')
				$(obj+'_start').html(startdt);
				$(obj+'_stop').html(stopdt);
				$(obj+'_duration').html(rundur);
			}
			
			
		},
	error: function (){
	  console.log('Error encountered');
	  }
	})
}

$('#relay-8').change(function () {
	SetRelay('#relay-8');
	}
)
$('#relay-7').change(function () {
	SetRelay('#relay-7');
	}
)
$('#relay-6').change(function () {
	SetRelay('#relay-6');
	}
)
$('#relay-5').change(function () {
	SetRelay('#relay-5');
	}
)
$('#relay-4').change(function () {
	SetRelay('#relay-4');
	}
)
$('#relay-3').change(function () {
	SetRelay('#relay-3');
	}
)
$('#relay-2').change(function () {
	SetRelay('#relay-2');
	}
)
$('#relay-1').change(function () {
	SetRelay('#relay-1');
	}
)

