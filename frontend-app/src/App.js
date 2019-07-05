import React from 'react';
import './App.css';
import Predictor from './Predictor';
import Results from './Results'

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

