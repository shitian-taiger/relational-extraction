import React from 'react';
import './App.css';
import Predictor from './Predictor';
import { Button } from 'semantic-ui-react';


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
      predicted: null,
    };
  }

  render() {
    return (
      <div className="App">
        <Predictor onResultReceived={this.resultReceived}/>
        <Results/>
      </div>
    );
  }

  resultReceived = (result) => {
    this.setState({predicted: result});
    console.log(this.state.predicted)
  }
}

class Results extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      oie_results: [],
      dp_results: [],
      combined_results: []
    };
  }

  render() {
    return (
      <div className="Results">
        <div className="Results-Header"> Predicted Results </div>
        <div className="Results-Subheader"> OIE Results </div>
        <Span text="Word"/>
      </div>
    );
  }
}


class ResultLine extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <div>
        <Button>
          Valid
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

