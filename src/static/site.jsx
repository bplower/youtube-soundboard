

class ClipButton extends React.Component {
  constructor(props) {
    super(props);
    this.state = {clip_name: ''}
    this.submitDelete = this.submitDelete.bind(this);
  }

  submitDelete() {
    var self = this;
    var xhttp = new XMLHttpRequest();
    xhttp.open("DELETE", "/api/clips/"+this.props.pkid);
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 204) {
        self.props.onDelete()
      }
    };
    xhttp.send();
  }

  render() {
    return (
      <div className="card" style={{margin: "10px", width:"31%", display: "inline-block"}}>
        <div className="card-body">
          <h4 className="card-title">
            {this.props.name}
            <a className="btn btn-danger" style={{float: "right"}} role="button" onClick={this.submitDelete}>
              <span className="oi oi-trash" title="trash" aria-hidden="true"></span>
            </a>
          </h4>
          <p class="card-text">
          <a href={this.props.url}>Source video</a> ({this.props.start}s - {this.props.end}s)
          </p>
          <audio controls preload="none" style={{width: "100%"}}>
            <source src={"/audio/" + this.props.pkid + ".mp3"} type="audio/mp3" />
            Your browser does not support the audio element.
          </audio>
        </div>
      </div>
    );
  }
}

class ClipRange extends React.Component {
  constructor(props) {
    super(props);
    this.state = {clips: []}

    this.loadClips = this.loadClips.bind(this);

    this.loadClips()
  }

  loadClips() {
    var self = this;
    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", "/api/clips");
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
        let result = JSON.parse(this.responseText);
        let new_state = self.state
        new_state.clips = result
        self.setState(new_state);
      }
    };
    xhttp.send();
  }

  render() {
    return (
      <div className="row">
      {this.state.clips.map((obj, i) => 
        <ClipButton key={i} name={obj.name} pkid={obj.pkid} url={obj.url} start={obj.start} end={obj.end} source={obj.source} onDelete={this.loadClips} />
      )}
      </div>
    );
  }
}

class ClipCreateForm extends React.Component {
	constructor(props) {
		super(props);
		this.state = {
      name: '',
      url: '',
      start: null,
      end: null,
      error_display: "none",
      error_message: ''
    };

    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
	}

	handleChange(event) {
		let new_state = this.state;
		let field = event.target.dataset.field;
		new_state[field] = event.target.value;
		this.setState(new_state);
	}

	handleSubmit(event) {
    // Check if the URL is valid first
    if (!isURL(this.state.url)) {
      alert('bad url');
      return false;
    }

		var self = this;
		event.preventDefault();
		var xhttp = new XMLHttpRequest(); // new HttpRequest instance 
		xhttp.open("POST", "/api/clips");
		xhttp.setRequestHeader("Content-Type", "application/json");
		xhttp.onreadystatechange = function() {
			if (this.readyState == 4 && this.status == 200) {
				let result = JSON.parse(this.responseText);
				self.setState({result: result});
			} else if (this.readyState == 4 && this.status == 400) {
        let result = JSON.parse(this.responseText);
        console.log(result);
        self.state.error_display = "block";
        self.state.error_message = result.message;
      }
		};
		xhttp.send(JSON.stringify(self.state));
	}

	render() {
		return (
      <div>
  			<div className="modal-body">
  				<div>
  					<label className="control-label">Name</label>
  					<input type="text" data-field="name" className="form-control" onChange={this.handleChange} />
  				</div>
  				<div>
  					<label className="control-label">URL</label>
  					<input type="text" data-field="url" className="form-control" onChange={this.handleChange} />
  				</div>
  				<div>
  					<label className="control-label">Start</label>
  					<input type="number" data-field="start" className="form-control" onChange={this.handleChange} />
  				</div>
  				<div>
  					<label className="control-label">End</label>
  					<input type="number" data-field="end" className="form-control" onChange={this.handleChange} />
  				</div>
        </div>
        <p style={{display: self.state.error_display}}>{this.state.error_message}</p>
        <div className="modal-footer">
          <button type="button" className="btn btn-default" data-dismiss="modal">Cancel</button>
          <button type="submit" className="btn btn-primary" onClick={this.handleSubmit}>Create Clip</button>
        </div>
      </div>
		);
	}
}

// pattern from stack overflow https://stackoverflow.com/questions/5717093/check-if-a-javascript-string-is-a-url
function isURL(str) {
  var pattern = new RegExp('^(https?:\\/\\/)?'+ // protocol
  '((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.?)+[a-z]{2,}|'+ // domain name
  '((\\d{1,3}\\.){3}\\d{1,3}))'+ // OR ip (v4) address
  '(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*'+ // port and path
  '(\\?[;&a-z\\d%_.~+=-]*)?'+ // query string
  '(\\#[-a-z\\d_]*)?$','i'); // fragment locator
  return pattern.test(str);
}
