	function pad(number, digits) {
		beforeDecimalLength = number.toString().split('.')[0].length;
		return Array(Math.max(digits - beforeDecimalLength + 1, 0)).join(0) + number;
	}

	function getJSON(url, callback) {
		var xhr = new XMLHttpRequest();
			xhr.open('GET', url, true);
			xhr.responseType = 'json';
			xhr.onload = function() {
				var status = xhr.status;
				if (status === 200) {
					callback(null, xhr.response);
				} else {
					callback(status, xhr.response);
				}
			};
		xhr.send();
	};    



	function degreesToSexagesimal(raDeg, decDeg) {
		ra = raDeg/15;
		hours = Math.floor(ra);
		minutes = (ra - Math.floor(ra)) * 60;
		seconds = (minutes - Math.floor(minutes)) * 60;
		minutes = Math.floor(minutes);
		seconds = Math.round(seconds*100) / 100;
					
		dec = decDeg;
		decDegrees = Math.floor(dec);
		if (dec>0) decSign = "+";
		else decSign = "-";
		dec = Math.abs(dec);
		decMinutes = (dec - Math.floor(dec)) * 60;
		dec = Math.floor(dec);
		decSeconds = (decMinutes - Math.floor(decMinutes)) * 60;
		decMinutes = Math.floor(decMinutes);
		
		decSeconds = Math.round(decSeconds*100) / 100;
		var sexString = "";
		sexString+= pad(hours, 2) + ":" + pad(minutes,2) + ":" + pad(seconds, 2); 
		sexString+= " " + decSign +  pad(dec,2) + ":" + pad(decMinutes,2) + ":" + pad(decSeconds,2);
		
		return sexString;

	}


	function wcsSolution() {
		this.equinox = 0;	
	}

	wcsSolution.prototype.init = function(data){
		this.equinox = data.equinox;
		this.x_ref = data.x_ref;
		this.y_ref = data.y_ref;
		this.ra = data.ra;
		this.dec = data.dec;
		this.CD_1_1 = data.CD_1_1;
		this.CD_1_2 = data.CD_1_2;
		this.CD_2_1 = data.CD_2_1;
		this.CD_2_2 = data.CD_2_2;
	}

	wcsSolution.prototype.toString = function(){
		outStr = "WCS solution centred at RA: " + this.ra + " DEC: " + this.dec;
		return outStr;
	}
	
	wcsSolution.prototype.pixelToWorld = function(x, y) {
		abs_x = x - this.x_ref + 1;
		abs_y = y - this.y_ref + 1;
		world_x = this.CD_1_1 * abs_x + this.CD_1_2 * abs_y;
		world_y = this.CD_2_1 * abs_x + this.CD_2_2 * abs_y;
		
		// Deal with the tangent plane projection
		world_x = world_x / Math.cos(this.dec/180*Math.PI);
		world_x = world_x + this.ra;
		world_y = world_y + this.dec;
		
		worldCoord = {wx: world_x, wy: world_y}
		
		return worldCoord;
	}

	wcsSolution.prototype.worldToPixel = function(r, d) {
		r = r - this.ra;
		d = d - this.dec;
		r = r * Math.cos(this.dec/180*Math.PI);
		var determinant = this.CD_1_1 * this.CD_2_2 - this.CD_1_2 * this.CD_2_1;
		var CD_inv_1_1 =  this.CD_2_2 / determinant;
		var CD_inv_1_2 = -1.0 * this.CD_1_2 / determinant;
		var CD_inv_2_1 = -1.0 * this.CD_2_1 / determinant;
		var CD_inv_2_2 =  this.CD_1_1 / determinant;

		var x = CD_inv_1_1 * r + CD_inv_1_2 * d;
		var y = CD_inv_2_1 * r + CD_inv_2_2 * d;
		
		// Deal with the tangent plane projection
		//world_x = world_x / Math.cos(this.dec/180*Math.PI);
		x = x + this.x_ref - 1;
		y = y + this.y_ref - 1;
		
		var pixel = {x: x, y: y}
		
		return pixel;
	}


	wcsSolution.prototype.calc_xy_rotation_and_scale = function() {
        var determinant = this.CD_1_1 * this.CD_2_2 - this.CD_1_2 * this.CD_2_1;
		var sgn;
		if (determinant < 0) sgn = -1
        else sgn = 1
        
        if ((this.CD_2_1 == 0.0) || (this.CD_1_2 == 0.0)) {
            // Unrotated coordinates?
            this.xrot = 0.0
            this.yrot = 0.0
            this.cdelt1 = this.CD_1_1
			this.cdelt2 = this.CD_2_2
		} else {
            this.xrot = Math.atan2(sgn * this.CD_1_2, sgn * this.CD_1_1)
            this.yrot = Math.atan2(-this.CD_2_1, this.CD_2_2)

            this.cdelt1 = sgn * Math.sqrt(this.CD_1_1**2 + this.CD_1_2**2)
            this.cdelt2 = Math.sqrt(this.CD_1_1*this.CD_1_1 + this.CD_2_1*this.CD_2_1)
		}
	 }

    