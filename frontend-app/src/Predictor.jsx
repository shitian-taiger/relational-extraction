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
        <SentenceInput/>
      </div>
    );
  };
}

class SentenceInput extends React.Component {
  constructor(props) {
    super(props);
    this.state = { sentence: "Mary is Harry's friend.",
                   oie_predict_url: "http://127.0.0.1:8000/predict/oie",
                   oie_results: [],
                   dp_predict_url: "http://127.0.0.1:8000/predict/dep_parse",
                   dp_results: [],
                 };

    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleChange(event) {
    this.setState({sentence: event.target.value});
    console.log(this.state.sentence);
  }

  handleSubmit(event) {

    event.preventDefault();
    fetcher(this.state.oie_predict_url, this.state.sentence)
      .then((res) => this.state.oie_results = res);

    fetcher(this.state.dp_predict_url, this.state.sentence)
      .then((res) => this.state.dp_results = res);

    console.log(this.state.oie_results);
    console.log(this.state.dp_results);

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
