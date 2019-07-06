import React from 'react';
import './App.css';
import Predictor from './components/Predictor';
import Results from './components/Results';

function App() {

  return (
    <div className="App">
      <Base/>
    </div>
  );
}

export default App;

// Helper for mapping vArr and instances
function mapValidInstance(validityArr, instances) {
  let validInstances = []
  for (let i = 0; i < instances.length; i++) {
    if (validityArr[i] === 1) {
      validInstances.push(instances[i])
    }
  }
  return validInstances;
}

class Base extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      sentence: "",
      predictedResults: null,
      oieResults: [],
      nerOieResults: [],
      dpResults: [],
      validInstances: []
    };
  }

  render() {
    return (
      <div className="App">
        {/* Pass onPredictionResult prop to Predictor for callback on retrieval */}
        <Predictor onPredictionResult={this.resultReceived}/>
        {/* Pass onValidated prop to Results for callback on user validation of results */}
        <Results
          sentence={this.state.sentence}
          onValidated={this.validationReceived}
          results={this.state.predictedResults}/>
      </div>
    );
  }

  // Retrieve sentence and predicted results from Predictor
  // predictionResults of format: {dp / oie / ner_oie_prediction: }
  resultReceived = (sentence, predictionResults) => {
    this.setState({
      sentence: sentence,
      predictedResults: predictionResults,
      oieResults: predictionResults.oie_prediction,
      nerOieResults: predictionResults.ner_oie_prediction,
      dpResults: predictionResults.dp_prediction
    });
  }

  validationReceived = (validationArr, userInstances) => {
    let validInstances = userInstances.
        concat(mapValidInstance(validationArr.oie, this.state.oieResults)).
        concat(mapValidInstance(validationArr.dp, this.state.dpResults)).
        concat(mapValidInstance(validationArr.nerOie, this.state.nerOieResults))
    this.setState({
      validInstances: validInstances
    });
  }
}
