var sounds = {}

function play(id) {
	// Make sure the id is a key that is present in the dict and make sure
	// the dict object has the audio file in it
	if (id in sounds) {
		if (!sounds[id].audio) {
			load_clip(id);
		}
		sounds[id].audio.play();
		sounds[id].audio.currentTime = 0;
	}
	else {
		console.log('Invalid clip id: ' + String(id));
	}
}

function load_clip(id) {
	if (id in sounds) {
		console.log('loading clip ' + String(id) + ' at ' + sounds[id].url)
		sounds[id].audio = new Audio(sounds[id].url);
	}
}

function update_dom() {
	button_list = document.getElementById("button_list");
	button_list.innerHTML = ''; // http://stackoverflow.com/questions/3955229/remove-all-child-elements-of-a-dom-node-in-javascript
	for (var key in sounds) {
		if (sounds.hasOwnProperty(key)) {
			// Create the buttons label
			var name = document.createElement("b");
			name.innerHTML = sounds[key].name;
			// Create the buttons icon
			var icon = document.createElement("span");
			icon.className = "glyphicon glyphicon-play"
			// Define the button itself
			var btn = document.createElement("div");
			btn.className = 'clipbutton';
			btn.setAttribute('onclick', 'play(' + String(key) + ');');
			btn.appendChild(name);
			btn.appendChild(icon);
			// Now add the new button to the div
			button_list.appendChild(btn);
		}
	}
}
