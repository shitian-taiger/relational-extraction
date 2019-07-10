import React from 'react';
import './App.css';
import Predictor from './components/Predictor';
import Results from './components/Results';
import { Button, Table, Container, Transition, Popup, Icon } from 'semantic-ui-react';
import equal from 'fast-deep-equal';
import _ from 'lodash';

// let IP = "http://192.168.86.101:8000";
// let IP = "http://127.0.0.1:8000";
let IP = "http://192.168.86.248:8000";

function App() {

  return (
    <div className="App">
      <Base/>
    </div>
  );
}

export default App;


function instanceAdd(sentence, validInstances, invalidInstances) {
  return fetch(IP + "/addinstances", {
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
      DBINFO: "Remember to clear browser cache if recent downloads of DB are not updating",
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

  componentDidMount(){
    document.title = "Relational Extraction Data Generation";
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

  // Helper for mapping vArr and instances
  getInstances(validationArr, validity) {
    let instances = [];
    for (let idx in this.state.oieResults) {
      if (validationArr.oie[idx] === validity) instances.push(this.state.oieResults[idx]);
    }
    for (let idx in this.state.dpResults) {
      if (validationArr.dp[idx] === validity) instances.push(this.state.dpResults[idx]);
    }
    for (let idx in this.state.nerOieResults) {
      if (validationArr.nerOie[idx] === validity) instances.push(this.state.nerOieResults[idx]);
    }
    // Remove duplicates
    return _.uniqBy(instances, instance => instance[0] + instance[1] + instance[2]);
  }
  // Upon confirmation of instance validity from Results
  validationReceived = (validationArr, userInstances) => {
    let validInstances = userInstances.concat(this.getInstances(validationArr, 1));
    let invalidInstances = this.getInstances(validationArr, 0);
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
      .then((res) => console.log(res))
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

  // Download the store as a Blob
  downloadDb = (event) => {
    fetch(IP + "/db_download", {method: 'GET'})
      .then((response) => {
        const reader = response.body.getReader();
        reader.read().then( ({done, value}) => {
          const blob = new Blob([value], {type: 'text/plain'});
          const url = URL.createObjectURL(blob);
          const dbDownload = document.createElement('a');
          dbDownload.href = url;
          dbDownload.download = 'store.db';
          dbDownload.click(); // Manual trigger
        });
      })
      .catch((err) => alert("Server Error"));
  }

  render() {
    return (
      <div className="App">
        <Button onClick={this.downloadDb}>
          Download DB
        </Button>
        <Popup content={this.state.DBINFO} trigger={<Icon name='info circle'/>} />

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
