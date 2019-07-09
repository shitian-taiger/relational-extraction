import React from 'react';
import { Message, Button, Input } from 'semantic-ui-react';


function fetcher(url, sentenceToPredict) {
  return fetch(url, {
    method: 'POST',
    body: JSON.stringify({
      sentence: sentenceToPredict,
    }),
  })
    .then((response) => response.json());
}

class Predictor extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      sentence: ""
    };
  }

  render() {
    return (
      <div className="Predictor">
        <div className="Predictor-Header"> Open Relational Extraction </div>
        <SentenceInput onResultReceived={this.resultReceived}/>
        <Message style={{marginLeft: "30px", marginRight: "30px"}}>
          <Message.Header>Sentence</Message.Header>
          <p>{this.state.sentence}</p>
        </Message>
      </div>
    );
  };

  resultReceived = (sentence, result) => {
    this.setState({
      sentence: sentence
    });
    this.props.onPredictionResult(sentence, result);
  }
}

class SentenceInput extends React.Component {
  constructor(props) {
    super(props);
    this.state = { sentence: "Lexa Luthoror, an actress and singer in New York and around the world, died on saturday at St. Vincent's hospital in Manhattan.",
                   oie_predict_url: "http://127.0.0.1:8000/predict/all",
                   oie_results: [],
                 };

    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
    this.handleKeyPress = this.handleKeyPress.bind(this);
  }

  handleChange(event) {
    this.setState({sentence: event.target.value});
  }

  // Allow `Enter` keypress to simulate button clicking
  handleKeyPress(target) {
    if(target.charCode === 13) { // `Enter` keycode
      fetcher(this.state.oie_predict_url, this.state.sentence)
        .then((res) => this.props.onResultReceived(this.state.sentence, res))
        .catch((err) => alert("Server Error"));
    }
  }
  handleSubmit(event) {
    event.preventDefault();
    fetcher(this.state.oie_predict_url, this.state.sentence)
      .then((res) => this.props.onResultReceived(this.state.sentence, res))
      .catch((err) => alert("Server not up"));
  }

  render() {
    return (
      <div className="SentenceInput">
        <span className="SentenceInput-Label">
          Sentence Input:
        </span>
        <Input className="SentenceInput-Text"
               focus
               onKeyPress={this.handleKeyPress}
               placeholder="Enter a sentence"
               value={this.state.sentence}
               onChange={this.handleChange} />
        <Button style={{margin: "10px"}} onClick={this.handleSubmit} >
          Predict
        </Button>
      </div>
    );
  }
}


export default Predictor;
