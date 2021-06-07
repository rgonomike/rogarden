
function getSensor(sensor_type) {
  if (sensor_type == 'temp') {  
  temp_url = '/temp_sensor/15'
  $.ajax({
      url: temp_url,
      async: true,
      type: "GET",
      success: function (json) {
		$('#T1').html(json.fa+json.temperature)
		$('#H1').html('<i class="fa fa-tint" aria-hidden="true" style="color:deepskyblue"></i> '+json.humidity)
      },
      error: function (){
          console.log('Error encountered');
	  }
      })
  } else if (sensor_type == 'moist') {
	moist_url = '/moisture_sensor/12'
	$.ajax({
      url: moist_url,
      async: true,
      type: "GET",
      success: function (json) {
		if (json == 0) {  
			$('#M1').html('<i class="fa fa-bath" aria-hidden="true" style="color:deepskyblue"></i> Wet')
		} else {
			$('#M1').html('<i class="fa fa-fire" aria-hidden="true" style="color:orange"></i> Dry')
		}
      },
      error: function (){
          console.log('Error encountered');
	  }
      })  
  }
}

setInterval(function(){ 
	getSensor('temp'); 
	getSensor('moist');
	}
, 1000*10);

window.onload = function() {
  getSensor('temp');
  getSensor('moist');
};