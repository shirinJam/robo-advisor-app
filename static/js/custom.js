// ###################################################################################
//                           FIRST PAGE & SECOND PAGE
// ###################################################################################

// Example starter JavaScript for disabling form submissions if there are invalid fields
$(function () {
    $('form#question_form').on('submit',function(event){
        //Make groups
        console.log($('input:radio'));
        if ($('input:radio').length != 0) {
            var names = []
            $('input:radio').each(function () {
                var rname = $(this).attr('name');
                if ($.inArray(rname, names) == -1) names.push(rname);
            });

            $.each(names, function (i, name) {
                if ($('input[name="' + name + '"]:checked').length == 0) {
                    console.log('Please check ' + name);
                    $('#valid_'+name).text('Please select one of the above option');
                    document.getElementById("warning").style.display= 'block';
                    event.preventDefault();
                }
                else{
                    window.onbeforeunload = false;
                    $('#valid_'+name).text('');
                }
            });
        }
        else{
            window.onbeforeunload = false;
        }
    });
});

// ###################################################################################
//                                     CONTACT PAGE
// ###################################################################################

$(function () {
    $("#contact_us").on("click",function(event){
         window.onbeforeunload = false;
    });
});


$(function () {
    $("#validate").on("click",function(event){

        function validateEmail(email) {
            const re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
            return re.test(email);
        }
        
        const email = $("#email").val();
        console.log(email.length);
        if ((validateEmail(email)) && (email.length > 0)) {
            $('#valid_email').text('');
            window.onbeforeunload = false;
        } 
        else {
        $('#valid_email').text(email + ' is not valid email id!');
        event.preventDefault();
        }
    });
});



// ###################################################################################
//                                     FIRST PAGE
// ###################################################################################

// Animation on the first page for the requirements questions
$(document).ready(function() {   
    $('#converter-do').hide();
    $('#requirements').hide();
    $('#questionA').on('click', function (e) {
        e.preventDefault();
        if ($('#requirements').is(':visible')) { 
              $('#requirements').slideToggle('slow');
        }
        $('#converter-do').slideToggle('slow');
    });
    $('#questionB').on('click', function (e) {
        e.preventDefault();
        if ($('#converter-do').is(':visible')) { 
              $('#converter-do').slideToggle('slow');
        }
        $('#requirements').slideToggle('slow');
    });
})


// ###################################################################################
//                                     Slider
// ###################################################################################

// For slider1 for Net Worth
const slider = document.getElementById('sliderPrice1');
// const slider = document.getElementById('sliderPrice2');
const rangeMin = parseInt(slider.dataset.min);
const rangeMax = parseInt(slider.dataset.max);
const step = parseInt(slider.dataset.step);
const filterInputs = document.querySelectorAll('input.filter__input');

noUiSlider.create(slider, {
    start: [rangeMin, rangeMax],
    connect: true,
    step: step,
    range: {
        'min': rangeMin,
        'max': rangeMax
    },
  
    // make numbers whole
    format: {
      to: value => Math.trunc(value),
      from: value => Math.trunc(value)
    }
});

// bind inputs with noUiSlider 
slider.noUiSlider.on('update', (values, handle) => { 
  filterInputs[handle].value = values[handle]; 
});

filterInputs.forEach((input, indexInput) => { 
  input.addEventListener('change', () => {
    slider.noUiSlider.setHandle(indexInput, input.value);
  })
});


// For slider2 for salary
const slider2 = document.getElementById('sliderPrice2');
const rangeMin2 = parseInt(slider2.dataset.min);
const rangeMax2 = parseInt(slider2.dataset.max);
const step2 = parseInt(slider2.dataset.step);
const filterInputs2 = document.querySelectorAll('input.filter__input.slider2');

noUiSlider.create(slider2, {
    start: [rangeMin2, rangeMax2],
    connect: true,
    step: step2,
    range: {
        'min': rangeMin2,
        'max': rangeMax2
    },
  
    // make numbers whole
    format: {
      to: value => Math.trunc(value),
      from: value => Math.trunc(value)
    }
});

// bind inputs with noUiSlider 
slider2.noUiSlider.on('update', (values, handle) => { 
  filterInputs2[handle].value = values[handle]; 
});

filterInputs2.forEach((input, indexInput) => { 
  input.addEventListener('change', () => {
    slider.noUiSlider.setHandle(indexInput, input.value);
  })
});

// ###################################################################################
//                                 Currency Converter
// ###################################################################################


// for currency converter
const currencies = ["EUR", "USD", "INR", "GBP"]

const fromSelectEl = document.querySelector('#from')
const toSelectEl = document.querySelector('#to')
const formEl = document.querySelector('form.currency_converter')
const resultEl = document.querySelector('#result')
const symbolEl = document.querySelector('#symbol')

const renderOptions = (options) => {
    options.sort().forEach(curr => {
        const newOption = document.createElement('option')
        newOption.setAttribute('value', curr)
        newOption.textContent = curr
        const clonedOption = newOption.cloneNode(true)
        if(curr === 'EUR') {
            newOption.selected = true
        }
        if(curr === 'USD') {
            clonedOption.selected = true
        }
        fromSelectEl.appendChild(newOption)
        toSelectEl.appendChild(clonedOption)
    })
}

const submitHandler = (e) => {
    e.preventDefault()

    const [amountVal, fromVal, toVal] = [...e.target.elements].map(el => el.value)
    
    if(amountVal === '') {
        return alert('Please insert amount')
    }

    if(fromVal === toVal) {
        return alert('Fun Fact: 1 amount X equals to 1 amount X')
    }    

    makeHttpRequest(`https://api.exchangeratesapi.io/latest?base=${fromVal}&symbols=${toVal}`, (response) => {
        const dataToShow = response.rates[toVal] * amountVal
        resultEl.textContent = dataToShow.toFixed(3)
        symbolEl.value = toVal
    })
}

const makeHttpRequest = (url, callback) => {
    const xhr = new XMLHttpRequest()
    xhr.onload = (res) => {
        if(xhr.status === 200) {
            return callback(JSON.parse(res.target.responseText))            
        } else {
            alert('Probably a server error')
        }        
    }

    xhr.open('GET', url)
    xhr.send()
}

renderOptions(currencies)
formEl.addEventListener('submit', submitHandler)