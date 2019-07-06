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
      sentence: props.sentence
    };
  }

  // Updating of Prediction Results: Set result array and instantiate validity index
  // Also updates sentence
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
      },
      sentence: this.props.sentence
    });
  }

  // Process each prediction type (Array of tuples) into ResultLine(TableRow)
  getResArray(predictionType, arr) {
    let resLines = [];
    let validity = (predictionType === "USER") ? true : false;
    for (let i = 0; i < arr.length; i++) {
      let line = arr[i];
      resLines.push(<ResultLine
                    pType={predictionType}
                    key={i} // Each child in list requires unique key, not accessible in props
                    index={i}
                    text={line}
                    validity={validity}
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
        <div className="Results-Subheader"> OIE Results </div>
        <Table selectable className="Results-Table">
          <Table.Body>{oieResLines}</Table.Body>
        </Table>

        <div className="Results-Subheader"> NER-OIE Results </div>
        <Table selectable className="Results-Table">
          <Table.Body>{oieNerResLines}</Table.Body>
        </Table>

        <div className="Results-Subheader"> DP Results </div>
        <Table selectable className="Results-Table">
          <Table.Body>{dPLines}</Table.Body>
        </Table>

        <div className="Results-Subheader"> Custom Instances </div>
        <Table selectable className="Results-Table">
          <Table.Body>{userLines}</Table.Body>
        </Table>

        <InstanceCreator
          sentence={this.state.sentence}
          instanceCreate={this.addInstance}/>

        <Button onClick={() => this.confirmValidations()}>
          Confirm Instances
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
      sentence: props.sentence
    };
    this.handleArg1Change = this.handleArg1Change.bind(this);
    this.handleRelChange = this.handleRelChange.bind(this);
    this.handleArg2Change = this.handleArg2Change.bind(this);
  }

  componentDidUpdate(prevProps, prevState, snapshot) {
    // Required since setState results in inf loop within componentDidUpdate
    if (!equal(this.props.sentence, prevProps.sentence)) {
      this.setState({
        sentence: this.props.sentence
      });
    }
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
    console.log(this.state.sentence)
    if (this.state.sentence === "") {
      this.setState({errorMessage: "Predict on valid sentence first"});
    } else if (!this.state.arg1Input || !this.state.relInput || !this.state.arg2Input) {
      this.setState({errorMessage: "Ensure all fields are filled in"});
    } else if (!this.state.sentence.includes(this.state.arg1Input) ||
               !this.state.sentence.includes(this.state.relInput) ||
               !this.state.sentence.includes(this.state.arg2Input)) {
      this.setState({errorMessage: "Ensure arguments are contained within sentence"});
    } else {
      this.props.instanceCreate(this.state);
      this.setState({
        arg1Input: "",
        relInput: "",
        arg2Input: "",
      });
    }
  }

  render() {
    return (
        <div>
          <Input className="InstanceCreator-Input"
                 placeholder="Entity One"
                 value={this.state.arg1Input}
                 onChange={this.handleArg1Change} />
          <Input className="InstanceCreator-Input"
                 placeholder="Relation"
                 value={this.state.relInput}
                 onChange={this.handleRelChange} />
          <Input className="InstanceCreator-Input"
                 placeholder="Entity Two"
                 value={this.state.arg2Input}
                 onChange={this.handleArg2Change} />
          <Button onClick={() => this.addInstance()}>
            Add Relation
          </Button>
          <div>{this.state.errorMessage}</div>
        </div>
    );
  }
}

export default Results;
