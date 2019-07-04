import React from 'react';
import { Button, Input } from 'semantic-ui-react';


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
  render() {
    return (
      <div className="Predictor">
        <div className="Predictor-Header"> Relational Extraction </div>
        <SentenceInput onResultReceived={this.resultReceived}/>
      </div>
    );
  };

  resultReceived = (result) => {
    this.props.onResultReceived(result);
  }
}

class SentenceInput extends React.Component {
  constructor(props) {
    super(props);
    this.state = { sentence: "Lex Luthor, who was an actress and singer in New York and around the world, died on saturday at St. Vincent's hospital in Manhattan.",
                   oie_predict_url: "http://127.0.0.1:8000/predict/all",
                   oie_results: [],
                 };

    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleChange(event) {
    this.setState({sentence: event.target.value});
  }

  handleSubmit(event) {

    event.preventDefault();
    fetcher(this.state.oie_predict_url, this.state.sentence)
      .then((res) => this.props.onResultReceived(res));

  }

  render() {
    return (
      <div className="SentenceInput">
        <span className="SentenceInput-Label">
          Sentence Input:
        </span>
        <Input className="SentenceInput-Text"
          placeholder="Enter a sentence"
               focus
               value={this.state.sentence}
               onChange={this.handleChange} />
        <Button onClick={this.handleSubmit} >
          Predict
        </Button>
      </div>
    );
  }
}


export default Predictor;
