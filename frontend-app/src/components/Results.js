import React from 'react';
import { Input, Button, Table } from 'semantic-ui-react';
import { ResultLine } from './ResultLine';
import equal from 'fast-deep-equal';

class Results extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      oieResults: [],
      dpResults: [],
      nerOieResults: [],
      // Bitwise validity for user input
      validity: {oie: [], dp: [], nerOie: []},
      userInstances: [],
    };
  }

  // Updating of Prediction Results: Set result array and instantiate validity index
  componentDidUpdate(prevProps, prevState, snapshot) {
    // Required since setState results in inf loop within componentDidUpdate
    if (!equal(this.props.results, prevProps.results)) {
      this.updatePredictionResults();
    }
  }
  updatePredictionResults() {
    let results = this.props.results;
    this.setState({
      oieResults: results.oie_prediction,
      dpResults: results.dp_prediction,
      nerOieResults: results.ner_oie_prediction,
      validity: {
        oie: results.oie_prediction.map(x => 0),
        dp: results.dp_prediction.map(x => 0),
        nerOie: results.ner_oie_prediction.map(x => 0)
      }
    });
  }

  // Process each prediction type (Array of tuples) into ResultLine(TableRow)
  getResArray(predictionType, arr) {
    let resLines = [];
    for (let i = 0; i < arr.length; i++) {
      let line = arr[i];
      resLines.push(<ResultLine
                    pType={predictionType}
                    key={i} // Each child in list requires unique key, not accessible in props
                    index={i}
                    text={line}
                    validateInstance={this.instanceValidation}/>);
    }
    return resLines;
  }

  /** To be called by ResultLine child class, result should contain:
      pType : Prediction Type
      index : Index of instance within prediction type
      validity : Whether instance is valid
     */
  instanceValidation = (result) => {
    if (result.pType === "OIE") {
      this.state.validity.oie[result.index] = (result.validity) ? 1 : 0;
    } else if (result.pType === "DP") {
      this.state.validity.dp[result.index] = (result.validity) ? 1 : 0;
    } else if (result.pType === "NER-OIE") {
      this.state.validity.nerOie[result.index] = (result.validity) ? 1 : 0;
    } else {
      console.log("Setting validity of invalid prediction type");
      throw("Invalid");
    }
  }

  // Pass validations to parent Base
  confirmValidations() {
    if (this.state.oieResults.length === 0 &&
        this.state.nerOieResults.length === 0 &&
        this.state.dpResults.length === 0) {
      alert("Please process a valid sentence");
      }
    this.props.onValidated(this.state.validity);
  }

  // InstanceCreator Helper
  addInstance = (instance) => {
    let newInstances = this.state.userInstances.concat([[instance.arg1Input, instance.relInput, instance.arg2Input]]);
    this.setState({
      userInstances: newInstances
    });
  }

  render() {
    // TODO Don't compute these calculations on every render, move to results retrieval
    let oieResLines = this.getResArray("OIE", this.state.oieResults);
    let dPLines = this.getResArray("DP", this.state.dpResults);
    let oieNerResLines = this.getResArray("NER-OIE", this.state.nerOieResults);
    let userLines = this.getResArray("USER", this.state.userInstances);
    return (
      <div className="Results">
        <div className="Results-Header"> Predicted Results </div>
        <div className="Results-Subheader"> OIE Results </div>
        <Table className="Results-Table">
          <Table.Body>{oieResLines}</Table.Body>
        </Table>

        <div className="Results-Subheader"> NER-OIE Results </div>
        <Table className="Results-Table">
          <Table.Body>{oieNerResLines}</Table.Body>
        </Table>

        <div className="Results-Subheader"> DP Results </div>
        <Table className="Results-Table">
          <Table.Body>{dPLines}</Table.Body>
        </Table>

        <div className="Results-Subheader"> Custom Instances </div>
        <Table className="Results-Table">
          <Table.Body>{userLines}</Table.Body>
        </Table>

        <InstanceCreator instanceCreate={this.addInstance}/>

        <Button onClick={() => this.confirmValidations()}>
          Confirm Validations
        </Button>
      </div>

    );
  }
}

class InstanceCreator extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      arg1Input: "",
      relInput: "",
      arg2Input: "",
    };
    this.handleArg1Change = this.handleArg1Change.bind(this);
    this.handleRelChange = this.handleRelChange.bind(this);
    this.handleArg2Change = this.handleArg2Change.bind(this);
  }

  handleArg1Change(event) {
    this.setState({arg1Input: event.target.value});
  }
  handleRelChange(event) {
    this.setState({relInput: event.target.value});
  }
  handleArg2Change(event) {
    this.setState({arg2Input: event.target.value});
  }

  addInstance() {
    this.props.instanceCreate(this.state);
    this.setState({
      arg1Input: "",
      relInput: "",
      arg2Input: "",
    });
  }

  render() {
    return (
        <div>
          <Input className="Results-Input"
                 placeholder="Entity One"
                 value={this.state.arg1Input}
                 onChange={this.handleArg1Change} />
          <Input className="Results-Input"
                 placeholder="Relation"
                 value={this.state.relInput}
                 onChange={this.handleRelChange} />
          <Input className="Results-Input"
                 placeholder="Entity Two"
                 value={this.state.arg2Input}
                 onChange={this.handleArg2Change} />
          <Button onClick={() => this.addInstance()}>
            Add Relation
          </Button>
        </div>
    );
  }
}

export default Results;
