/*==========================================================================		
				                MACHINE LEARNING
========================================================================== */

$(function(){
	// animate on scroll
	new WOW().init();
});


/*==========================================================================		
				                	MY WORK
========================================================================== */

$(function() {
 	 $('#work').magnificPopup({
	 	delegate: 'a', // child items selector, by clicking on it popup will open
	 	type: 'image',
	 	// other options
	 	gallery:{
	 		enabled:true
	 	}
  	});
});

/*==========================================================================		
				                	MY TEAM
========================================================================== */

$(function(){
	$("#team-members").owlCarousel({
		items:1,
		autoplay:true,
		center: true,
		loop: false,
		smartSpeed:700,
		autoplayHoverPause:true
	});
});

/*==========================================================================		
				                	MY RECOMMENDATION
========================================================================== */

$(function(){
	$("#my-recommendations").owlCarousel({
		items:1,
		autoplay:true,
		loop: true,
		smartSpeed:700,
		autoplayHoverPause:true
	});
});

/*==========================================================================		
				                	MY STATS
========================================================================== */

$(function(){
	$('.counter').counterUp({
	    delay: 10,
	    time: 2000
	});
});

/*==========================================================================		
				                CLIENTS
========================================================================== */

$(function(){
	$(".clients").owlCarousel({
		items:6,
		autoplay:true,
		loop: true,
		smartSpeed:700,
		autoplayHoverPause:true,
		responsive: {
			// breakpoint from 0 up
			0 : {
				items:1
			},
			// breakpoint from 480 up
			480 : {
				items: 3
			},
			// breakpoint from 768 up
			768 : {
				items: 5
			},
			// breakpoint from 992 up
			992 : {
				items: 6
			}
		}
	});
});

/*==========================================================================		
				                NAVIGATION
========================================================================== */


$(function(){
	$(window).scroll(function(){
		if($(this).scrollTop() < 50){
			//hide nav
			$("#back-to-top").fadeOut();
		}
		else{
			$("#back-to-top").fadeIn();
		}
	});
});

//Smooth scrolling

$(function(){
	$("a.smooth-scrolling").click(function(event){

		event.preventDefault();

		//get return id like #about, #work etc
		var section = $(this).attr("href");

		$('html, body').animate({
			scrollTop: $(section).offset().top
		}, 1250, "easeInOutExpo");
	});
});


$(function(){
     $(window).resize(function(){
         if($(this).width() < 992){
			$(function(){
				$(".navbar-collapse ul li a").on("click touch",function(){
					$(".navbar-toggler").click();
				});
			});
         }
      })
      .resize();//trigger resize on page load
});