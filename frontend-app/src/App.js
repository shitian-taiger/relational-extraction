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
function mapInstance(validityArr, instances, validity) {
  let validInstances = [];
  for (let i = 0; i < instances.length; i++) {
    if (validityArr[i] === validity) {
      validInstances.push(instances[i]);
    }
  }
  return validInstances;
}

function instanceAdd(sentence, validInstances, invalidInstances) {
  return fetch("http://127.0.0.1:8000/addinstances", {
    method: 'POST',
    body: JSON.stringify({
      sentence: sentence,
      validInstances: validInstances,
      invalidInstances: invalidInstances
    }),
  })
    .then((response) => response.json());
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
      invalidInstances: []
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
        .concat(mapInstance(validationArr.oie, this.state.oieResults, 1))
        .concat(mapInstance(validationArr.dp, this.state.dpResults, 1))
        .concat(mapInstance(validationArr.nerOie, this.state.nerOieResults, 1));
    let invalidInstances = userInstances
        .concat(mapInstance(validationArr.oie, this.state.oieResults, 0))
        .concat(mapInstance(validationArr.dp, this.state.dpResults, 0))
        .concat(mapInstance(validationArr.nerOie, this.state.nerOieResults, 0));
    this.setState({
      instancesGenerated: true
    });
    this.setState({
      validInstances: validInstances,
      invalidInstances: invalidInstances
    });
  }

  // Reset everything once instances are confirmed
  confirmInstances = () => {
    instanceAdd(this.state.sentence, this.state.validInstances, this.state.invalidInstances)
      .then((res) => console.log("Instances updated"))
      .catch((err) => alert("Error: Instances not uploaded"));
    this.setState({
      sentence: "",
      predictedResults: {},
      oieResults: [],
      nerOieResults: [],
      dpResults: [],
      resultsPresent: false,
      instancesGenerated: false,
      validInstances: [],
    });
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
              validInstances={this.state.validInstances}
              invalidInstances={this.state.invalidInstances}
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
      validInstances: props.validInstances,
      invalidInstances: props.invalidInstances
    };
  }

  componentDidUpdate(prevProps, prevState, snapshot) {
    // Required since setState results in inf loop within componentDidUpdate
    if (!equal(this.props.validInstances, prevProps.validInstances)) {
      this.setState({
        validInstances: this.props.validInstances,
        invalidInstances: this.props.invalidInstances
      });
    }
  }

  validInstanceTable() {
    let tableRows = [];
    for (let i = 0; i < this.state.validInstances.length; i++) {
      let tableCells = [];
      for (let j = 0; j < 3; j++) {
        tableCells.push(<Table.Cell key={j}>{this.state.validInstances[i][j]}</Table.Cell>);
      }
      tableRows.push(<Table.Row key={i}>{tableCells}</Table.Row>);
    }
    return tableRows;
  }
  invalidInstanceTable() {
    let tableRows = [];
    for (let i = 0; i < this.state.invalidInstances.length; i++) {
      let tableCells = [];
      for (let j = 0; j < 3; j++) {
        tableCells.push(<Table.Cell key={j}>{this.state.invalidInstances[i][j]}</Table.Cell>);
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
              <Table.HeaderCell>Valid Instances</Table.HeaderCell>
              <Table.HeaderCell></Table.HeaderCell>
              <Table.HeaderCell></Table.HeaderCell>
            </Table.Row>
          </Table.Header>

          <Table.Body>
            {this.validInstanceTable()}
          </Table.Body>
        </Table>

        <Table>
          <Table.Header>
            <Table.Row>
              <Table.HeaderCell>Invalid Instances</Table.HeaderCell>
              <Table.HeaderCell></Table.HeaderCell>
              <Table.HeaderCell></Table.HeaderCell>
            </Table.Row>
          </Table.Header>

          <Table.Body>
            {this.invalidInstanceTable()}
          </Table.Body>
        </Table>
        <Button onClick={this.handleSubmit}>Save Instances</Button>
      </div>
    );
  }
}
