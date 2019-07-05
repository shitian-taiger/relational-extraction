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
        {/* Pass onPredictionResult prop to Predictor for callback on retrieval */}
        <Predictor onPredictionResult={this.resultReceived}/>
        {/* Pass onValidated prop to Results for callback on user validation of results */}
        <Results onValidated={this.validationReceived}
                 results={this.state.predictedResults}/>
      </div>
    );
  }

  resultReceived = (predictionResults) => {
    this.setState({predictedResults: predictionResults});
  }

  validationReceived = (validationResult) => {
    console.log(validationResult);
  }
}

