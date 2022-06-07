/*

    This file is part of OpenWebRX, it provides a spectrum display and is
    based on code provided by Ubermood (https://groups.io/g/openwebrx/topic/88626097)

	Copyright (c) 2022 eroyee (https://github.com/eroyee/)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

NOTE: This is a crude way of providing spectral data, it is expensive on CPU and should be (vastly!) improved.

*/

    function qs(q) { return document.querySelector(q); }
    var freqSpectrumCtx;
    var freqSpectrumGradient; 
    var is_on;
    var fft_size=qs("#webrx-canvas-container").lastElementChild.width; // get fft_size from waterfall setting to use with the spectrum canvas width (otherwise need to manually set width to 4096/8192/16384)
    function display_spectra () {
    if (!is_on) {
    // Create a new DIV for spectrum analyzer canvas (in header.include.html)
        var divFreqSpectrum = '<div id="freq-div-spectrum">'
                            + '<canvas id="freq-canvas-spectrum" width="'+(fft_size)+'" height="256" style="width:100%;height:256px;left:0px;position:absolute;bottom:0px;">'
                            + '</div>';

        //eroyee below to drop down spectrum container
        document.getElementById('spectrum_container').style.height = "130px";
        document.getElementById('spectrum_container').style.opacity = "1";
        var div = qs(".openwebrx-spectrum-container");
        div.insertAdjacentHTML('beforeEnd', divFreqSpectrum);
     
    // Canvas context for spectrum analyzer
    // var freqSpectrumCtx;
        freqSpectrumCtx        = qs("#freq-canvas-spectrum").getContext('2d');
        freqSpectrumCtx.width  = (fft_size);
        freqSpectrumCtx.height = 255
     
    // Gradient color scheme for spectrum, these are probably weird colours but I have an excuse! You can change to something better...
        freqSpectrumGradient = freqSpectrumCtx.createLinearGradient(0, 0, 0, 255);
        freqSpectrumGradient.addColorStop(1.00, 'blue');
        freqSpectrumGradient.addColorStop(0.75, 'green');
        freqSpectrumGradient.addColorStop(0.50, 'red');
        freqSpectrumGradient.addColorStop(0.25, 'orange');
        freqSpectrumGradient.addColorStop(0.00, 'yellow');		   
    // Update spectrum analyzer
	setInterval(function() {
            freqSpectrumDraw(getFreqData());
        }, 25) 	
    // Observe zooming of waterfall and copy zoom-width to spectrum also
        var observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutationRecord) {
                qs("#freq-canvas-spectrum").style.left  = qs("#webrx-canvas-container").style.left
                qs("#freq-canvas-spectrum").style.width = qs("#webrx-canvas-container").style.width
            });    
        });
        observer.observe(qs("#webrx-canvas-container"), { attributes : true, attributeFilter : ['style'] });
	    is_on=true;	   
	    }
    // eroyee below to flush display & return up
    else{
        is_on=false;
        document.getElementById('spectrum_container').style.height = "0px";
        document.getElementById('spectrum_container').style.opacity = "0";
        const flush = qs("#freq-canvas-spectrum");
        flush.parentNode.removeChild(flush);
        return;
	}
    // ----------------------------------------
    }	
    // Function to draw spectrum, and include 'd' equidistant lines
    function freqSpectrumDraw(freqData) {
        var y = 1;
	const d = (freqSpectrumCtx.height/6);    
        freqSpectrumCtx.fillStyle = "#000";
        freqSpectrumCtx.fillRect(0, 0, freqSpectrumCtx.width, freqSpectrumCtx.height);
        freqSpectrumCtx.fillStyle = freqSpectrumGradient;  
    // Draw spectrum
        for (var i = 0; i < freqSpectrumCtx.width; i++) {
		y = y+d; // lines
		freqSpectrumCtx.fillStyle = "#FFF"; // white, remove this for colour coded lines
		freqSpectrumCtx.fillRect(0, y, freqSpectrumCtx.width, 0.5);  // draw lines
                freqSpectrumCtx.fillStyle = freqSpectrumGradient; // remove if colour coded lines req'd
		freqSpectrumCtx.fillRect(i, freqSpectrumCtx.height, 1, -freqData[i]);  // draw spectra
        }
    }
     
    // Function to get data for spectrum, by grabbing the first row from waterfall canvas
    function getFreqData() {
    // Get waterfall canvas
        var theCanvas  = qs("#webrx-canvas-container").lastElementChild;
    // Get canvas Y position
        var theCanvasY = Math.abs(new WebKitCSSMatrix(window.getComputedStyle(theCanvas).webkitTransform).m42);
    // Grab single row of data from that Y position
        var theCanvasData = theCanvas.getContext('2d').getImageData(1, theCanvasY - 1, theCanvas.width, 1).data;   
    // Convert row of pixels to spectrum analyser data
        var data = [];
        var x = 0;
        for (var i = 0; i < theCanvasData.length; i += 4) {
    // RGB data to Grayscale
                var avg = (theCanvasData[i] + theCanvasData[i + 2] + theCanvasData[i + 1]) / 3;  // mess with these numbers to get desired output
                data[x++] = parseInt(avg) - 38;  // subtract number to lower floor hard level
        }
        return data;
    }
     
   
    
