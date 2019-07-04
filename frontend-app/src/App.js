import React from 'react';
import './App.css';
import Predictor from './Predictor';
import { Button } from 'semantic-ui-react';
import equal from 'fast-deep-equal';

function App() {

  return (
    <div className="App">
      <Base/>
    </div>
  );
}

export default App;

class Base extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      predictedResults: null,
    };
  }

  render() {
    return (
      <div className="App">
        <Predictor onResultReceived={this.resultReceived}/>
        <Results results={this.state.predictedResults}/>
      </div>
    );
  }

  resultReceived = (result) => {
    this.setState({predictedResults: result});
  }
}

class Results extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      oieResults: [],
      dpResults: [],
      nerOieResults: []
    };
  }

  componentDidUpdate(prevProps, prevState, snapshot) {
    // Required since setState results in inf loop within componentDidUpdate
    if (!equal(this.props.results, prevProps.results))
    {
      this.updatePredictionResults();
    }
  }

  updatePredictionResults() {
    let results = this.props.results;
    this.setState({oieResults: results.oie_prediction});
    this.setState({dpResults: results.dp_prediction});
    this.setState({nerOieResults: results.ner_oie_prediction});
  }


  getResArray(arr) {
      let resLines = [];
    for (let i = 0; i < arr.length; i++) {
        let line = arr[i];
      resLines.push(<ResultLine key={i} text={line}/>);
    }
    return resLines;
  }

  render() {
    let oieResLines = this.getResArray(this.state.oieResults);
    let oieDPLines = this.getResArray(this.state.dpResults);
    let oieNerResLines = this.getResArray(this.state.nerOieResults);

    return (
      <div className="Results">
        <div className="Results-Header"> Predicted Results </div>
        <div className="Results-Subheader">
          OIE Results
          {oieResLines}
        </div>
        <div className="Results-Subheader">
          NER-OIE Results
          {oieNerResLines}
        </div>
        <div className="Results-Subheader">
          DP Results
          {oieDPLines}
        </div>
      </div>
    );
  }
}


class ResultLine extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      arg1: props.text[0],
      rel: props.text[1],
      arg2: props.text[2],
    }
  }

  render() {
    return (
      <div className="ResultLine">
        <Span text={this.state.arg1 + " "}/>
        <Span text={this.state.rel + " "}/>
        <Span text={this.state.arg2 + " "}/>
        <Button>
          Valid Relation
        </Button>
      </div>
    )
  }
}


class Span extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      text: props["text"]
    };
  }

  render() {
    return (
      <span>{this.state.text}</span>
    );
  }
}

