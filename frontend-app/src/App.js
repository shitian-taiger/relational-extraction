import React from 'react';
import './App.css';
import Predictor from './components/Predictor';
import Results from './components/Results';
import { Button, Table, Container, Transition } from 'semantic-ui-react';
import equal from 'fast-deep-equal';

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
  let validInstances = [];
  for (let i = 0; i < instances.length; i++) {
    if (validityArr[i] === 1) {
      validInstances.push(instances[i]);
    }
  }
  return validInstances;
}

class Base extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      sentence: "",
      predictedResults: {},
      oieResults: [],
      nerOieResults: [],
      dpResults: [],
      resultsPresent: false,
      instancesGenerated: false,
      validInstances: [],
    };
  }

  // Retrieve sentence and predicted results from Predictor
  // predictionResults of format: {dp / oie / ner_oie_prediction: }
  resultReceived = (sentence, predictionResults) => {
    this.setState({
      resultsPresent: true,
      instancesGenerated: false
    });
    this.setState({
      sentence: sentence,
      predictedResults: predictionResults,
      oieResults: predictionResults.oie_prediction,
      nerOieResults: predictionResults.ner_oie_prediction,
      dpResults: predictionResults.dp_prediction
    });
  }

  validationReceived = (validationArr, userInstances) => {
    let validInstances = userInstances
        .concat(mapValidInstance(validationArr.oie, this.state.oieResults))
        .concat(mapValidInstance(validationArr.dp, this.state.dpResults))
        .concat(mapValidInstance(validationArr.nerOie, this.state.nerOieResults));
    this.setState({
      instancesGenerated: true
    });
    this.setState({
      validInstances: validInstances,
    });
  }

  // Reset everything once instances are confirmed
  confirmInstances = () => {
    this.setState({
      sentence: "",
      predictedResults: {},
      oieResults: [],
      nerOieResults: [],
      dpResults: [],
      resultsPresent: false,
      instancesGenerated: false,
      validInstances: [],
    })
  }

  render() {
    return (
      <div className="App">
        {/* Pass onPredictionResult prop to Predictor for callback on retrieval */}
        <Predictor onPredictionResult={this.resultReceived}/>

        {/* Pass onValidated prop to Results for callback on user validation of results */}
        <Transition visible={this.state.resultsPresent && !this.state.instancesGenerated}
                    animation="scale"
                    duration={200}>
          <Container fluid>
            <Results
              sentence={this.state.sentence}
              onValidated={this.validationReceived}
              results={this.state.predictedResults}/>
          </Container>
        </Transition>

        <Transition visible={this.state.instancesGenerated}
                    animation="scale"
                    duration={200}>
          <Container fluid>
            <Confirmation
              instances={this.state.validInstances}
              onConfirmation={this.confirmInstances}
              />
          </Container>
        </Transition>

      </div>
    );
  }
}

class Confirmation extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      instances: props.instances
    };
  }

  componentDidUpdate(prevProps, prevState, snapshot) {
    // Required since setState results in inf loop within componentDidUpdate
    if (!equal(this.props.instances, prevProps.instances)) {
      this.setState({
        instances: this.props.instances
      });
    }
  }

  instanceTable() {
    let tableRows = []
    for (let i = 0; i < this.state.instances.length; i++) {
      let tableCells = [];
      for (let j = 0; j < 3; j++) {
        tableCells.push(<Table.Cell key={j}>{this.state.instances[i][j]}</Table.Cell>);
      }
      tableRows.push(<Table.Row key={i}>{tableCells}</Table.Row>);
    }
    return tableRows;
  }

  handleSubmit = (event) => {
    this.props.onConfirmation();
  }

  render() {
    return (
      <div className="Confirmation">
        <Table>
          <Table.Header>
            <Table.Row>
              <Table.HeaderCell>Instances</Table.HeaderCell>
              <Table.HeaderCell></Table.HeaderCell>
              <Table.HeaderCell></Table.HeaderCell>
            </Table.Row>
          </Table.Header>

          <Table.Body>
            {this.instanceTable()}
          </Table.Body>
        </Table>
        <Button onClick={this.handleSubmit}>Confirm Instances</Button>
      </div>
    );
  }
}
