$(function() {

	// Start serial connection
	$.getJSON($SCRIPT_ROOT + '/_start_serial', {}, {});

	// Initialize the window
	var ScreenWidth = $(window).width();
	var ScreenHeight = $(window).height();
	var ScreenXPadding = 30;
	var XSpacing = 50;
	var YSpacing = 60;
	var ytop = 400;

	

	var RaceBusy = 0;
	// Keeps track of whether there is a race currently busy.
	var NextStart = 0;
	// Time of the next start

	// We are running a simulation here
	var boats = [];
	for (var i = 0; i < 6; i++) {
		var boat = {
			Name : "Laga " + i, // Name of the boat
			Type : "8+", // Type of the boat
			Speed : 0, // Velocity in s / 500m
			Stroke : 0, // Strokerate / min
			Long : 0, // Longitude
			Lat : 0, // Latitude
			Active : 0, // Rowing
			RacePos : 0, // Distance from start
			RealPos : 0, // Actual distance from start
			boatItem : undefined
		};
		boats.push(boat);
	}

	// Set two center boats to active
	boats[2].Active = 1;
	boats[3].Active = 1;

	StartLat = 51.988489;
	StartLong = 4.5565610;
	EndLat = 52.005489;
	EndLong = 4.5645610;

	// set right width for course
	$('#Content').css('width',10000+(ScreenWidth/2));

	// Draw the boats
	//var Boat = $('.Boat');
	y = ytop - 45;
	x = 40;

	for (var i = 0; i < 6; i++) {
		var lane = i + 1;
		boats[i].boatItem = $('#lane-' + lane).find('.boat');
		
		boats[i].boatItem.css('left', x);
		// hide unactive boats
		if (!boats[i].Active)
			boats[i].boatItem.hide();
		//y = y + YSpacing;
	}

	/*
	for (var i = 0; i < 6; i++) {
	boats[i].boatItem = Boat.clone();
	boats[i].boatItem.appendTo("#Content");
	boats[i].boatItem.css('top', y).css('left', x);
	if (!boats[i].Active)
	boats[i].boatItem.hide();
	y = y + YSpacing;
	}
	*/

	// Draw the Bouys
	var x = ScreenXPadding - XSpacing;
	y = ytop;
	var Bouy = $('.Bouy');

	for (var c = 1; c <= 145; c++) {
		//e = Bouy.clone().appendTo('.bouys');
		$("<span class='bouy'></span>").appendTo('.bouys');
	}
	/*$('.Bouy').each(function(e) {
	$(this).css('top', y).css('left', x);
	x = x + XSpacing;
	if (x > 10000) {
	y = y + YSpacing;
	x = ScreenXPadding;
	}
	});*/

	// Draw the distance blocks
	y = 5;
	x = 160;
	//Block = $('.DistanceBlock');
	for (var c = 1; c < 42; c++){
		$('<div class="DistanceBlock"><div>').appendTo('#DistanceBlockContainer');
	}
		
	$('.DistanceBlock').each(function(e) {
		$(this).css('margin-left', x);
		$(this).html('<p>'+ (2000 - 50 * e) + '</p>');
		//x = x + 250;
	});

	// Start the simulation
	var d = new Date();
	var StartTime = d.getTime() + 6000;
	// We start in 6 seconds;
	var _state = 0;
	// State of the screen
	var _moves = 0;
	// Saves whether the boats or the screen movess
	var firstBoat = 0;

	// Main function which runs every 1000 millis
	//window.setInterval(startUp, 1000);
	
	// start race when spacebar is pressed 
	$(window).keyup(function(e) {
	    if ( e.keyCode == 32 ) {
			window.setInterval(startUp, 1000);
	    }
	});
	
	function startUp(){
			var d = new Date();
			switch (_state) {
				case 0: // Nothing is happening
					// Check if the match is about to start
					StartupScreen();
					break;
				case 1: // units are racing
					// Get boat info. For the simulation change the speed;
					var firstBoat_T = 0;
					var MaxLeft_T   = 0;
					for (var i = 0; i < 6; i++) {
						if (boats[i].Active) {
							boats[i].Speed = 40 + 2 * Math.sin(d.getTime()) + i * 2;
							// Animate to new position
							// Every meter is 5 pixels
							boats[i].RealPos += 500 / boats[i].Speed;
							var NewLeft = 40 + boats[i].RealPos * 5;
							if( NewLeft < 10000 ){
								boats[i].boatItem.animate({left: NewLeft}, 1000, "linear");
							}
							
							
							var leftPos = boats[i].boatItem.css('left');
							leftPos = leftPos.replace('px', '');
							if (parseInt(leftPos, 10) > MaxLeft_T) {
								MaxLeft_T = parseInt(leftPos, 10);
								firstBoat_T = i;
							}
						}
					}
					firstBoat = firstBoat_T;
					break;
				case 2: // units are finished
			
					break;
			}
	}


	// Screen refresh function - 50Hz
	window.setInterval(function() {
		MaxLeft = boats[firstBoat].boatItem.css('left');
		MaxLeft = parseInt(MaxLeft.replace('px', ''), 10);
		if (MaxLeft > ( ScreenWidth / 2 ) ) {
			var ContentLeft = -MaxLeft + ( ScreenWidth / 2 ) ;
			var contentPosition = parseInt($('#Content').css('left')) - ScreenWidth;
			
			if( contentPosition < 10000 ){
				$('#Content').css({
					'left' : ContentLeft + 'px'
				});
			}
		}
	}, 20);

	var starting = true;
	function StartupScreen() {
		console.log(starting);
		var d = new Date();
		if (StartTime - d.getTime() < 4000 && starting) {
			starting = false;
			$('#Message').html("Attention");
			$('#Message').show();
			setTimeout(function() {
				$('#Message').html("Set");
			}, 2000);
			setTimeout(function() {
				$('#Message').html("GO!!!!");
			}, 4000);
			setTimeout(function() {
				$('#Message').hide();
				_state = 1;
			}, 4500);
		}
	}

	/*
	 function Competition() {
	 while (1) {
	 if (!RaceStatus) {
	 // As there is no race busy right now, we are going to request the next time start
	 $.getJSON($SCRIPT_ROOT + '/_get_race_status', {}, function(data) {

	 });
	 }
	 }
	 }
	 */

	// MoveScreen is not being used
	/*
	function MoveScreen(Speed) {
		$('#Content').animate({
			left : "-=100"
		}, Speed, function() {
			MoveScreen(Speed);
		});
	};
	*/
	//MoveScreen(100);

	/*window.setInterval(function() {

	 $.getJSON($SCRIPT_ROOT + '/_return_serial', {}, function(data) {
	 res = data.result.replace(new RegExp('_', 'g'), '<br />');
	 $('#Content').html(res);
	 console.log(data.result);
	 });
	 }, 1000);*/
}); 